"""Tests para el motor de insights competitivos."""
import pytest
import pandas as pd

from src.competitive.insights_engine import (
    compute_position_by_category,
    find_promo_opportunities,
    generate_digest_report,
)


@pytest.fixture
def comparison_df():
    """DataFrame de comparacion NINO vs competencia."""
    return pd.DataFrame({
        "ean": ["7790001234567"] * 3 + ["7790002345678"] * 2,
        "descripcion": ["LECHE ENTERA 1L"] * 3 + ["COCA COLA 2.25L"] * 2,
        "marca": ["LA SERENISIMA"] * 3 + ["COCA COLA"] * 2,
        "categoria": ["LACTEOS"] * 3 + ["BEBIDAS"] * 2,
        "cadena": ["CARREFOUR", "CHANGOMAS", "JUMBO", "CARREFOUR", "DISCO"],
        "nino_precio_promedio": [1200, 1200, 1200, 2000, 2000],
        "precio_promedio": [1300, 1280, 1250, 1890, 2100],
        "diferencia_pct": [-7.7, -6.3, -4.0, 5.8, -4.8],
        "tiene_promo": [False, True, False, True, False],
        "promo_nombre": ["", "2da al 50%", "", "3x2", ""],
        "fuente": ["SEPA", "SEPA", "SEPA", "VTEX", "SEPA"],
    })


def test_position_by_category(comparison_df):
    """Debe calcular posicion competitiva por categoria."""
    position = compute_position_by_category(comparison_df)
    assert "LACTEOS" in position["categoria"].values
    assert "BEBIDAS" in position["categoria"].values
    # LACTEOS: NINO es mas barato en promedio
    lacteos = position[position["categoria"] == "LACTEOS"].iloc[0]
    assert lacteos["posicion"] == "COMPETITIVO"


def test_find_promo_opportunities(comparison_df):
    """Debe encontrar oportunidades de promo basadas en competencia."""
    opps = find_promo_opportunities(comparison_df)
    assert len(opps) > 0
    # Coca Cola: competencia tiene 3x2, NINO es mas caro -> oportunidad
    coca = opps[opps["ean"] == "7790002345678"]
    assert len(coca) > 0


def test_generate_digest_report(comparison_df):
    """Debe generar reporte digerido con secciones."""
    report = generate_digest_report(comparison_df)
    assert "resumen" in report
    assert "productos_oportunidad" in report
    assert "promos_competencia" in report
    assert "sugerencias" in report
    assert isinstance(report["resumen"], dict)
    assert isinstance(report["productos_oportunidad"], pd.DataFrame)
