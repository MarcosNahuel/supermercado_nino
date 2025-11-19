"""Baseline ticket amount and margin predictor."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Iterable, Optional, Tuple

import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, r2_score

try:  # pragma: no cover - guard for optional dependency during import time
    from xgboost import XGBRegressor
except ImportError:  # Fallback keeps notebook exploration usable if xgboost is absent
    from sklearn.ensemble import GradientBoostingRegressor as XGBRegressor


CategoricalColumns = Iterable[str]


@dataclass
class TicketPredictor:
    """
    Gradient boosted baseline that models ticket-level revenue and margin.

    The model uses behavioural metadata (cluster, calendar context, mix)
    to approximate the expected value of a ticket prior to any commercial
    intervention. This baseline establishes the counterfactual for the
    remaining strategy simulators.
    """

    categorical_columns: Tuple[str, ...] = (
        "cluster",
        "dia_semana",
        "tipo_dia",
        "medio_pago",
    )
    numeric_columns: Tuple[str, ...] = (
        "hora",
        "num_items",
        "num_skus",
    )
    monto_model: Optional[XGBRegressor] = field(default=None, init=False)
    margen_model: Optional[XGBRegressor] = field(default=None, init=False)
    feature_columns_: Optional[pd.Index] = field(default=None, init=False)

    def __post_init__(self) -> None:
        uses_xgboost = "xgboost" in XGBRegressor.__module__
        if uses_xgboost:
            hyperparams = dict(
                n_estimators=200,
                max_depth=6,
                learning_rate=0.1,
                subsample=0.8,
                colsample_bytree=0.8,
                random_state=42,
            )
        else:
            hyperparams = dict(
                n_estimators=200,
                max_depth=6,
                learning_rate=0.1,
                random_state=42,
            )
        self.monto_model = XGBRegressor(**hyperparams)
        self.margen_model = XGBRegressor(**hyperparams)

    def _augment_ticket_frame(self, tickets: pd.DataFrame) -> pd.DataFrame:
        """Derive the minimal feature set expected by the model."""
        df = tickets.copy()

        if "cluster" not in df.columns:
            if "cluster_ticket" in df.columns:
                df["cluster"] = df["cluster_ticket"]
            else:
                df["cluster"] = 0

        if "dia_semana" not in df.columns:
            if "fecha" in df.columns:
                fechas = pd.to_datetime(df["fecha"], errors="coerce")
                df["dia_semana"] = fechas.dt.day_name().fillna("Unknown")
                df["hora"] = fechas.dt.hour.fillna(0).astype(int)
            else:
                df["dia_semana"] = "Unknown"
                df["hora"] = 0
        elif "hora" not in df.columns:
            df["hora"] = 0

        if "medio_pago" not in df.columns:
            df["medio_pago"] = df.get("tipo_medio_pago", "Desconocido")

        df["num_items"] = df.get("unidades_totales", df.get("num_items", 0))
        df["num_skus"] = df.get("productos_unicos", df.get("num_skus", 0))
        df["tipo_dia"] = df.get("tipo_dia", "Desconocido")

        return df

    def _validate_columns(self, tickets: pd.DataFrame) -> None:
        expected = set(self.categorical_columns + self.numeric_columns)
        missing = expected.difference(tickets.columns)
        if missing:
            raise ValueError(f"Missing required ticket features: {sorted(missing)}")

    def prepare_features(self, tickets: pd.DataFrame) -> pd.DataFrame:
        """One-hot encode categorical fields and align to stored schema."""
        tickets = self._augment_ticket_frame(tickets)
        self._validate_columns(tickets)
        base = tickets[list(self.numeric_columns)].copy()
        categorical = pd.get_dummies(
            tickets[list(self.categorical_columns)].astype("category"),
            drop_first=False,
            dtype=np.uint8,
        )
        design_matrix = pd.concat([base, categorical], axis=1)

        if self.feature_columns_ is None:
            self.feature_columns_ = design_matrix.columns
        else:
            design_matrix = design_matrix.reindex(
                columns=self.feature_columns_, fill_value=0
            )

        return design_matrix

    def train(self, tickets: pd.DataFrame) -> Dict[str, float]:
        """
        Fit the amount and margin models and return in-sample diagnostics.
        """
        if tickets.empty:
            raise ValueError("TicketPredictor requires a non-empty dataset.")

        features = self.prepare_features(tickets)
        monto_series = tickets.get("monto_total", tickets.get("ventas_totales"))
        if monto_series is None:
            raise ValueError("Tickets dataset must include 'monto_total' or 'ventas_totales'.")
        y_monto = monto_series.astype(float)

        margen_series = tickets.get("margen_total")
        if margen_series is None:
            raise ValueError("Tickets dataset must include 'margen_total'.")
        y_margen = margen_series.astype(float)

        self.monto_model.fit(features, y_monto)
        self.margen_model.fit(features, y_margen)

        predictions_monto = self.monto_model.predict(features)
        predictions_margen = self.margen_model.predict(features)

        return {
            "r2_monto": float(r2_score(y_monto, predictions_monto)),
            "r2_margen": float(r2_score(y_margen, predictions_margen)),
            "mae_monto": float(mean_absolute_error(y_monto, predictions_monto)),
            "mae_margen": float(mean_absolute_error(y_margen, predictions_margen)),
        }

    def predict(self, tickets: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
        """
        Predict ticket amount and margin for the provided feature frame.
        """
        if self.feature_columns_ is None:
            raise RuntimeError("Model not trained yet. Call 'train' first.")

        features = self.prepare_features(tickets)
        monto = self.monto_model.predict(features)
        margen = self.margen_model.predict(features)
        return np.asarray(monto), np.asarray(margen)
