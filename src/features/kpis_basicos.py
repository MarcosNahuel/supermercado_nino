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


def build_kpi_periodo(ventas_diarias: pd.DataFrame) -> pd.DataFrame:
    """
    Genera KPIs mensuales (periodo) usando valores NORMALIZADOS.
    Oct y Nov 2025 usan tickets_normalizados para compensar datos faltantes.
    """
    # Crear columna periodo si no existe
    if "periodo" not in ventas_diarias.columns:
        ventas_diarias = ventas_diarias.copy()
        ventas_diarias["periodo"] = (
            ventas_diarias["anio"].astype(str) + "-" +
            ventas_diarias["mes"].astype(str).str.zfill(2)
        )

    # Usar valores normalizados si existen, sino los originales
    ventas_col = "ventas_normalizadas" if "ventas_normalizadas" in ventas_diarias.columns else "ventas_totales"
    margen_col = "margen_normalizado" if "margen_normalizado" in ventas_diarias.columns else "margen_total"
    tickets_col = "tickets_normalizados" if "tickets_normalizados" in ventas_diarias.columns else "tickets"
    unidades_col = "unidades_normalizadas" if "unidades_normalizadas" in ventas_diarias.columns else "unidades_totales"

    grouped = (
        ventas_diarias.groupby("periodo")
        .agg(
            ventas_totales=(ventas_col, "sum"),
            margen_total=(margen_col, "sum"),
            tickets=(tickets_col, "sum"),
            unidades_totales=(unidades_col, "sum"),
        )
        .reset_index()
    )
    grouped["ticket_promedio"] = _safe_ratio(grouped["ventas_totales"], grouped["tickets"])
    grouped["upt"] = _safe_ratio(grouped["unidades_totales"], grouped["tickets"])
    grouped["margen_pct"] = _safe_ratio(grouped["margen_total"], grouped["ventas_totales"])
    grouped = grouped.sort_values("periodo")
    return grouped


def build_kpi_semana(ventas_diarias: pd.DataFrame) -> pd.DataFrame:
    """
    Genera KPIs semanales usando valores NORMALIZADOS.
    Semanas de Oct y Nov 2025 usan tickets_normalizados para compensar datos faltantes.
    """
    # Usar valores normalizados si existen, sino los originales
    ventas_col = "ventas_normalizadas" if "ventas_normalizadas" in ventas_diarias.columns else "ventas_totales"
    margen_col = "margen_normalizado" if "margen_normalizado" in ventas_diarias.columns else "margen_total"
    tickets_col = "tickets_normalizados" if "tickets_normalizados" in ventas_diarias.columns else "tickets"
    unidades_col = "unidades_normalizadas" if "unidades_normalizadas" in ventas_diarias.columns else "unidades_totales"

    grouped = (
        ventas_diarias.groupby("semana_iso")
        .agg(
            ventas_totales=(ventas_col, "sum"),
            margen_total=(margen_col, "sum"),
            tickets=(tickets_col, "sum"),
            unidades_totales=(unidades_col, "sum"),
            semana_inicio=("fecha", "min"),
        )
        .reset_index()
    )
    grouped["ticket_promedio"] = _safe_ratio(grouped["ventas_totales"], grouped["tickets"])
    grouped["upt"] = _safe_ratio(grouped["unidades_totales"], grouped["tickets"])
    grouped["margen_pct"] = _safe_ratio(grouped["margen_total"], grouped["ventas_totales"])
    grouped = grouped.sort_values("semana_iso")
    return grouped


def export_kpis(
    *,
    output_dir: Path,
    kpi_dia: pd.DataFrame,
    kpi_tipo_dia: pd.DataFrame,
    kpi_categoria: pd.DataFrame,
    kpi_medio_pago: pd.DataFrame,
    kpi_periodo: pd.DataFrame = None,
    kpi_semana: pd.DataFrame = None,
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

    # Exportar KPIs de periodo y semana si se proporcionan
    if kpi_periodo is not None:
        paths["kpi_periodo"] = output_dir / "kpi_periodo.parquet"
        kpi_periodo.to_parquet(paths["kpi_periodo"], index=False)
    if kpi_semana is not None:
        paths["kpi_semana"] = output_dir / "kpi_semana.parquet"
        kpi_semana.to_parquet(paths["kpi_semana"], index=False)

    return paths

