"""Validaciones de consistencia sobre los datasets procesados."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Dict

import pandas as pd


logging.basicConfig(level=logging.INFO, format="%(message)s")
LOGGER = logging.getLogger("validacion")

BASE_DIR = Path(__file__).resolve().parent
PROCESSED_DIR = BASE_DIR / "data" / "processed"

TICKET_MIN = 25_000
TICKET_MAX = 30_000
TIPOS_DIA_ESPERADOS = {"HABIL", "FDS", "FERIADO"}


def _load_parquet(name: str) -> pd.DataFrame:
    path = PROCESSED_DIR / name
    if not path.exists():
        raise FileNotFoundError(f"No se encontró {path}")
    return pd.read_parquet(path)


def validar_suma_anual(kpi_dia: pd.DataFrame, tolerancia: float = 1.0) -> bool:
    anual_directo = kpi_dia.groupby("anio")["ventas_totales"].sum()
    mensual = (
        kpi_dia.assign(anio_mes=lambda df: df["anio"].astype(str) + "-" + df["mes"].astype(str).str.zfill(2))
        .groupby(["anio", "anio_mes"])["ventas_totales"]
        .sum()
        .groupby("anio")
        .sum()
    )
    diferencia = (anual_directo - mensual).abs().max()
    LOGGER.info("Diferencia max entre anual directo y mensual: %.2f", diferencia)
    return diferencia <= tolerancia


def validar_ticket_promedio(kpi_dia: pd.DataFrame) -> Dict[str, float]:
    promedio_global = kpi_dia["ticket_promedio"].mean()
    fuera_de_rango = kpi_dia[
        (kpi_dia["ticket_promedio"] < TICKET_MIN)
        | (kpi_dia["ticket_promedio"] > TICKET_MAX)
    ]
    porcentaje_fuera = len(fuera_de_rango) / len(kpi_dia) * 100 if len(kpi_dia) else 0.0
    LOGGER.info(
        "Ticket promedio global: %.2f | %0.2f%% dias fuera de rango (%d de %d)",
        promedio_global,
        porcentaje_fuera,
        len(fuera_de_rango),
        len(kpi_dia),
    )
    return {
        "promedio_global": promedio_global,
        "porcentaje_fuera": porcentaje_fuera,
    }


def validar_tipologias(kpi_tipo_dia: pd.DataFrame) -> bool:
    tipos_encontrados = set(kpi_tipo_dia["tipo_dia"].unique())
    desconocidos = tipos_encontrados - TIPOS_DIA_ESPERADOS
    if desconocidos:
        LOGGER.warning("Tipos de dia no esperados: %s", ", ".join(sorted(desconocidos)))
        return False
    LOGGER.info("Tipos de dia validados: %s", ", ".join(sorted(tipos_encontrados)))
    return True


def main() -> None:
    LOGGER.info("Iniciando validaciones de informes")
    kpi_dia = _load_parquet("kpi_dia.parquet")
    kpi_tipo_dia = _load_parquet("kpi_tipo_dia.parquet")

    if validar_suma_anual(kpi_dia):
        LOGGER.info("OK: la suma mensual concuerda con el total anual.")
    else:
        LOGGER.error("ERROR: discrepancia detectada en la suma mensual vs anual.")

    ticket_stats = validar_ticket_promedio(kpi_dia)
    if ticket_stats["porcentaje_fuera"] > 5.0:
        LOGGER.warning(
            "Mas del 5%% de los dias tienen ticket promedio fuera del rango [%d, %d].",
            TICKET_MIN,
            TICKET_MAX,
        )

    if validar_tipologias(kpi_tipo_dia):
        LOGGER.info("OK: Tipologias de dia consistentes.")

    LOGGER.info("Validaciones completadas")


if __name__ == "__main__":
    main()
