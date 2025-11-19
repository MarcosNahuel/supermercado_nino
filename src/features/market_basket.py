"""Market basket analysis utilities."""

from __future__ import annotations

from pathlib import Path
from typing import Dict

import numpy as np
import pandas as pd
from mlxtend.frequent_patterns import apriori, association_rules
from mlxtend.preprocessing import TransactionEncoder

from src.utils.load_data import ensure_directory


def _select_relevant_products(detalle: pd.DataFrame) -> pd.DataFrame:
    """Reduce dimensionality keeping high-impact products."""
    detalle = detalle.copy()
    detalle["descripcion"] = detalle["descripcion"].str.upper()

    keywords = ["COCA", "FERNET", "VINO", "CARNE"]
    mask_keywords = detalle["descripcion"].str.contains("|".join(keywords), na=False)
    productos_keywords = detalle[mask_keywords]["producto_id"].unique().tolist()

    top_por_importe = (
        detalle.groupby("producto_id")["importe_total"].sum().nlargest(200).index.tolist()
    )

    productos_clave = list(set(productos_keywords + top_por_importe))
    if not productos_clave:
        productos_clave = top_por_importe
    return detalle[detalle["producto_id"].isin(productos_clave)].copy()


def run_market_basket(
    detalle: pd.DataFrame,
    output_dir: Path,
    *,
    min_support: float = 0.005,
    min_confidence: float = 0.15,
    min_lift: float = 1.0,
    sample_tickets: int = 25000,
) -> Dict[str, Path]:
    ensure_directory(output_dir)
    filtered = _select_relevant_products(detalle)

    tickets = filtered.groupby("ticket_id")["producto_id"].nunique()
    tickets_validos = tickets[tickets >= 2].index
    if tickets_validos.empty:
        return {}

    rng = np.random.default_rng(seed=42)
    if len(tickets_validos) > sample_tickets:
        sample_ids = rng.choice(tickets_validos, size=sample_tickets, replace=False)
    else:
        sample_ids = tickets_validos

    df_sample = filtered[filtered["ticket_id"].isin(sample_ids)]
    transacciones = df_sample.groupby("ticket_id")["descripcion"].apply(list).tolist()
    if not transacciones:
        return {}

    encoder = TransactionEncoder()
    encoded = encoder.fit(transacciones).transform(transacciones)
    basket_matrix = pd.DataFrame(encoded, columns=encoder.columns_)

    frequent_itemsets = apriori(basket_matrix, min_support=min_support, use_colnames=True)
    if frequent_itemsets.empty:
        return {}

    rules = association_rules(
        frequent_itemsets, metric="confidence", min_threshold=min_confidence
    )
    rules = rules[rules["lift"] >= min_lift].sort_values("lift", ascending=False)
    if rules.empty:
        return {}

    export_paths: Dict[str, Path] = {}

    rules_export = rules.copy()
    rules_export["antecedents"] = rules_export["antecedents"].apply(
        lambda x: ", ".join(list(x))
    )
    rules_export["consequents"] = rules_export["consequents"].apply(
        lambda x: ", ".join(list(x))
    )
    export_paths["reglas"] = output_dir / "reglas.parquet"
    rules_export.to_parquet(export_paths["reglas"], index=False)

    adjacency = rules[rules["antecedents"].apply(len) == 1].copy()
    adjacency["antecedent"] = adjacency["antecedents"].apply(lambda x: list(x)[0])
    adjacency["consequent"] = adjacency["consequents"].apply(lambda x: list(x)[0])
    adjacency = adjacency[["antecedent", "consequent", "support", "confidence", "lift"]]
    adjacency = adjacency.nlargest(50, "lift")
    if not adjacency.empty:
        export_paths["adjacency_pairs"] = output_dir / "adjacency_pairs.parquet"
        adjacency.to_parquet(export_paths["adjacency_pairs"], index=False)

    combos = rules.nlargest(20, "lift").copy()
    combos["antecedent"] = combos["antecedents"].apply(lambda x: ", ".join(list(x)))
    combos["consequent"] = combos["consequents"].apply(lambda x: ", ".join(list(x)))

    precio_map = df_sample.groupby("descripcion")["precio_unitario"].mean().to_dict()
    margen_pct_map = df_sample.groupby("descripcion")["rentabilidad_pct"].mean().to_dict()

    def _precio_combo(row: pd.Series) -> float:
        items = list(row["antecedents"]) + list(row["consequents"])
        return float(sum(precio_map.get(item, 0.0) for item in items))

    def _margen_combo(row: pd.Series) -> float:
        items = list(row["antecedents"]) + list(row["consequents"])
        valores = [margen_pct_map.get(item, 18.0) for item in items]
        return float(np.mean(valores)) if valores else 18.0

    combos["precio_combo_sugerido"] = combos.apply(_precio_combo, axis=1) * 0.9
    combos["margen_combo_estimado"] = combos.apply(_margen_combo, axis=1)
    combos["adopcion_objetivo_pct"] = 2.0
    export_paths["combos_recomendados"] = output_dir / "combos_recomendados.parquet"
    combos[
        [
            "antecedent",
            "consequent",
            "support",
            "confidence",
            "lift",
            "precio_combo_sugerido",
            "margen_combo_estimado",
            "adopcion_objetivo_pct",
        ]
    ].to_parquet(export_paths["combos_recomendados"], index=False)

    return export_paths

