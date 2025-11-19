# -*- coding: utf-8 -*-
"""
===============================================================================
Genera el paquete ligero de datos para la app Streamlit
-------------------------------------------------------------------------------
Lee los CSV procesados en data/processed/FASE1_OUTPUT y exporta únicamente
los dataframes necesarios en formato Parquet a data/app_dataset/.

Se excluye 01_ITEMS_VENTAS.csv para evitar archivos >100 MB en el repositorio.
===============================================================================
"""

from pathlib import Path

import pandas as pd


PROCESSED_DIR = Path("data/processed/FASE1_OUTPUT")
TARGET_DIR = Path("data/app_dataset")

FILE_MAPPING = {
    "kpi_periodo": "03_KPI_PERIODO.csv",
    "kpi_categoria": "04_KPI_CATEGORIA.csv",
    "kpi_dia": "08_KPI_DIA_SEMANA.csv",
    "pareto": "05_PARETO_PRODUCTOS.csv",
    "clusters": "07_PERFILES_CLUSTERS.csv",
    "reglas": "06_REGLAS_ASOCIACION.csv",
    "tickets": "02_TICKETS.csv",
}


def export_parquet():
    if not PROCESSED_DIR.exists():
        raise SystemExit(f"No se encontró {PROCESSED_DIR}. Ejecuta primero FASE1_ANALISIS_COMPLETO.py")

    TARGET_DIR.mkdir(parents=True, exist_ok=True)

    for key, filename in FILE_MAPPING.items():
        source = PROCESSED_DIR / filename
        if not source.exists():
            print(f"[WARN] No se encontró {source.name}; se omitirá {key}.")
            continue

        df = pd.read_csv(source, sep=";", encoding="utf-8-sig")

        if key == "tickets" and "fecha" in df.columns:
            df["fecha"] = pd.to_datetime(df["fecha"])

        target = TARGET_DIR / f"{key}.parquet"
        df.to_parquet(target, index=False)
        print(f"[OK] {target.relative_to(Path('.'))}")


if __name__ == "__main__":
    export_parquet()
