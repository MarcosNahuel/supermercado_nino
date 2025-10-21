"""Pareto analysis on margin contribution by category and product."""

from __future__ import annotations

from pathlib import Path
from typing import Dict

import pandas as pd

from src.utils.load_data import ensure_directory


def _pareto(df: pd.DataFrame, value_col: str, id_col: str) -> pd.DataFrame:
    ordered = (
        df.groupby(id_col)[value_col]
        .sum()
        .sort_values(ascending=False)
        .reset_index()
    )
    ordered["participacion"] = ordered[value_col] / ordered[value_col].sum()
    ordered["participacion_acumulada"] = ordered["participacion"].cumsum()

    def clasifica(row: pd.Series) -> str:
        if row["participacion_acumulada"] <= 0.8:
            return "A"
        if row["participacion_acumulada"] <= 0.95:
            return "B"
        return "C"

    ordered["segmento_pareto"] = ordered.apply(clasifica, axis=1)
    return ordered


def run_pareto(detalle: pd.DataFrame, output_dir: Path) -> Dict[str, Path]:
    ensure_directory(output_dir)
    categoria = _pareto(detalle, "margen_linea", "categoria")
    producto = _pareto(detalle, "margen_linea", "descripcion")

    paths = {
        "pareto_categoria": output_dir / "pareto_categoria.parquet",
        "pareto_producto": output_dir / "pareto_producto.parquet",
    }
    categoria.to_parquet(paths["pareto_categoria"], index=False)
    producto.to_parquet(paths["pareto_producto"], index=False)
    return paths

