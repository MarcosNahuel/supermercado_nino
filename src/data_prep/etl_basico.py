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
    "RENTABILIDAD": "rentabilidad_factor",
    "mARGEN DE RENTABILIDAD": "margen_rentabilidad_pct",
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
    fecha_corte: str = "2026-03-31",
) -> EtlArtifacts:
    """Execute ETL steps and return canonical datasets."""
    rename_columns = {
        source: target for source, target in COLUMN_MAPPING.items() if source in raw_sales.columns
    }
    df = raw_sales.rename(columns=rename_columns)

    df["fecha"] = pd.to_datetime(df["fecha"], errors="coerce")
    df = df[df["fecha"].notna()].copy()

    # Filtrar hasta fecha de corte (excluir datos incompletos posteriores)
    df = df[df["fecha"] <= pd.Timestamp(fecha_corte)].copy()

    # Marcar meses con datos incompletos (Oct y Nov 2025 tuvieron pérdida de información)
    # Estos meses tienen ~30-50% menos transacciones que el promedio
    df["mes_incompleto"] = (
        ((df["fecha"].dt.year == 2025) & (df["fecha"].dt.month == 10)) |
        ((df["fecha"].dt.year == 2025) & (df["fecha"].dt.month == 11))
    )

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
            "BILLETERA VITUAL": "BILLETERA VIRTUAL",
        }
    )
    df["emisor_tarjeta"] = _normalize_text(
        df.get("emisor_tarjeta", pd.Series(dtype=str)), "DESCONOCIDO"
    )

    df = _enrich_temporal(df, feriados)

    # Usar rentabilidad del CSV si está disponible, sino del archivo auxiliar
    if "margen_rentabilidad_pct" in df.columns and df["margen_rentabilidad_pct"].notna().any():
        # El CSV ya tiene el porcentaje de margen por línea
        df["rentabilidad_pct"] = pd.to_numeric(
            df["margen_rentabilidad_pct"].astype(str).str.replace(",", "."), errors="coerce"
        ).fillna(fallback_rentabilidad)
    else:
        # Fallback: usar archivo RENTABILIDAD.csv por departamento
        rent_dict = rentabilidad.set_index("Departamento")["rentabilidad_pct"].to_dict()
        df["rentabilidad_pct"] = df["categoria"].map(rent_dict).fillna(fallback_rentabilidad)

    # Clasificación del departamento del archivo auxiliar
    clas_dict = rentabilidad.set_index("Departamento")["Clasificacion"].to_dict()
    df["clasificacion_departamento"] = df["categoria"].map(clas_dict).fillna(
        "SIN CLASIFICACION"
    )

    # Calcular margen usando rentabilidad del CSV si está disponible
    if "rentabilidad_factor" in df.columns and df["rentabilidad_factor"].notna().any():
        # Factor de rentabilidad (ej: 0.28 = 28%)
        df["rentabilidad_factor_clean"] = pd.to_numeric(
            df["rentabilidad_factor"].astype(str).str.replace(",", "."), errors="coerce"
        )
        df["margen_linea"] = df["importe_total"] * df["rentabilidad_factor_clean"].fillna(
            df["rentabilidad_pct"] / 100.0
        )
        # Corregir rentabilidad_pct: usar factor * 100 como porcentaje real
        # (el campo margen_rentabilidad_pct del CSV contiene el margen absoluto,
        #  no el porcentaje — la fuente de verdad es rentabilidad_factor)
        df["rentabilidad_pct"] = (
            df["rentabilidad_factor_clean"].fillna(fallback_rentabilidad / 100.0) * 100.0
        )
        df = df.drop(columns=["rentabilidad_factor_clean"])
    else:
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
            mes_incompleto=("mes_incompleto", "first"),
        )
        .reset_index()
    )

    # Normalización de meses con datos incompletos (Oct y Nov 2025)
    # Factor basado en: promedio mensual normal ~230K transacciones
    # Oct 2025: ~72K (factor 3.2), Nov 2025: ~130K (factor 1.8)
    factor_normalizacion = {
        (2025, 10): 3.2,  # Oct 2025 perdió ~69% de datos
        (2025, 11): 1.8,  # Nov 2025 perdió ~44% de datos
    }

    def get_factor(row):
        key = (row["anio"], row["mes"])
        return factor_normalizacion.get(key, 1.0)

    ventas_diarias["factor_norm"] = ventas_diarias.apply(get_factor, axis=1)
    ventas_diarias["ventas_normalizadas"] = ventas_diarias["ventas_totales"] * ventas_diarias["factor_norm"]
    ventas_diarias["margen_normalizado"] = ventas_diarias["margen_total"] * ventas_diarias["factor_norm"]
    ventas_diarias["tickets_normalizados"] = ventas_diarias["tickets"] * ventas_diarias["factor_norm"]
    ventas_diarias["unidades_normalizadas"] = ventas_diarias["unidades_totales"] * ventas_diarias["factor_norm"]
    ventas_diarias["nota_datos"] = ventas_diarias["mes_incompleto"].apply(
        lambda x: "DATOS INCOMPLETOS - NORMALIZADO" if x else ""
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

