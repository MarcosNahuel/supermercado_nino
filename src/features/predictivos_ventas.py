"""Weekly sales forecasting using classical ARIMA models."""

from __future__ import annotations

import itertools
import warnings
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
from statsmodels.tsa.statespace.sarimax import SARIMAX

from src.utils.load_data import ensure_directory


@dataclass
class ForecastResult:
    categoria: str
    history: pd.DataFrame
    forecast: pd.DataFrame
    order: Tuple[int, int, int]
    aic: float


def _parse_semana(ventas: pd.DataFrame) -> pd.DataFrame:
    ventas = ventas.copy()
    ventas["semana_inicio"] = pd.to_datetime(
        ventas["semana_iso"] + "-1", format="%G-W%V-%u"
    )
    ventas = ventas.sort_values("semana_inicio")
    return ventas


def _candidate_orders() -> List[Tuple[int, int, int]]:
    return list(itertools.product([0, 1, 2], [0, 1], [0, 1, 2]))


def _fit_best_model(series: pd.Series) -> Tuple[SARIMAX, Tuple[int, int, int], float]:
    best_model = None
    best_aic = np.inf
    best_order = (1, 1, 1)
    for order in _candidate_orders():
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                model = SARIMAX(
                    series,
                    order=order,
                    enforce_stationarity=False,
                    enforce_invertibility=False,
                )
                fitted = model.fit(disp=False)
            if fitted.aic < best_aic:
                best_model = fitted
                best_aic = fitted.aic
                best_order = order
        except Exception:
            continue

    if best_model is None:
        raise RuntimeError("No se pudo ajustar un modelo ARIMA válido")
    return best_model, best_order, best_aic


def _prepare_result(
    categoria: str,
    model,
    series: pd.Series,
    steps: int,
    order: Tuple[int, int, int],
    aic: float,
) -> ForecastResult:
    history_df = series.reset_index()
    history_df.columns = ["semana_inicio", "ventas_semana"]
    history_df["categoria"] = categoria
    history_df["tipo"] = "observado"

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        forecast_res = model.get_forecast(steps=steps)
    forecast_mean = forecast_res.predicted_mean
    conf = forecast_res.conf_int(alpha=0.2)
    forecast_df = pd.DataFrame(
        {
            "semana_inicio": forecast_mean.index,
            "ventas_semana": forecast_mean.values,
            "categoria": categoria,
            "tipo": "forecast",
            "ventas_semana_lower": conf.iloc[:, 0].values,
            "ventas_semana_upper": conf.iloc[:, 1].values,
        }
    )

    history_df["ventas_semana_lower"] = np.nan
    history_df["ventas_semana_upper"] = np.nan

    return ForecastResult(
        categoria=categoria,
        history=history_df,
        forecast=forecast_df,
        order=order,
        aic=aic,
    )


def generate_forecasts(
    ventas_semanales_categoria: pd.DataFrame,
    output_dir: Path,
    *,
    top_n: int = 10,
    forecast_steps: int = 8,
) -> Dict[str, Path]:
    ensure_directory(output_dir)
    ventas = _parse_semana(ventas_semanales_categoria)

    top_categorias = (
        ventas.groupby("categoria")["ventas_semana"].sum().nlargest(top_n).index.tolist()
    )

    resultados: List[pd.DataFrame] = []
    metadata_rows: List[Dict[str, object]] = []

    for categoria in top_categorias:
        serie_categoria = ventas[ventas["categoria"] == categoria]
        serie = (
            serie_categoria.groupby("semana_inicio")["ventas_semana"].sum()
            .sort_index()
            .asfreq("W-MON")
            .fillna(method="ffill")
        )
        if serie.count() < 12:
            continue
        model, order, aic = _fit_best_model(serie)
        result = _prepare_result(
            categoria,
            model,
            serie,
            forecast_steps,
            order=order,
            aic=aic,
        )
        resultados.append(result.history)
        resultados.append(result.forecast)
        metadata_rows.append(
            {
                "categoria": categoria,
                "order_p": order[0],
                "order_d": order[1],
                "order_q": order[2],
                "aic": aic,
                "observaciones": serie.count(),
            }
        )

    if not resultados:
        return {}

    forecast_path = output_dir / "prediccion_ventas_semanal.parquet"
    metadata_path = output_dir / "prediccion_ventas_semanal_modelos.parquet"

    pd.concat(resultados, ignore_index=True).to_parquet(forecast_path, index=False)
    pd.DataFrame(metadata_rows).to_parquet(metadata_path, index=False)

    return {
        "forecast": forecast_path,
        "metadata": metadata_path,
    }
