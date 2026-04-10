"""Descarga datos diarios de SEPA (Precios Claros) del gobierno argentino.

SEPA: Sistema Electronico de Publicidad de Precios Argentinos
Fuente: https://datos.produccion.gob.ar/dataset/sepa-precios
~12 millones de registros diarios, +70.000 productos, 3.600 sucursales.
"""
import io
import zipfile
import logging
from pathlib import Path
from datetime import datetime

import pandas as pd
import requests

from src.competitive.config import (
    SEPA_API_BASE,
    SEPA_RAW_DIR,
    PROVINCIAS_INTERES,
)

logger = logging.getLogger(__name__)

REQUEST_TIMEOUT = 30
DOWNLOAD_TIMEOUT = 120


def get_latest_sepa_resource_url() -> tuple[str, str]:
    """Consulta CKAN API y retorna (url, fecha) del recurso ZIP mas reciente.

    Returns:
        Tuple de (download_url, date_string YYYY-MM-DD)

    Raises:
        ValueError: Si no encuentra recursos ZIP.
        requests.RequestException: Si falla la conexion.
    """
    resp = requests.get(SEPA_API_BASE, timeout=REQUEST_TIMEOUT)
    resp.raise_for_status()
    data = resp.json()

    resources = data["result"]["resources"]
    zips = [r for r in resources if r.get("format", "").upper() == "ZIP"]

    if not zips:
        raise ValueError("No se encontraron recursos ZIP en el dataset SEPA")

    latest = sorted(zips, key=lambda r: r["last_modified"], reverse=True)[0]
    date_str = latest["last_modified"][:10]

    logger.info(f"SEPA recurso mas reciente: {date_str}")
    return latest["url"], date_str


def download_sepa_zip(url: str, output_dir: Path | None = None) -> Path:
    """Descarga ZIP de SEPA y lo guarda en disco.

    Args:
        url: URL directa al archivo ZIP.
        output_dir: Directorio destino. Default: data/competitive/sepa_raw/

    Returns:
        Path al archivo ZIP descargado.
    """
    output_dir = output_dir or SEPA_RAW_DIR
    output_dir.mkdir(parents=True, exist_ok=True)

    logger.info(f"Descargando SEPA ZIP desde {url[:80]}...")
    resp = requests.get(url, timeout=DOWNLOAD_TIMEOUT)
    resp.raise_for_status()

    timestamp = datetime.now().strftime("%Y-%m-%d")
    zip_path = output_dir / f"sepa_{timestamp}.zip"
    zip_path.write_bytes(resp.content)

    size_mb = len(resp.content) / (1024 * 1024)
    logger.info(f"SEPA ZIP descargado: {zip_path} ({size_mb:.1f} MB)")
    return zip_path


def extract_sepa_csv(
    zip_path: Path,
    provincias: list[str] | None = None,
) -> pd.DataFrame:
    """Extrae CSV del ZIP y retorna DataFrame filtrado.

    Args:
        zip_path: Path al archivo ZIP.
        provincias: Lista de provincias para filtrar. None = todas.

    Returns:
        DataFrame con datos SEPA filtrados.
    """
    provincias = provincias or PROVINCIAS_INTERES

    with zipfile.ZipFile(zip_path, "r") as zf:
        csv_files = [f for f in zf.namelist() if f.endswith(".csv")]
        if not csv_files:
            raise ValueError(f"No se encontro CSV dentro de {zip_path}")

        with zf.open(csv_files[0]) as f:
            df = pd.read_csv(
                io.TextIOWrapper(f, encoding="utf-8"),
                sep="|",
                low_memory=False,
            )

    logger.info(f"SEPA CSV cargado: {len(df):,} filas, {len(df.columns)} columnas")

    # Normalizar texto para filtrado
    if "sucursales_provincia" in df.columns:
        df["sucursales_provincia"] = df["sucursales_provincia"].str.upper().str.strip()

    # Filtrar por provincia
    if provincias:
        provincias_upper = [p.upper() for p in provincias]
        df = df[df["sucursales_provincia"].isin(provincias_upper)]
        logger.info(f"Filtrado por provincias {provincias_upper}: {len(df):,} filas")

    return df


def fetch_sepa_daily(
    output_dir: Path | None = None,
    provincias: list[str] | None = None,
) -> tuple[pd.DataFrame, str]:
    """Pipeline completo: obtiene datos SEPA del dia.

    Returns:
        Tuple de (DataFrame filtrado, fecha string)
    """
    url, date_str = get_latest_sepa_resource_url()
    zip_path = download_sepa_zip(url, output_dir=output_dir)
    df = extract_sepa_csv(zip_path, provincias=provincias)
    return df, date_str
