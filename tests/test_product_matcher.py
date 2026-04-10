"""Tests para matching de productos NINO vs competencia."""
import warnings

import pytest
import pandas as pd

from src.competitive.product_matcher import (
    load_nino_products,
    match_sepa_to_nino,
    match_vtex_to_nino,
    compute_price_comparison,
)


@pytest.fixture
def nino_detalle():
    """Simula detalle_lineas de NINO (solo columnas relevantes)."""
    return pd.DataFrame({
        "codigo_barras": ["7790001234567", "7790001234567", "7790002345678",
                          "7790003456789", "7790003456789"],
        "descripcion": ["LECHE ENTERA 1L", "LECHE ENTERA 1L", "COCA COLA 2.25L",
                        "PAN LACTAL 500G", "PAN LACTAL 500G"],
        "marca": ["LA SERENISIMA", "LA SERENISIMA", "COCA COLA",
                  "BIMBO", "BIMBO"],
        "categoria": ["LACTEOS", "LACTEOS", "BEBIDAS", "PANADERIA", "PANADERIA"],
        "precio_unitario": [1200.00, 1250.00, 2000.00, 1400.00, 1450.00],
        "cantidad": [2, 1, 3, 1, 2],
        "importe_total": [2400.00, 1250.00, 6000.00, 1400.00, 2900.00],
    })


@pytest.fixture
def sepa_processed():
    """Datos SEPA procesados."""
    return pd.DataFrame({
        "ean": ["7790001234567", "7790001234567", "7790002345678"],
        "descripcion": ["LECHE ENTERA 1L", "LECHE ENTERA 1L", "COCA COLA 2.25L"],
        "marca": ["LA SERENISIMA", "LA SERENISIMA", "COCA COLA"],
        "cadena": ["CARREFOUR", "CHANGOMAS", "CARREFOUR"],
        "precio_promedio": [1300.00, 1280.00, 2100.00],
        "precio_min": [1250.00, 1280.00, 2050.00],
        "precio_max": [1350.00, 1280.00, 2150.00],
        "n_sucursales": [3, 1, 3],
    })


@pytest.fixture
def vtex_promos():
    """Promos VTEX scrapeadas."""
    return pd.DataFrame({
        "ean": ["7790002345678", "7790001234567"],
        "descripcion": ["Coca Cola 2.25L", "Leche Entera 1L"],
        "cadena": ["CARREFOUR", "JUMBO"],
        "precio_lista": [2100.00, 1350.00],
        "precio_venta": [1890.00, 1350.00],
        "descuento_pct": [10.0, 0.0],
        "tiene_promo": [True, False],
        "promo_nombre": ["2da unidad al 50%", ""],
    })


def test_load_nino_products_aggregates(nino_detalle):
    """Debe agregar productos NINO por EAN con precio promedio ponderado."""
    nino = load_nino_products(nino_detalle)
    assert len(nino) == 3  # 3 EAN unicos
    leche = nino[nino["ean"] == "7790001234567"].iloc[0]
    # Precio ponderado: (1200*2 + 1250*1) / 3 = 1216.67
    assert leche["nino_precio_promedio"] == pytest.approx(1216.67, abs=0.01)


def test_match_sepa_to_nino(nino_detalle, sepa_processed):
    """Debe cruzar por EAN y calcular diferencia de precio."""
    nino = load_nino_products(nino_detalle)
    matched = match_sepa_to_nino(nino, sepa_processed)
    assert len(matched) > 0
    assert "nino_precio_promedio" in matched.columns
    assert "precio_promedio" in matched.columns
    assert "diferencia_pct" in matched.columns


def test_match_sepa_shows_nino_cheaper(nino_detalle, sepa_processed):
    """Donde NINO es mas barato, diferencia_pct debe ser negativa."""
    nino = load_nino_products(nino_detalle)
    matched = match_sepa_to_nino(nino, sepa_processed)
    # Leche NINO ~1216 vs Carrefour 1300 -> NINO es mas barato -> diff < 0
    leche_carrefour = matched[
        (matched["ean"] == "7790001234567") & (matched["cadena"] == "CARREFOUR")
    ]
    assert leche_carrefour.iloc[0]["diferencia_pct"] < 0


def test_match_vtex_to_nino(nino_detalle, vtex_promos):
    """Debe cruzar promos VTEX con productos NINO."""
    nino = load_nino_products(nino_detalle)
    matched = match_vtex_to_nino(nino, vtex_promos)
    assert len(matched) > 0
    assert "tiene_promo" in matched.columns
    assert "promo_nombre" in matched.columns


def test_compute_price_comparison(nino_detalle, sepa_processed, vtex_promos):
    """Debe generar tabla de comparacion completa."""
    nino = load_nino_products(nino_detalle)
    comparison = compute_price_comparison(nino, sepa_processed, vtex_promos)
    assert len(comparison) > 0
    assert "nino_precio_promedio" in comparison.columns
    assert "cadena" in comparison.columns


def test_load_nino_products_no_divide_by_zero_warning():
    """load_nino_products no debe emitir RuntimeWarning divide by zero
    cuando hay filas con cantidad=0 o cantidad<0 en los datos crudos.
    """
    dirty = pd.DataFrame({
        "codigo_barras": [
            "7790001234567", "7790001234567",
            "7790002345678",  # Solo filas con cantidad=0
            "7790002345678",
            "7790003456789",  # Solo devolucion (cantidad<0)
            "CAM NINO",  # codigo no-EAN
            None,  # NaN EAN
        ],
        "descripcion": ["LECHE"] * 2 + ["COCA"] * 2 + ["PAN", "CAM", "X"],
        "marca": ["LS"] * 2 + ["CC"] * 2 + ["BIMBO", "NINO", "X"],
        "categoria": ["LACT"] * 2 + ["BEB"] * 2 + ["PAN", "TEXTIL", "X"],
        "precio_unitario": [1200.0, 1250.0, 2000.0, 2050.0, 1500.0, 500.0, 100.0],
        "cantidad": [2, 3, 0, 0, -2, 1, 1],
        "importe_total": [2400.0, 3750.0, 0.0, 0.0, -3000.0, 500.0, 100.0],
    })

    with warnings.catch_warnings():
        warnings.simplefilter("error", RuntimeWarning)
        result = load_nino_products(dirty)

    # Solo leche debe pasar el filtro (unica con EAN valido + cantidad>0 + precio>0)
    assert len(result) == 1
    assert result.iloc[0]["ean"] == "7790001234567"
    # Precio ponderado: (1200*2 + 1250*3) / 5 = 1230
    assert result.iloc[0]["nino_precio_promedio"] == pytest.approx(1230.0, abs=0.01)
