"""Main orchestrator for the modular analytics pipeline."""

from __future__ import annotations

import logging
from pathlib import Path

from src.data_prep.etl_basico import run_etl
from src.features.clustering_tickets import run_ticket_clustering
from src.features.kpis_basicos import (
    build_kpi_categoria,
    build_kpi_dia,
    build_kpi_medio_pago,
    build_kpi_tipo_dia,
    export_kpis,
)
from src.features.market_basket import run_market_basket
from src.features.pareto_margen import run_pareto
from src.features.predictivos_ventas_simple import generate_forecasts
from src.utils.load_data import (
    ensure_directory,
    load_feriados,
    load_rentabilidad_data,
    load_sales_data,
)


logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
LOGGER = logging.getLogger("main_pipeline")


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
PREDICTIVE_DIR = DATA_DIR / "predictivos"

SALES_FILE = RAW_DIR / "SERIE_COMPROBANTES_COMPLETOS.csv"
RENTABILIDAD_FILE = RAW_DIR / "RENTABILIDAD.csv"
FERIADOS_FILE = RAW_DIR / "FERIADOS_2024_2025.csv"


def main() -> None:
    LOGGER.info("Iniciando pipeline modular")

    ensure_directory(PROCESSED_DIR)
    ensure_directory(PREDICTIVE_DIR)

    LOGGER.info("Cargando datasets base")
    raw_sales = load_sales_data(SALES_FILE)
    rentabilidad = load_rentabilidad_data(RENTABILIDAD_FILE)
    feriados = load_feriados(FERIADOS_FILE)

    LOGGER.info("Ejecutando ETL principal")
    artifacts = run_etl(raw_sales, rentabilidad, feriados)

    detalle_path = PROCESSED_DIR / "detalle_lineas.parquet"
    tickets_path = PROCESSED_DIR / "tickets.parquet"
    ventas_semana_path = PROCESSED_DIR / "ventas_semanales_categoria.parquet"
    artifacts.detalle.to_parquet(detalle_path, index=False)
    artifacts.tickets.to_parquet(tickets_path, index=False)
    artifacts.ventas_semanales_categoria.to_parquet(ventas_semana_path, index=False)

    LOGGER.info("Calculando KPIs estandarizados")
    kpi_dia = build_kpi_dia(artifacts.ventas_diarias)
    kpi_tipo_dia = build_kpi_tipo_dia(kpi_dia)
    kpi_categoria = build_kpi_categoria(artifacts.detalle)
    kpi_medio_pago = build_kpi_medio_pago(artifacts.tickets)
    export_kpis(
        output_dir=PROCESSED_DIR,
        kpi_dia=kpi_dia,
        kpi_tipo_dia=kpi_tipo_dia,
        kpi_categoria=kpi_categoria,
        kpi_medio_pago=kpi_medio_pago,
    )

    LOGGER.info("Ejecutando market basket")
    run_market_basket(artifacts.detalle, PROCESSED_DIR)

    LOGGER.info("Calculando Pareto de margen")
    run_pareto(artifacts.detalle, PROCESSED_DIR)

    LOGGER.info("Clustering de tickets")
    run_ticket_clustering(artifacts.tickets, PROCESSED_DIR)

    LOGGER.info("Generando pronosticos semanales por categoria")
    generate_forecasts(artifacts.ventas_semanales_categoria, PREDICTIVE_DIR)

    LOGGER.info("Pipeline finalizado correctamente")


if __name__ == "__main__":
    main()
