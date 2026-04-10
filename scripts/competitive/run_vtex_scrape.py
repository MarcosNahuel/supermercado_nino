"""Scrapea promociones de cadenas VTEX."""
import sys
import logging
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.competitive.vtex_scraper import scrape_all_chains

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(message)s")
logger = logging.getLogger(__name__)


def main():
    logger.info("=== VTEX Scrape Start ===")

    result = scrape_all_chains()
    logger.info(
        f"Total: {len(result):,} productos, "
        f"{result['tiene_promo'].sum():,} con promo"
    )

    logger.info("=== VTEX Scrape Complete ===")


if __name__ == "__main__":
    main()
