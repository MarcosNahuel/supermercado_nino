"""ETL module that prepares transactional data for downstream analytics."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import numpy as np
import pandas as pd


@dataclass
class EtlArtifacts:
    detalle: pd.DataFrame
    tickets: pd.DataFrame
    ventas_diarias: pd.DataFrame
    ventas_semanales_categoria: pd.DataFrame


COLUMN_MAPPING = {
    "Fecha": "fecha",
    "Comprobante": "ticket_id",
    "Código": "producto_id",
    "Codigo": "producto_id",
    "Código barras": "codigo_barras",
    "Codigo barras": "codigo_barras",
    "Marca": "marca",
    "Departamento": "categoria",
    "Nombre": "descripcion",
    "Cantidad": "cantidad",
    "Importe": "importe_total",
    "Unitario": "precio_unitario",
    "TIPO FACTURA": "tipo_factura",
    "Tipo medio de pago": "tipo_medio_pago",
    "Emisor tarjeta": "emisor_tarjeta",
}


def _normalize_text(series: pd.Series, fill: str) -> pd.Series:
    text = series.astype(str).str.strip().str.upper()
    text = text.replace({"NAN": np.nan})
    return text.fillna(fill)


def _enrich_temporal(df: pd.DataFrame, feriados: Optional[pd.DataFrame]) -> pd.DataFrame:
    df["anio"] = df["fecha"].dt.year
    df["mes"] = df["fecha"].dt.month
    df["dia"] = df["fecha"].dt.day
    df["dia_semana"] = df["fecha"].dt.day_name()
    df["hora"] = df["fecha"].dt.hour
    df["periodo"] = df["anio"].astype(str) + "-" + df["mes"].astype(str).str.zfill(2)

    iso_calendar = df["fecha"].dt.isocalendar()
    df["semana_iso"] = (
        iso_calendar["year"].astype(str)
        + "-W"
        + iso_calendar["week"].astype(str).str.zfill(2)
    )

    df["es_fin_de_semana"] = df["fecha"].dt.dayofweek >= 5

    if feriados is None or feriados.empty:
        df["es_feriado"] = False
    else:
        feriados_idx = feriados["fecha"].dt.normalize().unique()
        df["es_feriado"] = df["fecha"].dt.normalize().isin(feriados_idx)

    df["tipo_dia"] = np.select(
        [df["es_feriado"], df["es_fin_de_semana"]],
        ["FERIADO", "FDS"],
        default="HABIL",
    )
    return df


def run_etl(
    raw_sales: pd.DataFrame,
    rentabilidad: pd.DataFrame,
    feriados: Optional[pd.DataFrame] = None,
    *,
    fallback_rentabilidad: float = 18.0,
) -> EtlArtifacts:
    """Execute ETL steps and return canonical datasets."""
    rename_columns = {
        source: target for source, target in COLUMN_MAPPING.items() if source in raw_sales.columns
    }
    df = raw_sales.rename(columns=rename_columns)

    df["fecha"] = pd.to_datetime(df["fecha"], errors="coerce")
    df = df[df["fecha"].notna()].copy()

    df["cantidad"] = pd.to_numeric(
        df["cantidad"].astype(str).str.replace(",", "."), errors="coerce"
    )
    df["precio_unitario"] = pd.to_numeric(
        df["precio_unitario"].astype(str).str.replace(",", "."), errors="coerce"
    )

    df["categoria"] = _normalize_text(df.get("categoria", pd.Series(dtype=str)), "SIN CATEGORIA")
    df["marca"] = _normalize_text(df.get("marca", pd.Series(dtype=str)), "SIN MARCA")
    df["descripcion"] = _normalize_text(df.get("descripcion", pd.Series(dtype=str)), "SIN DESCRIPCION")
    df["producto_id"] = _normalize_text(df.get("producto_id", pd.Series(dtype=str)), "SIN CODIGO")
    df["tipo_medio_pago"] = _normalize_text(
        df.get("tipo_medio_pago", pd.Series(dtype=str)), "EFECTIVO"
    ).replace(
        {
            "DEBITO": "TARJETA_DEBITO",
            "CREDITO": "TARJETA_CREDITO",
            "TARJETA DEBITO": "TARJETA_DEBITO",
            "TARJETA CREDITO": "TARJETA_CREDITO",
        }
    )
    df["emisor_tarjeta"] = _normalize_text(
        df.get("emisor_tarjeta", pd.Series(dtype=str)), "DESCONOCIDO"
    )

    df = _enrich_temporal(df, feriados)

    rent_dict = rentabilidad.set_index("Departamento")["rentabilidad_pct"].to_dict()
    clas_dict = rentabilidad.set_index("Departamento")["Clasificacion"].to_dict()

    df["rentabilidad_pct"] = df["categoria"].map(rent_dict).fillna(fallback_rentabilidad)
    df["clasificacion_departamento"] = df["categoria"].map(clas_dict).fillna(
        "SIN CLASIFICACION"
    )
    df["margen_linea"] = df["importe_total"] * (df["rentabilidad_pct"] / 100.0)

    tickets = (
        df.groupby("ticket_id")
        .agg(
            fecha=("fecha", "first"),
            anio=("anio", "first"),
            mes=("mes", "first"),
            semana_iso=("semana_iso", "first"),
            tipo_dia=("tipo_dia", "first"),
            tipo_medio_pago=("tipo_medio_pago", lambda x: x.mode().iat[0] if not x.mode().empty else "EFECTIVO"),
            ventas_totales=("importe_total", "sum"),
            margen_total=("margen_linea", "sum"),
            unidades_totales=("cantidad", "sum"),
            productos_unicos=("producto_id", "nunique"),
        )
        .reset_index()
    )

    ventas_diarias = (
        df.groupby(["fecha", "anio", "mes", "semana_iso", "tipo_dia"])
        .agg(
            ventas_totales=("importe_total", "sum"),
            margen_total=("margen_linea", "sum"),
            unidades_totales=("cantidad", "sum"),
            tickets=("ticket_id", "nunique"),
        )
        .reset_index()
    )

    ventas_semanales_categoria = (
        df.groupby(["semana_iso", "anio", "categoria"])
        .agg(
            ventas_semana=("importe_total", "sum"),
            margen_semana=("margen_linea", "sum"),
            unidades_semana=("cantidad", "sum"),
            tickets_semana=("ticket_id", "nunique"),
        )
        .reset_index()
    )

    return EtlArtifacts(
        detalle=df,
        tickets=tickets,
        ventas_diarias=ventas_diarias,
        ventas_semanales_categoria=ventas_semanales_categoria,
    )

