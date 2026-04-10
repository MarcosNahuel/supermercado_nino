"""Tests para el modulo de auditoria de datos competitivos."""
import pytest
import pandas as pd
import numpy as np

from src.competitive.data_quality import (
    validate_ean_format,
    filter_valid_nino_rows,
    detect_price_anomalies,
    audit_comparison,
)


@pytest.fixture
def raw_nino_df():
    """Simula detalle_lineas con mix de filas validas e invalidas."""
    return pd.DataFrame({
        "codigo_barras": [
            "7790001234567",   # EAN-13 valido
            "7790001234567",   # EAN-13 valido (duplicado, venta normal)
            "CAM 45X60 NINO",  # Codigo interno, no EAN
            "1234",            # Muy corto
            None,              # NaN
            "7790002345678",   # EAN-13 valido pero cantidad=0
            "7790003456789",   # EAN-13 valido pero cantidad negativa (devolucion)
            "7790004567890",   # EAN-13 valido pero precio negativo
            "12345678",        # EAN-8 valido
        ],
        "descripcion": ["LECHE", "LECHE", "CAMISETA", "X", "Y", "COCA", "PAN", "AGUA", "GALLETA"],
        "precio_unitario": [1200.0, 1250.0, 500.0, 100.0, 200.0, 2000.0, 1500.0, -800.0, 900.0],
        "cantidad": [2, 3, 1, 1, 1, 0, -1, 1, 2],
    })


# ===== validate_ean_format =====

def test_validate_ean_accepts_ean13():
    """EAN-13 standard (13 digitos) es valido."""
    assert validate_ean_format("7790001234567") is True


def test_validate_ean_accepts_ean8():
    """EAN-8 (8 digitos) es valido."""
    assert validate_ean_format("12345678") is True


def test_validate_ean_rejects_short_code():
    """Codigo menos de 8 digitos es invalido."""
    assert validate_ean_format("1234") is False


def test_validate_ean_rejects_alphanumeric():
    """Codigos con letras no son EAN."""
    assert validate_ean_format("CAM 45X60 NINO") is False


def test_validate_ean_rejects_empty():
    """String vacio no es EAN."""
    assert validate_ean_format("") is False


def test_validate_ean_rejects_none():
    """None no es EAN."""
    assert validate_ean_format(None) is False


def test_validate_ean_rejects_nan():
    """NaN no es EAN."""
    assert validate_ean_format(float("nan")) is False


def test_validate_ean_handles_whitespace():
    """EAN con espacios alrededor debe ser valido tras strip."""
    assert validate_ean_format(" 7790001234567 ") is True


def test_validate_ean_rejects_decimal():
    """Numero con decimal no es EAN."""
    assert validate_ean_format("7790001234567.0") is False


# ===== filter_valid_nino_rows =====

def test_filter_removes_non_ean_codes(raw_nino_df):
    """Debe eliminar filas con codigos no-EAN (ej: 'CAM 45X60 NINO')."""
    result = filter_valid_nino_rows(raw_nino_df)
    assert "CAM 45X60 NINO" not in result["codigo_barras"].values
    assert "1234" not in result["codigo_barras"].values


def test_filter_removes_nan_ean(raw_nino_df):
    """Debe eliminar filas con EAN NaN/None."""
    result = filter_valid_nino_rows(raw_nino_df)
    assert result["codigo_barras"].isna().sum() == 0


def test_filter_removes_zero_quantity(raw_nino_df):
    """Debe eliminar filas con cantidad=0 (causan divide by zero)."""
    result = filter_valid_nino_rows(raw_nino_df)
    assert (result["cantidad"] == 0).sum() == 0


def test_filter_removes_negative_quantity(raw_nino_df):
    """Debe eliminar devoluciones (cantidad<0)."""
    result = filter_valid_nino_rows(raw_nino_df)
    assert (result["cantidad"] < 0).sum() == 0


def test_filter_removes_negative_price(raw_nino_df):
    """Debe eliminar filas con precio<=0."""
    result = filter_valid_nino_rows(raw_nino_df)
    assert (result["precio_unitario"] <= 0).sum() == 0


def test_filter_keeps_valid_rows(raw_nino_df):
    """Debe conservar filas con EAN valido + cantidad>0 + precio>0."""
    result = filter_valid_nino_rows(raw_nino_df)
    # 2 filas de leche + 1 galleta EAN-8 = 3 filas validas
    assert len(result) == 3
    assert set(result["codigo_barras"]) == {"7790001234567", "12345678"}


def test_filter_empty_df_returns_empty():
    """DataFrame vacio debe retornar vacio sin error."""
    empty = pd.DataFrame({"codigo_barras": [], "precio_unitario": [], "cantidad": []})
    result = filter_valid_nino_rows(empty)
    assert len(result) == 0


# ===== detect_price_anomalies =====

