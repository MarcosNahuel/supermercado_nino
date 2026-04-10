"""Auditoria de calidad de datos para el modulo competitivo.

Valida integridad de EANs, detecta anomalias de precio y genera
reportes de calidad sobre la data cruzada NINO vs competencia.
"""
import math
import re

import pandas as pd


_EAN_PATTERN = re.compile(r"^\d{8,14}$")


def validate_ean_format(value) -> bool:
    """Valida que el valor sea un EAN numerico de 8 a 14 digitos.

    Acepta EAN-8, EAN-13 y EAN-14. Rechaza strings vacios, None, NaN,
    alfanumericos y numeros con decimales.
    """
    if value is None:
        return False
    if isinstance(value, float) and math.isnan(value):
        return False
    s = str(value).strip()
    return bool(_EAN_PATTERN.match(s))


def filter_valid_nino_rows(df: pd.DataFrame) -> pd.DataFrame:
    """Filtra el detalle de lineas NINO conservando solo filas auditables.

    Criterios:
    - codigo_barras con formato EAN numerico (8-14 digitos)
    - cantidad > 0 (descarta 0 y devoluciones negativas)
    - precio_unitario > 0 (descarta anulaciones negativas)

    Esta limpieza previa es necesaria antes del groupby ponderado para
    evitar divide-by-zero y contaminacion con codigos internos NINO.
    """
    if df.empty:
        return df.copy()

    mask = (
        df["codigo_barras"].apply(validate_ean_format)
        & (df["cantidad"] > 0)
        & (df["precio_unitario"] > 0)
    )
    return df[mask].copy()


ANOMALY_DIFF_PCT_THRESHOLD = 80.0


def detect_price_anomalies(comparison_df: pd.DataFrame) -> pd.DataFrame:
    """Detecta anomalias en una tabla de comparacion NINO vs competencia.

    Criterios de anomalia:
    - |diferencia_pct| > 80 (diferencia extrema, probable error de matching)
    - diferencia_pct NaN o Inf (division por cero o dato corrupto)
    - nino_precio_promedio <= 0 (precio invalido)
    - precio_promedio <= 0 (precio invalido)

    Returns:
        DataFrame con las filas problematicas y una columna 'motivo'
        describiendo la causa.
    """
    if comparison_df.empty:
        return comparison_df.assign(motivo="").iloc[0:0]

    df = comparison_df.copy()

    nino_price = df["nino_precio_promedio"]
    mkt_price = df["precio_promedio"]
    diff = df["diferencia_pct"]

    zero_nino = nino_price <= 0
    zero_mkt = mkt_price <= 0
    nan_diff = diff.isna()
    inf_diff = diff.apply(lambda x: isinstance(x, float) and math.isinf(x))
    extreme_diff = (~nan_diff) & (~inf_diff) & (diff.abs() > ANOMALY_DIFF_PCT_THRESHOLD)

    anomaly_mask = zero_nino | zero_mkt | nan_diff | inf_diff | extreme_diff
    flagged = df[anomaly_mask].copy()

    motivos = []
    for _, row in flagged.iterrows():
        reasons = []
        if row["nino_precio_promedio"] <= 0:
            reasons.append("nino_precio<=0")
        if row["precio_promedio"] <= 0:
            reasons.append("precio_mercado<=0")
        d = row["diferencia_pct"]
        if pd.isna(d):
            reasons.append("diferencia_nan")
        elif isinstance(d, float) and math.isinf(d):
            reasons.append("diferencia_inf")
        elif abs(d) > ANOMALY_DIFF_PCT_THRESHOLD:
            reasons.append(f"diferencia_extrema_{d:+.0f}pct")
        motivos.append("; ".join(reasons))

    flagged["motivo"] = motivos
    return flagged


def audit_comparison(comparison_df: pd.DataFrame) -> dict:
    """Ejecuta auditoria completa sobre la tabla de comparacion.

    Returns:
        Dict con metricas de calidad:
        - total_rows: filas totales
        - n_valid: filas sin anomalias
        - n_anomalies: filas anomalas
        - pct_valid: porcentaje de filas validas
        - eans_unicos: cantidad de EANs unicos
        - anomalies: DataFrame con las filas problematicas y motivos
    """
    total = len(comparison_df)
    anomalies = detect_price_anomalies(comparison_df)
    n_anomalies = len(anomalies)
    n_valid = total - n_anomalies
    pct_valid = (n_valid / total * 100) if total > 0 else 0.0

    eans_unicos = (
        int(comparison_df["ean"].nunique()) if "ean" in comparison_df.columns else 0
    )

    return {
        "total_rows": total,
        "n_valid": n_valid,
        "n_anomalies": n_anomalies,
        "pct_valid": round(pct_valid, 2),
        "eans_unicos": eans_unicos,
        "anomalies": anomalies,
    }
