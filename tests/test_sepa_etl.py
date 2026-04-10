"""Tests para ETL de datos SEPA."""
import pytest
import pandas as pd
from pathlib import Path

from src.competitive.sepa_etl import (
    normalize_sepa_columns,
    aggregate_by_product_chain,
    save_sepa_parquet,
    run_sepa_etl,
)


@pytest.fixture
def raw_sepa_df():
    """DataFrame crudo simulando formato SEPA."""
    return pd.DataFrame({
        "productos_ean": ["7790001234567", "7790001234567", "7790002345678",
                          "7790002345678", "7790003456789"],
        "productos_descripcion": ["LECHE ENTERA 1L", "LECHE ENTERA 1L",
                                  "COCA COLA 2.25L", "COCA COLA 2.25L",
                                  "PAN LACTAL 500G"],
        "productos_precio_lista": [1250.50, 1300.00, 2100.00, 2050.00, 1500.75],
        "productos_marca": ["LA SERENISIMA", "LA SERENISIMA",
                           "COCA COLA", "COCA COLA", "BIMBO"],
        "sucursales_cadena": ["CARREFOUR", "CHANGOMAS",
                             "CARREFOUR", "JUMBO", "DISCO"],
        "sucursales_nombre": ["SUC MENDOZA", "SUC GODOY CRUZ",
                             "SUC MENDOZA", "SUC LUJAN", "SUC MAIPU"],
        "sucursales_provincia": ["MENDOZA", "MENDOZA",
                                "MENDOZA", "MENDOZA", "MENDOZA"],
        "sucursales_tipo": ["Hipermercado", "Supermercado",
                           "Hipermercado", "Hipermercado", "Supermercado"],
    })


def test_normalize_columns_renames_correctly(raw_sepa_df):
    """Debe renombrar columnas SEPA al schema interno."""
    df = normalize_sepa_columns(raw_sepa_df)
    assert "ean" in df.columns
    assert "descripcion" in df.columns
    assert "precio" in df.columns
    assert "cadena" in df.columns
    assert "marca" in df.columns


def test_normalize_columns_cleans_text(raw_sepa_df):
    """Debe normalizar texto a UPPER y sin espacios extra."""
    df = normalize_sepa_columns(raw_sepa_df)
    assert all(df["cadena"] == df["cadena"].str.upper().str.strip())
    assert all(df["marca"] == df["marca"].str.upper().str.strip())


def test_aggregate_computes_stats(raw_sepa_df):
    """Debe agregar precio min/max/mean por producto+cadena."""
    df = normalize_sepa_columns(raw_sepa_df)
    agg = aggregate_by_product_chain(df)

    # Leche en Carrefour: solo 1 registro -> min=max=mean=1250.50
    leche_carrefour = agg[
        (agg["ean"] == "7790001234567") & (agg["cadena"] == "CARREFOUR")
    ]
    assert len(leche_carrefour) == 1
    assert leche_carrefour.iloc[0]["precio_min"] == 1250.50
    assert leche_carrefour.iloc[0]["precio_max"] == 1250.50


def test_aggregate_counts_sucursales(raw_sepa_df):
    """Debe contar en cuantas sucursales aparece cada producto."""
    df = normalize_sepa_columns(raw_sepa_df)
    agg = aggregate_by_product_chain(df)
    leche_carrefour = agg[
        (agg["ean"] == "7790001234567") & (agg["cadena"] == "CARREFOUR")
    ]
    assert leche_carrefour.iloc[0]["n_sucursales"] == 1


def test_save_parquet_creates_file(tmp_path, raw_sepa_df):
    """Debe guardar parquet procesado."""
    df = normalize_sepa_columns(raw_sepa_df)
    agg = aggregate_by_product_chain(df)
    path = save_sepa_parquet(agg, output_dir=tmp_path, date_str="2026-04-09")
    assert path.exists()
    loaded = pd.read_parquet(path)
    assert len(loaded) == len(agg)


def test_run_sepa_etl_end_to_end(tmp_path, raw_sepa_df):
    """Pipeline ETL completo."""
    result = run_sepa_etl(raw_sepa_df, output_dir=tmp_path, date_str="2026-04-09")
    assert isinstance(result, pd.DataFrame)
    assert "ean" in result.columns
    assert "precio_promedio" in result.columns
    assert "cadena" in result.columns
