"""Descarga y procesa datos SEPA del dia."""
import sys
import logging
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.competitive.sepa_downloader import fetch_sepa_daily
from src.competitive.sepa_etl import run_sepa_etl
from src.competitive.config import SEPA_PROCESSED_DIR

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(message)s")
logger = logging.getLogger(__name__)


def main():
    logger.info("=== SEPA Update Start ===")

    # 1. Descargar datos del dia
    raw_df, date_str = fetch_sepa_daily()
    logger.info(f"Descargado: {len(raw_df):,} registros para {date_str}")

    # 2. Procesar
    processed = run_sepa_etl(raw_df, output_dir=SEPA_PROCESSED_DIR, date_str=date_str)
    logger.info(f"Procesado: {len(processed):,} registros")

    logger.info("=== SEPA Update Complete ===")


if __name__ == "__main__":
    main()
