"""ETL para normalizar datos SEPA al formato interno de NINO."""
import logging
from pathlib import Path

import pandas as pd

from src.competitive.config import SEPA_PROCESSED_DIR

logger = logging.getLogger(__name__)

# Mapeo SEPA -> schema interno
COLUMN_MAP = {
    "productos_ean": "ean",
    "productos_descripcion": "descripcion",
    "productos_precio_lista": "precio",
    "productos_marca": "marca",
    "sucursales_cadena": "cadena",
    "sucursales_nombre": "sucursal",
    "sucursales_provincia": "provincia",
    "sucursales_tipo": "tipo_sucursal",
}

TEXT_COLUMNS = ["descripcion", "marca", "cadena", "sucursal", "provincia"]


def normalize_sepa_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Renombra columnas SEPA y normaliza texto.

    Args:
        df: DataFrame crudo de SEPA.

    Returns:
        DataFrame con columnas renombradas y texto normalizado.
    """
    df = df.rename(columns=COLUMN_MAP)

    # Normalizar texto
    for col in TEXT_COLUMNS:
        if col in df.columns:
            df[col] = df[col].astype(str).str.upper().str.strip()

    # Asegurar EAN como string limpio
    if "ean" in df.columns:
        df["ean"] = df["ean"].astype(str).str.strip().str.replace(r"\.0$", "", regex=True)

    # Precio numerico
    if "precio" in df.columns:
        df["precio"] = pd.to_numeric(df["precio"], errors="coerce")
        df = df.dropna(subset=["precio"])

    logger.info(f"SEPA normalizado: {len(df):,} filas")
    return df


def aggregate_by_product_chain(df: pd.DataFrame) -> pd.DataFrame:
    """Agrega precios por producto (EAN) y cadena.

    Calcula min, max, promedio y cuenta de sucursales.
    """
    agg = (
        df.groupby(["ean", "cadena", "descripcion", "marca"])
        .agg(
            precio_min=("precio", "min"),
            precio_max=("precio", "max"),
            precio_promedio=("precio", "mean"),
            n_sucursales=("sucursal", "nunique"),
        )
        .reset_index()
    )

    agg["precio_promedio"] = agg["precio_promedio"].round(2)

    logger.info(
        f"Agregado: {len(agg):,} combinaciones producto-cadena "
        f"({agg['ean'].nunique():,} productos, {agg['cadena'].nunique()} cadenas)"
    )
    return agg


def save_sepa_parquet(
    df: pd.DataFrame,
    output_dir: Path | None = None,
    date_str: str = "",
) -> Path:
    """Guarda DataFrame procesado como parquet."""
    output_dir = output_dir or SEPA_PROCESSED_DIR
    output_dir.mkdir(parents=True, exist_ok=True)

    filename = f"sepa_precios_{date_str}.parquet" if date_str else "sepa_precios_latest.parquet"
    path = output_dir / filename
    df.to_parquet(path, index=False)

    logger.info(f"Guardado: {path} ({len(df):,} filas)")
    return path


def run_sepa_etl(
    raw_df: pd.DataFrame,
    output_dir: Path | None = None,
    date_str: str = "",
) -> pd.DataFrame:
    """Pipeline ETL completo de SEPA."""
    normalized = normalize_sepa_columns(raw_df)
    aggregated = aggregate_by_product_chain(normalized)
    save_sepa_parquet(aggregated, output_dir=output_dir, date_str=date_str)

    # Guardar tambien version "latest" para el dashboard
    if date_str:
        save_sepa_parquet(aggregated, output_dir=output_dir, date_str="")

    return aggregated
