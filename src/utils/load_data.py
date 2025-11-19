"""Utility functions to load raw data for the Supermercado NINO analytics pipeline."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import pandas as pd


def load_sales_data(
    sales_path: Path,
    *,
    sep: str = ";",
    decimal: str = ",",
    encoding: str = "utf-8",
    low_memory: bool = False,
) -> pd.DataFrame:
    """Load the main sales dataset."""
    if not sales_path.exists():
        raise FileNotFoundError(f"Sales file not found: {sales_path}")
    return pd.read_csv(
        sales_path,
        sep=sep,
        decimal=decimal,
        encoding=encoding,
        low_memory=low_memory,
    )


def load_rentabilidad_data(rentabilidad_path: Path) -> pd.DataFrame:
    """Load rentabilidad dataset with margin by department."""
    if not rentabilidad_path.exists():
        raise FileNotFoundError(f"Rentabilidad file not found: {rentabilidad_path}")
    df = pd.read_csv(rentabilidad_path, encoding="utf-8", decimal=",")

    rename_map: dict[str, str] = {}
    if "Clasificación" in df.columns:
        rename_map["Clasificación"] = "Clasificacion"
    if "Clasificaci�n" in df.columns:
        rename_map["Clasificaci�n"] = "Clasificacion"
    if "% Rentabilidad" in df.columns:
        rename_map["% Rentabilidad"] = "Rentabilidad"
    df = df.rename(columns=rename_map)

    df["Departamento"] = df["Departamento"].astype(str).str.strip().str.upper()
    df["Clasificacion"] = df.get("Clasificacion", "").astype(str).str.strip()

    rent_col = "Rentabilidad" if "Rentabilidad" in df.columns else "% Rentabilidad"
    if df[rent_col].dtype == object:
        df["rentabilidad_pct"] = (
            df[rent_col].str.replace("%", "", regex=False).astype(float)
        )
    else:
        df["rentabilidad_pct"] = df[rent_col]
    return df


def load_feriados(feriados_path: Path) -> pd.DataFrame:
    """Load holiday calendar from CSV."""
    if not feriados_path.exists():
        raise FileNotFoundError(f"Feriados file not found: {feriados_path}")
    feriados = pd.read_csv(
        feriados_path,
        sep=";",
        encoding="utf-8",
    )
    rename_map = {}
    if "Fecha" in feriados.columns:
        rename_map["Fecha"] = "fecha"
    if "Descripcion" in feriados.columns:
        rename_map["Descripcion"] = "descripcion"
    feriados = feriados.rename(columns=rename_map)
    if "fecha" not in feriados.columns:
        raise ValueError("El archivo de feriados no contiene la columna 'fecha'.")
    feriados["fecha"] = pd.to_datetime(feriados["fecha"], errors="coerce")
    feriados = feriados[feriados["fecha"].notna()].copy()
    feriados["descripcion"] = feriados.get("descripcion", "").astype(str).str.strip()
    return feriados


def ensure_directory(path: Path) -> None:
    """Create directory if it does not exist."""
    path.mkdir(parents=True, exist_ok=True)


def safe_merge(
    left: pd.DataFrame,
    right: pd.DataFrame,
    *,
    on: str,
    how: str = "left",
    suffixes: tuple[str, str] = ("", "_right"),
    validate: Optional[str] = None,
) -> pd.DataFrame:
    """Wrapper around pandas merge with clearer defaults."""
    return left.merge(right, on=on, how=how, suffixes=suffixes, validate=validate)
