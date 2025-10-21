"""Private label impact estimator."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Iterable

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor


@dataclass
class MarcaPropiaEstimator:
    """
    Estimate the incremental margin of introducing private-label products
    across top Pareto categories.
    """

    elasticity_benchmarks: Dict[str, float] = field(
        default_factory=lambda: {
            "BEBIDAS": -1.8,
            "ALMACEN": -1.2,
            "CARNICERIA": -0.8,
            "LACTEOS": -1.0,
            "LIMPIEZA": -1.5,
        }
    )
    elasticity_model: RandomForestRegressor = field(
        default_factory=lambda: RandomForestRegressor(
            n_estimators=200, max_depth=None, random_state=42, n_jobs=-1
        )
    )
    substitution_model: RandomForestClassifier = field(
        default_factory=lambda: RandomForestClassifier(
            n_estimators=200, max_depth=None, random_state=42, n_jobs=-1
        )
    )

    def estimate_price_elasticity(self, categoria: str) -> float:
        """Provide a heuristic elasticity value by category."""
        categoria = (categoria or "").upper()
        return self.elasticity_benchmarks.get(categoria, -1.3)

    def simulate_marca_propia(
        self,
        pareto_cat: pd.DataFrame,
        detalle: pd.DataFrame,
        *,
        conversion_rate: float = 0.25,
        margin_gain_pp: float = 6.0,
        price_reduction_pct: float = 0.08,
    ) -> dict:
        """
        Simulate the introduction of a private-label alternative for
        top Pareto categories (clasificación 'A').
        """
        pareto_df = pareto_cat.copy()
        if "clasificacion_abc" not in pareto_df.columns:
            if "segmento_pareto" in pareto_df.columns:
                pareto_df["clasificacion_abc"] = pareto_df["segmento_pareto"]
            else:
                pareto_df["clasificacion_abc"] = "C"

        if "ventas" not in pareto_df.columns:
            ventas_map = (
                detalle.groupby("categoria")["importe_total"].sum()
                if "importe_total" in detalle.columns
                else pd.Series(dtype=float)
            )
            pareto_df["ventas"] = pareto_df["categoria"].map(ventas_map).fillna(0.0)

        if "margen_pct" not in pareto_df.columns:
            if "rentabilidad_pct" in detalle.columns:
                margen_map = detalle.groupby("categoria")["rentabilidad_pct"].mean() / 100.0
                pareto_df["margen_pct"] = pareto_df["categoria"].map(margen_map).fillna(0.30)
            else:
                pareto_df["margen_pct"] = 0.30

        required_columns = {"categoria", "clasificacion_abc", "ventas", "margen_pct"}
        missing = required_columns.difference(pareto_df.columns)
        if missing:
            raise ValueError(f"Pareto dataset missing columns: {sorted(missing)}")

        cat_a = pareto_df[pareto_df["clasificacion_abc"].str.upper() == "A"].copy()
        if cat_a.empty:
            return {
                "strategy": "Estrategia #2: Marca Propia en Categorías A",
                "target_categories": [],
                "total_ventas_convertibles": 0.0,
                "avg_elasticity": 0.0,
                "avg_volume_lift": 0.0,
                "incremental_margin_annual": 0.0,
                "incremental_margin_monthly": 0.0,
                "investment": 500_000.0,
                "roi_percentage": 0.0,
                "payback_months": float("inf"),
                "detailed_results": pd.DataFrame(),
            }

        results = []
        for _, cat in cat_a.iterrows():
            categoria = cat["categoria"]
            ventas_anuales = float(cat["ventas"])
            margen_actual_pct = float(cat["margen_pct"])

            elasticity = self.estimate_price_elasticity(categoria)
            volume_lift = elasticity * (-price_reduction_pct)
            ventas_convertibles = ventas_anuales * conversion_rate
            ventas_ajustadas = ventas_convertibles * (1 + volume_lift) * (1 - price_reduction_pct)
            margen_incremental = ventas_ajustadas * (margin_gain_pp / 100)

            results.append(
                {
                    "categoria": categoria,
                    "ventas_anuales": ventas_anuales,
                    "ventas_convertibles": ventas_convertibles,
                    "elasticity": elasticity,
                    "volume_lift": volume_lift,
                    "ventas_ajustadas": ventas_ajustadas,
                    "margen_incremental_anual": margen_incremental,
                }
            )

        df_results = pd.DataFrame(results)
        total_margen_incremental = float(df_results["margen_incremental_anual"].sum())
        investment = 500_000.0

        roi_percentage = (total_margen_incremental / investment) * 100 if investment > 0 else float("inf")
        payback_months = (
            investment / (total_margen_incremental / 12) if total_margen_incremental > 0 else float("inf")
        )

        return {
            "strategy": "Estrategia #2: Marca Propia en Categorías A",
            "target_categories": df_results["categoria"].tolist(),
            "total_ventas_convertibles": float(df_results["ventas_convertibles"].sum()),
            "avg_elasticity": float(df_results["elasticity"].mean()),
            "avg_volume_lift": float(df_results["volume_lift"].mean()),
            "incremental_margin_annual": total_margen_incremental,
            "incremental_margin_monthly": total_margen_incremental / 12,
            "investment": investment,
            "roi_percentage": roi_percentage,
            "payback_months": payback_months,
            "detailed_results": df_results,
        }
