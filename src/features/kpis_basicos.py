"""Computation of standardized KPIs for the analytics pipeline."""

from __future__ import annotations

from pathlib import Path
from typing import Dict

import numpy as np
import pandas as pd

from src.utils.load_data import ensure_directory


def _safe_ratio(numerator: pd.Series, denominator: pd.Series) -> pd.Series:
    return numerator.div(denominator.replace({0: np.nan}))


def build_kpi_dia(ventas_diarias: pd.DataFrame) -> pd.DataFrame:
    kpi = ventas_diarias.copy()
    kpi["ticket_promedio"] = _safe_ratio(kpi["ventas_totales"], kpi["tickets"])
    kpi["upt"] = _safe_ratio(kpi["unidades_totales"], kpi["tickets"])
    kpi["margen_pct"] = _safe_ratio(kpi["margen_total"], kpi["ventas_totales"])
    kpi = kpi.sort_values("fecha")
    return kpi


def build_kpi_tipo_dia(kpi_dia: pd.DataFrame) -> pd.DataFrame:
    grouped = (
        kpi_dia.groupby("tipo_dia")
        .agg(
            ventas_totales=("ventas_totales", "sum"),
            margen_total=("margen_total", "sum"),
            unidades_totales=("unidades_totales", "sum"),
            tickets=("tickets", "sum"),
        )
        .reset_index()
    )
    grouped["ticket_promedio"] = _safe_ratio(grouped["ventas_totales"], grouped["tickets"])
    grouped["upt"] = _safe_ratio(grouped["unidades_totales"], grouped["tickets"])
    grouped["margen_pct"] = _safe_ratio(grouped["margen_total"], grouped["ventas_totales"])
    return grouped


def build_kpi_categoria(detalle: pd.DataFrame) -> pd.DataFrame:
    grouped = (
        detalle.groupby(["anio", "mes", "categoria", "tipo_dia"])
        .agg(
            ventas_totales=("importe_total", "sum"),
            margen_total=("margen_linea", "sum"),
            unidades_totales=("cantidad", "sum"),
            tickets=("ticket_id", "nunique"),
        )
        .reset_index()
    )
    grouped["ticket_promedio"] = _safe_ratio(grouped["ventas_totales"], grouped["tickets"])
    grouped["upt"] = _safe_ratio(grouped["unidades_totales"], grouped["tickets"])
    grouped["margen_pct"] = _safe_ratio(grouped["margen_total"], grouped["ventas_totales"])
    return grouped


def build_kpi_medio_pago(tickets: pd.DataFrame) -> pd.DataFrame:
    grouped = (
        tickets.groupby(["tipo_medio_pago", "anio", "mes"])
        .agg(
            ventas_totales=("ventas_totales", "sum"),
            margen_total=("margen_total", "sum"),
            unidades_totales=("unidades_totales", "sum"),
            tickets=("ticket_id", "count"),
        )
        .reset_index()
    )
    grouped["ticket_promedio"] = _safe_ratio(grouped["ventas_totales"], grouped["tickets"])
    grouped["upt"] = _safe_ratio(grouped["unidades_totales"], grouped["tickets"])
    grouped["margen_pct"] = _safe_ratio(grouped["margen_total"], grouped["ventas_totales"])
    return grouped


def export_kpis(
    *,
    output_dir: Path,
    kpi_dia: pd.DataFrame,
    kpi_tipo_dia: pd.DataFrame,
    kpi_categoria: pd.DataFrame,
    kpi_medio_pago: pd.DataFrame,
) -> Dict[str, Path]:
    ensure_directory(output_dir)
    paths = {
        "kpi_dia": output_dir / "kpi_dia.parquet",
        "kpi_tipo_dia": output_dir / "kpi_tipo_dia.parquet",
        "kpi_categoria": output_dir / "kpi_categoria.parquet",
        "kpi_medio_pago": output_dir / "kpi_medio_pago.parquet",
    }
    kpi_dia.to_parquet(paths["kpi_dia"], index=False)
    kpi_tipo_dia.to_parquet(paths["kpi_tipo_dia"], index=False)
    kpi_categoria.to_parquet(paths["kpi_categoria"], index=False)
    kpi_medio_pago.to_parquet(paths["kpi_medio_pago"], index=False)
    return paths

