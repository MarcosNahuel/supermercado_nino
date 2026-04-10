"""Motor de insights competitivos — genera informes digeridos para el cliente.

Principio: "Nosotros tenemos que mandar la informacion ya digerida"
— Sebastian, cliente NINO.
"""
import logging
from datetime import datetime

import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)


def compute_position_by_category(comparison_df: pd.DataFrame) -> pd.DataFrame:
    """Calcula posicion competitiva de NINO por categoria.

    Para cada categoria:
    - COMPETITIVO: NINO es mas barato que el promedio de mercado (diff < -2%)
    - PAR: NINO esta en rango similar al mercado (-2% a +2%)
    - CARO: NINO es mas caro que el mercado (diff > +2%)

    Returns:
        DataFrame con: categoria, diff_promedio, posicion, n_productos, n_cadenas
    """
    by_cat = (
        comparison_df
        .groupby("categoria")
        .agg(
            diff_promedio=("diferencia_pct", "mean"),
            diff_mediana=("diferencia_pct", "median"),
            n_productos=("ean", "nunique"),
            n_cadenas=("cadena", "nunique"),
            n_promos_competencia=("tiene_promo", "sum"),
        )
        .reset_index()
    )

    by_cat["diff_promedio"] = by_cat["diff_promedio"].round(1)
    by_cat["diff_mediana"] = by_cat["diff_mediana"].round(1)

    def classify(diff):
        if diff < -2:
            return "COMPETITIVO"
        elif diff > 2:
            return "CARO"
        return "PAR"

    by_cat["posicion"] = by_cat["diff_promedio"].apply(classify)

    return by_cat.sort_values("diff_promedio")


def find_promo_opportunities(comparison_df: pd.DataFrame) -> pd.DataFrame:
    """Identifica oportunidades de promo para NINO.

    Criterios:
    1. Productos donde la competencia tiene promo activa
    2. Productos donde NINO es mas caro que el mercado
    3. Productos de alto volumen de venta en NINO

    Returns:
        DataFrame con oportunidades rankeadas por impacto potencial.
    """
    # Productos con promos en la competencia
    with_promos = comparison_df[comparison_df["tiene_promo"]].copy()

    if with_promos.empty:
        return pd.DataFrame()

    # Agregar por producto: cuantas cadenas tienen promo
    opp = (
        with_promos
        .groupby(["ean", "descripcion", "marca", "categoria"])
        .agg(
            cadenas_con_promo=("cadena", "nunique"),
            promos_activas=("promo_nombre", lambda x: " | ".join(x.unique())),
            nino_precio=("nino_precio_promedio", "first"),
            precio_mercado_min=("precio_promedio", "min"),
            diff_pct_promedio=("diferencia_pct", "mean"),
        )
        .reset_index()
    )

    # Score de oportunidad: mas cadenas con promo + NINO caro = mayor oportunidad
    opp["score_oportunidad"] = (
        opp["cadenas_con_promo"] * 30
        + opp["diff_pct_promedio"].clip(lower=0) * 5
    ).round(0).astype(int)

    opp = opp.sort_values("score_oportunidad", ascending=False)

    logger.info(f"Oportunidades de promo: {len(opp)} productos")
    return opp


def _suggest_promo_type(row: pd.Series) -> str:
    """Sugiere tipo de promo basado en contexto."""
    promos = str(row.get("promos_activas", "")).lower()
    diff = row.get("diff_pct_promedio", 0)

    if "2da" in promos or "segunda" in promos:
        return "2da unidad al 50% — la competencia ya lo hace, igualar"
    if "3x2" in promos:
        return "3x2 o 2da al 70% — la competencia tiene 3x2"
    if diff > 5:
        return "Descuento directo 10-15% — NINO esta caro en este producto"
    if diff > 0:
        return "Combo con producto complementario — mantener margen"
    return "Promo por volumen — NINO ya es competitivo, incentivar compra multiple"


def generate_digest_report(comparison_df: pd.DataFrame) -> dict:
    """Genera el informe digerido completo.

    Estructura del reporte:
    - resumen: metricas globales
    - posicion_categorias: tabla de posicion competitiva
    - productos_oportunidad: top productos donde actuar
    - promos_competencia: promos activas de la competencia
    - sugerencias: recomendaciones accionables

    Returns:
        Dict con secciones del reporte.
    """
    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    # 1. Resumen global
    n_productos = comparison_df["ean"].nunique()
    n_cadenas = comparison_df["cadena"].nunique()
    diff_global = comparison_df["diferencia_pct"].mean()
    pct_competitivo = (comparison_df["diferencia_pct"] < 0).mean() * 100
    n_promos = comparison_df["tiene_promo"].sum()

    resumen = {
        "fecha": now,
        "productos_comparados": n_productos,
        "cadenas_analizadas": n_cadenas,
        "diferencia_precio_promedio": round(diff_global, 1),
        "pct_productos_competitivos": round(pct_competitivo, 1),
        "promos_activas_competencia": int(n_promos),
    }

    # 2. Posicion por categoria
    posicion = compute_position_by_category(comparison_df)

    # 3. Oportunidades
    oportunidades = find_promo_opportunities(comparison_df)
    if not oportunidades.empty:
        oportunidades["sugerencia"] = oportunidades.apply(_suggest_promo_type, axis=1)

    # 4. Promos de la competencia (tabla cruda filtrada)
    promos = comparison_df[comparison_df["tiene_promo"]].copy()
    promos = promos.sort_values("cadena")

    # 5. Sugerencias top
    sugerencias = []
    if not oportunidades.empty:
        for _, row in oportunidades.head(5).iterrows():
            sugerencias.append({
                "producto": row["descripcion"],
                "ean": row["ean"],
                "categoria": row["categoria"],
                "contexto": f"{int(row['cadenas_con_promo'])} cadena(s) con promo activa",
                "accion": row.get("sugerencia", "Evaluar descuento"),
                "promos_competencia": row["promos_activas"],
            })

    # Agregar sugerencias por categoria cara
    cats_caras = posicion[posicion["posicion"] == "CARO"]
    for _, cat in cats_caras.iterrows():
        sugerencias.append({
            "producto": f"CATEGORIA: {cat['categoria']}",
            "ean": "",
            "categoria": cat["categoria"],
            "contexto": f"NINO es {cat['diff_promedio']}% mas caro que el mercado",
            "accion": "Revisar margenes o lanzar promo general en la categoria",
            "promos_competencia": f"{int(cat['n_promos_competencia'])} promos activas en competencia",
        })

    logger.info(
        f"Reporte generado: {n_productos} productos, "
        f"{len(sugerencias)} sugerencias"
    )

    return {
        "resumen": resumen,
        "posicion_categorias": posicion,
        "productos_oportunidad": oportunidades,
        "promos_competencia": promos,
        "sugerencias": sugerencias,
    }
