"""Pipeline completo de inteligencia competitiva.

Ejecuta: SEPA download -> ETL -> VTEX scrape -> Match -> Insights -> Export.
"""
import sys
import logging
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.competitive.sepa_downloader import fetch_sepa_daily
from src.competitive.sepa_etl import run_sepa_etl
from src.competitive.vtex_scraper import scrape_all_chains
from src.competitive.product_matcher import load_nino_products, compute_price_comparison
from src.competitive.insights_engine import generate_digest_report
from src.competitive.config import SEPA_PROCESSED_DIR, INSIGHTS_DIR

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(message)s")
logger = logging.getLogger(__name__)


def main():
    logger.info("=== Full Competitive Intelligence Pipeline ===")

    # 1. SEPA
    logger.info("--- Paso 1/5: Descargando SEPA ---")
    try:
        raw_df, date_str = fetch_sepa_daily()
        sepa_df = run_sepa_etl(raw_df, output_dir=SEPA_PROCESSED_DIR, date_str=date_str)
        logger.info(f"SEPA: {len(sepa_df):,} registros procesados")
    except Exception as e:
        logger.warning(f"SEPA fallo: {e}. Continuando sin SEPA.")
        sepa_df = None

    # 2. VTEX
    logger.info("--- Paso 2/5: Scrapeando VTEX ---")
    try:
        vtex_df = scrape_all_chains()
        logger.info(f"VTEX: {len(vtex_df):,} productos scrapeados")
    except Exception as e:
        logger.warning(f"VTEX fallo: {e}. Continuando sin VTEX.")
        vtex_df = None

    if sepa_df is None and vtex_df is None:
        logger.error("No se pudo obtener datos de ninguna fuente. Abortando.")
        return

    # 3. Match
    logger.info("--- Paso 3/5: Matching con NINO ---")
    nino_df = load_nino_products()
    comparison = compute_price_comparison(nino_df, sepa_df, vtex_df)
    logger.info(f"Match: {len(comparison):,} cruces encontrados")

    # 4. Insights
    logger.info("--- Paso 4/5: Generando insights ---")
    report = generate_digest_report(comparison)

    # 5. Export
    logger.info("--- Paso 5/5: Exportando ---")
    INSIGHTS_DIR.mkdir(parents=True, exist_ok=True)

    comparison.to_parquet(INSIGHTS_DIR / "comparison_latest.parquet", index=False)
    report["posicion_categorias"].to_parquet(
        INSIGHTS_DIR / "posicion_categorias.parquet", index=False
    )
    if not report["productos_oportunidad"].empty:
        report["productos_oportunidad"].to_parquet(
            INSIGHTS_DIR / "oportunidades.parquet", index=False
        )

    r = report["resumen"]
    logger.info(
        f"\n{'='*60}\n"
        f"RESUMEN INTELIGENCIA COMPETITIVA - {r['fecha']}\n"
        f"  Productos comparados: {r['productos_comparados']:,}\n"
        f"  Cadenas analizadas: {r['cadenas_analizadas']}\n"
        f"  Diferencia precio promedio: {r['diferencia_precio_promedio']:+.1f}%\n"
        f"  % productos competitivos: {r['pct_productos_competitivos']:.0f}%\n"
        f"  Promos activas competencia: {r['promos_activas_competencia']}\n"
        f"  Sugerencias generadas: {len(report['sugerencias'])}\n"
        f"{'='*60}"
    )

    logger.info("=== Pipeline Complete ===")


if __name__ == "__main__":
    main()
