"""Tests para el descargador de datos SEPA."""
import pytest
import pandas as pd
from pathlib import Path
from unittest.mock import patch, MagicMock
import zipfile
import io
import json

from src.competitive.sepa_downloader import (
    get_latest_sepa_resource_url,
    download_sepa_zip,
    extract_sepa_csv,
    fetch_sepa_daily,
)
from src.competitive.config import SEPA_RAW_DIR


# --- Fixtures ---

@pytest.fixture
def sample_ckan_response():
    """Respuesta simulada del CKAN API de datos.produccion.gob.ar."""
    return {
        "success": True,
        "result": {
            "resources": [
                {
                    "id": "abc123",
                    "name": "sepa-precios-2026-04-09.zip",
                    "url": "https://datos.produccion.gob.ar/dataset/xxx/resource/abc123/download/sepa-precios.zip",
                    "format": "ZIP",
                    "last_modified": "2026-04-09T10:00:00",
                },
                {
                    "id": "def456",
                    "name": "sepa-precios-2026-04-08.zip",
                    "url": "https://datos.produccion.gob.ar/dataset/xxx/resource/def456/download/sepa-precios.zip",
                    "format": "ZIP",
                    "last_modified": "2026-04-08T10:00:00",
                },
            ]
        },
    }


@pytest.fixture
def sample_sepa_csv_content():
    """CSV simulado con formato SEPA real."""
    return (
        "id_producto|productos_descripcion|productos_precio_lista|"
        "sucursales_nombre|sucursales_cadena|sucursales_provincia|"
        "sucursales_tipo|productos_marca|productos_ean\n"
        "1001|LECHE ENTERA 1L|1250.50|SUC MENDOZA CENTRO|CARREFOUR|MENDOZA|"
        "Hipermercado|LA SERENISIMA|7790001234567\n"
        "1002|COCA COLA 2.25L|2100.00|SUC MENDOZA CENTRO|CARREFOUR|MENDOZA|"
        "Hipermercado|COCA COLA|7790002345678\n"
        "1003|PAN LACTAL 500G|1500.75|SUC GODOY CRUZ|CHANGOMAS|MENDOZA|"
        "Supermercado|BIMBO|7790003456789\n"
    )


@pytest.fixture
def sample_sepa_zip(sample_sepa_csv_content):
    """ZIP en memoria con CSV SEPA."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("sepa-precios.csv", sample_sepa_csv_content)
    buf.seek(0)
    return buf.read()


# --- Tests ---

def test_get_latest_resource_url_returns_most_recent(sample_ckan_response):
    """Debe retornar la URL del recurso mas reciente."""
    with patch("src.competitive.sepa_downloader.requests.get") as mock_get:
        mock_get.return_value = MagicMock(
            status_code=200,
            json=lambda: sample_ckan_response
        )
        url, date = get_latest_sepa_resource_url()
        assert "abc123" in url
        assert "2026-04-09" in date


def test_download_sepa_zip_saves_file(tmp_path, sample_sepa_zip):
    """Debe descargar y guardar el ZIP en disco."""
    with patch("src.competitive.sepa_downloader.requests.get") as mock_get:
        mock_get.return_value = MagicMock(
            status_code=200,
            content=sample_sepa_zip
        )
        result = download_sepa_zip(
            "https://example.com/sepa.zip",
            output_dir=tmp_path
        )
        assert result.exists()
        assert result.suffix == ".zip"


def test_extract_sepa_csv_returns_dataframe(tmp_path, sample_sepa_zip):
    """Debe extraer CSV del ZIP y retornar DataFrame."""
    zip_path = tmp_path / "sepa.zip"
    zip_path.write_bytes(sample_sepa_zip)

    df = extract_sepa_csv(zip_path)
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 3
    assert "productos_descripcion" in df.columns
    assert "productos_precio_lista" in df.columns
    assert "sucursales_cadena" in df.columns


def test_extract_sepa_csv_filters_by_provincia(tmp_path, sample_sepa_zip):
    """Debe filtrar solo las provincias de interes."""
    zip_path = tmp_path / "sepa.zip"
    zip_path.write_bytes(sample_sepa_zip)

    df = extract_sepa_csv(zip_path, provincias=["MENDOZA"])
    assert len(df) == 3
    assert all(df["sucursales_provincia"] == "MENDOZA")


def test_fetch_sepa_daily_end_to_end(tmp_path, sample_ckan_response, sample_sepa_zip):
    """Pipeline completo: API -> ZIP -> CSV -> DataFrame."""
    with patch("src.competitive.sepa_downloader.requests.get") as mock_get:
        def side_effect(url, **kwargs):
            resp = MagicMock(status_code=200)
            if "api/3/action" in url:
                resp.json = lambda: sample_ckan_response
            else:
                resp.content = sample_sepa_zip
            return resp

        mock_get.side_effect = side_effect

        df, date = fetch_sepa_daily(output_dir=tmp_path, provincias=["MENDOZA"])
        assert isinstance(df, pd.DataFrame)
        assert len(df) > 0
        assert date == "2026-04-09"