@pytest.fixture
def comparison_with_anomalies():
    """Comparison con filas normales y anomalias."""
    return pd.DataFrame({
        "ean": [
            "7790001234567",  # Normal: -5%
            "7790002345678",  # Normal: +10%
            "7790003456789",  # Anomalia: diff > 80% (precio mercado muy bajo)
            "7790004567890",  # Anomalia: diff < -80% (precio mercado muy alto)
            "7790005678901",  # Anomalia: NaN en diferencia
            "7790006789012",  # Anomalia: Inf en diferencia
            "7790007890123",  # Anomalia: precio NINO 0
            "7790008901234",  # Anomalia: precio mercado 0
        ],
        "nino_precio_promedio": [1000.0, 2000.0, 100.0, 5000.0, 1500.0, 3000.0, 0.0, 1200.0],
        "precio_promedio":      [1050.0, 1818.0, 20.0,  1000.0, float("nan"), 1.0, 500.0, 0.0],
        "diferencia_pct":       [-5.0,   10.0,  400.0,  -80.1,  float("nan"), float("inf"), -100.0, float("inf")],
    })


def test_detect_anomalies_returns_dataframe(comparison_with_anomalies):
    """detect_price_anomalies retorna DataFrame con columna 'motivo'."""
    result = detect_price_anomalies(comparison_with_anomalies)
    assert isinstance(result, pd.DataFrame)
    assert "motivo" in result.columns


def test_detect_anomalies_flags_extreme_diff(comparison_with_anomalies):
    """Debe flaggear filas con |diferencia_pct| > 80."""
    result = detect_price_anomalies(comparison_with_anomalies)
    flagged_eans = set(result["ean"])
    assert "7790003456789" in flagged_eans
    assert "7790004567890" in flagged_eans


def test_detect_anomalies_flags_nan(comparison_with_anomalies):
    """Debe flaggear NaN en diferencia_pct."""
    result = detect_price_anomalies(comparison_with_anomalies)
    assert "7790005678901" in set(result["ean"])


def test_detect_anomalies_flags_inf(comparison_with_anomalies):
    """Debe flaggear Inf en diferencia_pct."""
    result = detect_price_anomalies(comparison_with_anomalies)
    assert "7790006789012" in set(result["ean"])


def test_detect_anomalies_flags_zero_prices(comparison_with_anomalies):
    """Debe flaggear precios en cero."""
    result = detect_price_anomalies(comparison_with_anomalies)
    flagged_eans = set(result["ean"])
    assert "7790007890123" in flagged_eans
    assert "7790008901234" in flagged_eans


def test_detect_anomalies_excludes_normal_rows(comparison_with_anomalies):
    """Filas normales (diff pequeno, precios validos) no aparecen."""
    result = detect_price_anomalies(comparison_with_anomalies)
    flagged_eans = set(result["ean"])
    assert "7790001234567" not in flagged_eans
    assert "7790002345678" not in flagged_eans


def test_detect_anomalies_empty_df_returns_empty():
    """DataFrame vacio retorna vacio."""
    empty = pd.DataFrame({
        "ean": [], "nino_precio_promedio": [],
        "precio_promedio": [], "diferencia_pct": [],
    })
    result = detect_price_anomalies(empty)
    assert len(result) == 0


# ===== audit_comparison =====

def test_audit_returns_structured_report(comparison_with_anomalies):
    """audit_comparison retorna dict con claves esperadas."""
    report = audit_comparison(comparison_with_anomalies)
    assert isinstance(report, dict)
    assert "total_rows" in report
    assert "n_valid" in report
    assert "n_anomalies" in report
    assert "pct_valid" in report
    assert "anomalies" in report
    assert "eans_unicos" in report


def test_audit_counts_valid_and_anomalies(comparison_with_anomalies):
    """Counts deben reflejar el total y cuantas son anomalas."""
    report = audit_comparison(comparison_with_anomalies)
    assert report["total_rows"] == 8
    assert report["n_anomalies"] == 6  # 3 anomalias diff + 1 nan + 1 inf + 1 zero_nino + 1 zero_mkt = wait let's count: ean3 (diff 400), ean4 (diff -80.1), ean5 (nan), ean6 (inf), ean7 (nino=0), ean8 (mkt=0) = 6
    assert report["n_valid"] == 2


def test_audit_computes_pct_valid(comparison_with_anomalies):
    """pct_valid debe ser n_valid / total_rows * 100."""
    report = audit_comparison(comparison_with_anomalies)
    assert report["pct_valid"] == pytest.approx(25.0, abs=0.1)  # 2/8


def test_audit_anomalies_is_dataframe(comparison_with_anomalies):
    """El campo 'anomalies' debe ser un DataFrame con motivos."""
    report = audit_comparison(comparison_with_anomalies)
    assert isinstance(report["anomalies"], pd.DataFrame)
    assert "motivo" in report["anomalies"].columns


def test_audit_empty_returns_zero_counts():
    """DataFrame vacio retorna counts en cero."""
    empty = pd.DataFrame({
        "ean": [], "nino_precio_promedio": [],
        "precio_promedio": [], "diferencia_pct": [],
    })
    report = audit_comparison(empty)
    assert report["total_rows"] == 0
    assert report["n_valid"] == 0
    assert report["n_anomalies"] == 0
    assert report["pct_valid"] == 0.0
