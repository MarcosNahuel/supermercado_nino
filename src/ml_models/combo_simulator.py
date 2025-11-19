"""Combo uplift simulator for bundled product promotions."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable, Optional

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LogisticRegression


@dataclass
class ComboSimulator:
    """
    Estimate the ROI of focussed combo promotions (e.g. Fernet + Coca-Cola).

    The workflow combines historical uplift measurement with a propensity
    model that approximates how frequently the combo should appear under
    comparable conditions. The simulator uses simple heuristics so it can
    operate quickly on aggregated ticket data.
    """

    combo_products: Iterable[str] = ("FERNET", "COCA")
    probability_model: LogisticRegression = field(
        default_factory=lambda: LogisticRegression(max_iter=1000)
    )
    uplift_model: RandomForestRegressor = field(
        default_factory=lambda: RandomForestRegressor(
            n_estimators=200, max_depth=6, random_state=42, n_jobs=-1
        )
    )
    feature_columns_: Optional[pd.Index] = field(default=None, init=False)

    def _augment_ticket_frame(self, tickets: pd.DataFrame) -> pd.DataFrame:
        df = tickets.copy()
        if "cluster" not in df.columns:
            if "cluster_ticket" in df.columns:
                df["cluster"] = df["cluster_ticket"]
            else:
                df["cluster"] = 0

        if "dia_semana" not in df.columns:
            fechas = pd.to_datetime(df.get("fecha"), errors="coerce")
            df["dia_semana"] = fechas.dt.day_name().fillna("Unknown")
        if "hora" not in df.columns:
            fechas = pd.to_datetime(df.get("fecha"), errors="coerce")
            df["hora"] = fechas.dt.hour.fillna(0).astype(int)

        if "tipo_dia" not in df.columns:
            df["tipo_dia"] = df.get("tipo_dia", "Desconocido")
        if "medio_pago" not in df.columns:
            df["medio_pago"] = df.get("tipo_medio_pago", "Desconocido")

        return df

    def identify_combo_tickets(self, detalle: pd.DataFrame) -> pd.Series:
        """Return ticket ids that purchased every product in the combo."""
        tickets_sets = []
        for product in self.combo_products:
            mask = detalle["descripcion"].str.contains(product, case=False, na=False)
            tickets_sets.append(set(detalle.loc[mask, "ticket_id"].unique()))

        if not tickets_sets:
            return pd.Index([])

        combo_ticket_ids = set.intersection(*tickets_sets)
        return pd.Index(sorted(combo_ticket_ids))

    def _prepare_ticket_features(self, tickets: pd.DataFrame) -> pd.DataFrame:
        tickets = self._augment_ticket_frame(tickets)
        cols = ["cluster", "dia_semana", "hora", "tipo_dia", "medio_pago"]
        missing = set(cols).difference(tickets.columns)
        if missing:
            raise ValueError(f"Missing columns for combo propensity model: {sorted(missing)}")

        base = tickets[["hora"]].astype(float)
        categorical = pd.get_dummies(
            tickets[["cluster", "dia_semana", "tipo_dia", "medio_pago"]].astype("category"),
            drop_first=False,
        )
        design_matrix = pd.concat([base, categorical], axis=1)
        if self.feature_columns_ is None:
            self.feature_columns_ = design_matrix.columns
        else:
            design_matrix = design_matrix.reindex(columns=self.feature_columns_, fill_value=0)
        return design_matrix

    def fit_probability_model(self, tickets: pd.DataFrame, detalle: pd.DataFrame) -> None:
        """Train a lightweight model predicting combo adoption probability."""
        tickets = self._augment_ticket_frame(tickets)
        combo_ids = self.identify_combo_tickets(detalle)
        if combo_ids.empty:
            return

        tickets = tickets.copy()
        tickets["combo_flag"] = tickets["ticket_id"].isin(combo_ids).astype(int)

        features = self._prepare_ticket_features(tickets)
        target = tickets["combo_flag"]

        # Down-sample to keep fitting time reasonable
        sample_size = min(75000, len(tickets))
        sampled = tickets.sample(sample_size, random_state=42)
        features_sampled = features.loc[sampled.index]
        target_sampled = target.loc[sampled.index]

        self.probability_model.fit(features_sampled, target_sampled)

        # Uplift model: learn delta in monto_total conditional on combo
        uplift_features = features_sampled.assign(combo_flag=target_sampled.values)
        monto_series = sampled.get("monto_total", sampled.get("ventas_totales"))
        if monto_series is None:
            raise ValueError("El dataset de tickets debe incluir 'monto_total' o 'ventas_totales'.")
        uplift_target = monto_series.astype(float)
        self.uplift_model.fit(uplift_features, uplift_target)

    def calculate_historical_uplift(
        self,
        tickets: pd.DataFrame,
        detalle: pd.DataFrame,
        *,
        min_records: int = 10,
    ) -> pd.DataFrame:
        """
        Compute realised uplift between combo vs. control tickets grouped by
        cluster and weekday, using heuristic matching.
        """
        tickets_aug = self._augment_ticket_frame(tickets)
        combo_ticket_ids = self.identify_combo_tickets(detalle)
        if combo_ticket_ids.empty:
            return pd.DataFrame(
                columns=[
                    "cluster",
                    "dia",
                    "uplift_monto",
                    "uplift_margen",
                    "n_combo",
                    "n_control",
                ]
            )

        tickets_combo = tickets_aug[tickets_aug["ticket_id"].isin(combo_ticket_ids)].copy()
        tickets_no_combo = tickets_aug[~tickets_aug["ticket_id"].isin(combo_ticket_ids)].copy()

        matched_rows = []
        weekday_values = tickets_aug["dia_semana"].unique()
        for cluster in sorted(tickets_aug["cluster"].unique()):
            for dia in weekday_values:
                combo_subset = tickets_combo[
                    (tickets_combo["cluster"] == cluster) & (tickets_combo["dia_semana"] == dia)
                ]
                if combo_subset.empty:
                    continue

                control_subset = tickets_no_combo[
                    (tickets_no_combo["cluster"] == cluster) & (tickets_no_combo["dia_semana"] == dia)
                ]
                if control_subset.empty:
                    continue

                sample_n = min(len(combo_subset) * 3, len(control_subset), 10000)
                control_sample = control_subset.sample(sample_n, random_state=42)

                if len(combo_subset) < min_records or len(control_sample) < min_records:
                    continue

                combo_monto = combo_subset.get("monto_total", combo_subset.get("ventas_totales"))
                control_monto = control_sample.get("monto_total", control_sample.get("ventas_totales"))
                combo_margen = combo_subset.get("margen_total")
                control_margen = control_sample.get("margen_total")

                if combo_monto is None or control_monto is None or combo_margen is None or control_margen is None:
                    continue

                uplift_monto = combo_monto.mean() - control_monto.mean()
                uplift_margen = combo_margen.mean() - control_margen.mean()

                matched_rows.append(
                    {
                        "cluster": cluster,
                        "dia": dia,
                        "uplift_monto": uplift_monto,
                        "uplift_margen": uplift_margen,
                        "n_combo": len(combo_subset),
                        "n_control": len(control_sample),
                    }
                )

        return pd.DataFrame(matched_rows)

    def simulate_roi(
        self,
        tickets: pd.DataFrame,
        detalle: pd.DataFrame,
        *,
        adoption_rate: float = 0.15,
        promo_cost: float = 150_000.0,
    ) -> dict:
        """Project ROI figures for the combo strategy."""
        if tickets.empty or detalle.empty:
            raise ValueError("Tickets and detalle datasets are required.")

        tickets_aug = self._augment_ticket_frame(tickets)

        self.fit_probability_model(tickets_aug, detalle)
        uplifts = self.calculate_historical_uplift(tickets_aug, detalle)
        if uplifts.empty:
            return {
                "strategy": "Estrategia #1: Combos Focalizados (Fernet+Coca)",
                "current_adoption_rate": 0.0,
                "target_adoption_rate": adoption_rate,
                "avg_uplift_monto_per_ticket": 0.0,
                "avg_uplift_margen_per_ticket": 0.0,
                "incremental_tickets_monthly": 0.0,
                "incremental_revenue_monthly": 0.0,
                "incremental_margin_monthly": 0.0,
                "investment": promo_cost,
                "roi_percentage": 0.0,
                "payback_months": float("inf"),
                "confidence_score": 0.0,
                "uplift_distribution": uplifts,
            }

        avg_uplift_monto = float(uplifts["uplift_monto"].mean())
        avg_uplift_margen = float(uplifts["uplift_margen"].mean())

        current_adoption = len(self.identify_combo_tickets(detalle)) / max(len(tickets_aug), 1)
        incremental_adoption = max(adoption_rate - current_adoption, 0)

        monthly_tickets = len(tickets_aug) / 12.0
        incremental_tickets = monthly_tickets * incremental_adoption

        incremental_revenue_monthly = incremental_tickets * avg_uplift_monto
        incremental_margin_monthly = incremental_tickets * avg_uplift_margen

        roi_percentage = (
            (incremental_margin_monthly * 12) / promo_cost * 100 if promo_cost > 0 else float("inf")
        )
        payback_months = (
            promo_cost / incremental_margin_monthly if incremental_margin_monthly > 0 else float("inf")
        )

        confidence_score = uplifts["n_combo"].sum() / max(len(tickets_aug), 1)

        return {
            "strategy": "Estrategia #1: Combos Focalizados (Fernet+Coca)",
            "current_adoption_rate": current_adoption,
            "target_adoption_rate": adoption_rate,
            "avg_uplift_monto_per_ticket": avg_uplift_monto,
            "avg_uplift_margen_per_ticket": avg_uplift_margen,
            "incremental_tickets_monthly": incremental_tickets,
            "incremental_revenue_monthly": incremental_revenue_monthly,
            "incremental_margin_monthly": incremental_margin_monthly,
            "investment": promo_cost,
            "roi_percentage": roi_percentage,
            "payback_months": payback_months,
            "confidence_score": confidence_score,
            "uplift_distribution": uplifts,
        }
