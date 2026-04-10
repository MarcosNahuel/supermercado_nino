"""Matching de productos NINO vs competencia por codigo EAN.

Cruza los 10K SKUs de NINO (detalle_lineas.parquet) con datos de SEPA
y promos VTEX para generar comparaciones de precios.
"""
import logging
from pathlib import Path

import pandas as pd

logger = logging.getLogger(__name__)


def load_nino_products(
    detalle_df: pd.DataFrame | None = None,
    parquet_path: Path | None = None,
) -> pd.DataFrame:
    """Carga y agrega productos NINO por EAN.

    Calcula precio promedio ponderado por cantidad vendida.

    Args:
        detalle_df: DataFrame de detalle_lineas. Si None, lee de parquet.
        parquet_path: Path al parquet. Default: data/app_dataset/detalle_lineas.parquet

    Returns:
        DataFrame con un registro por EAN: ean, descripcion, marca, categoria,
        nino_precio_promedio, nino_unidades_vendidas.
    """
    if detalle_df is None:
        parquet_path = parquet_path or Path("data/app_dataset/detalle_lineas.parquet")
        detalle_df = pd.read_parquet(
            parquet_path,
            columns=["codigo_barras", "descripcion", "marca", "categoria",
                     "precio_unitario", "cantidad", "importe_total"],
        )

    df = detalle_df.copy()
    df = df.rename(columns={"codigo_barras": "ean"})
    df["ean"] = df["ean"].astype(str).str.strip().str.replace(r"\.0$", "", regex=True)

    # Filtrar EAN validos (numerico, >6 digitos)
    df = df[df["ean"].str.match(r"^\d{7,}$", na=False)]

    # Agregar por EAN: precio ponderado por cantidad
    agg = (
        df.groupby("ean")
        .agg(
            descripcion=("descripcion", "first"),
            marca=("marca", "first"),
            categoria=("categoria", "first"),
            nino_precio_promedio=("precio_unitario", lambda x: (x * df.loc[x.index, "cantidad"]).sum() / df.loc[x.index, "cantidad"].sum()),
            nino_unidades_vendidas=("cantidad", "sum"),
        )
        .reset_index()
    )

    agg["nino_precio_promedio"] = agg["nino_precio_promedio"].round(2)

    logger.info(f"NINO productos cargados: {len(agg):,} EANs unicos")
    return agg


def match_sepa_to_nino(
    nino_df: pd.DataFrame,
    sepa_df: pd.DataFrame,
) -> pd.DataFrame:
    """Cruza precios SEPA con productos NINO por EAN.

    Args:
        nino_df: Output de load_nino_products().
        sepa_df: Output de sepa_etl.aggregate_by_product_chain().

    Returns:
        DataFrame con comparacion: producto, precio NINO, precio competencia,
        diferencia absoluta y porcentual.
    """
    merged = sepa_df.merge(
        nino_df[["ean", "nino_precio_promedio", "nino_unidades_vendidas", "categoria"]],
        on="ean",
        how="inner",
        suffixes=("_sepa", "_nino"),
    )

    if "categoria_nino" in merged.columns:
        merged["categoria"] = merged["categoria_nino"]
        merged = merged.drop(columns=["categoria_sepa", "categoria_nino"], errors="ignore")

    # Calcular diferencia: negativo = NINO mas barato
    merged["diferencia_abs"] = (
        merged["nino_precio_promedio"] - merged["precio_promedio"]
    ).round(2)
    merged["diferencia_pct"] = (
        (merged["diferencia_abs"] / merged["precio_promedio"]) * 100
    ).round(1)

    logger.info(
        f"Match SEPA-NINO: {len(merged):,} cruces "
        f"({merged['ean'].nunique():,} productos en comun)"
    )
    return merged


def match_vtex_to_nino(
    nino_df: pd.DataFrame,
    vtex_df: pd.DataFrame,
) -> pd.DataFrame:
    """Cruza promos VTEX con productos NINO por EAN.

    Args:
        nino_df: Output de load_nino_products().
        vtex_df: Output de vtex_scraper.scrape_all_chains().

    Returns:
        DataFrame con productos NINO que tienen promos en la competencia.
    """
    merged = vtex_df.merge(
        nino_df[["ean", "nino_precio_promedio", "nino_unidades_vendidas", "categoria"]],
        on="ean",
        how="inner",
    )

    logger.info(
        f"Match VTEX-NINO: {len(merged):,} cruces, "
        f"{merged['tiene_promo'].sum():,} con promo activa"
    )
    return merged


def compute_price_comparison(
    nino_df: pd.DataFrame,
    sepa_df: pd.DataFrame | None = None,
    vtex_df: pd.DataFrame | None = None,
) -> pd.DataFrame:
    """Genera tabla de comparacion completa unificando SEPA y VTEX.

    Returns:
        DataFrame con comparacion unificada de precios y promos.
    """
    frames = []

    if sepa_df is not None and not sepa_df.empty:
        sepa_match = match_sepa_to_nino(nino_df, sepa_df)
        sepa_match["fuente"] = "SEPA"
        if "tiene_promo" not in sepa_match.columns:
            sepa_match["tiene_promo"] = False
            sepa_match["promo_nombre"] = ""
        frames.append(sepa_match)

    if vtex_df is not None and not vtex_df.empty:
        vtex_match = match_vtex_to_nino(nino_df, vtex_df)
        vtex_match["fuente"] = "VTEX"
        # VTEX usa precio_venta; normalizar a precio_promedio para unificar schema
        if "precio_promedio" not in vtex_match.columns:
            vtex_match["precio_promedio"] = vtex_match["precio_venta"]
        if "diferencia_pct" not in vtex_match.columns:
            vtex_match["diferencia_abs"] = (
                vtex_match["nino_precio_promedio"] - vtex_match["precio_venta"]
            ).round(2)
            vtex_match["diferencia_pct"] = (
                (vtex_match["diferencia_abs"] / vtex_match["precio_venta"]) * 100
            ).round(1)
        frames.append(vtex_match)

    if not frames:
        return pd.DataFrame()

    result = pd.concat(frames, ignore_index=True)

    logger.info(f"Comparacion total: {len(result):,} registros")
    return result
