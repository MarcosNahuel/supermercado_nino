"""Ticket-level clustering using KMeans and silhouette search."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, Optional

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler

from src.utils.load_data import ensure_directory


@dataclass
class ClusteringResult:
    assignments: pd.DataFrame
    centroids: pd.DataFrame
    best_k: int
    silhouette: float


def _prepare_features(tickets: pd.DataFrame) -> pd.DataFrame:
    return tickets[
        [
            "ventas_totales",
            "margen_total",
            "unidades_totales",
            "productos_unicos",
        ]
    ].fillna(0.0)


def _find_best_k(
    data: np.ndarray, k_candidates: Iterable[int]
) -> tuple[int, float]:
    best_k = 0
    best_score = -1.0
    for k in k_candidates:
        if k >= data.shape[0]:
            continue
        model = KMeans(n_clusters=k, random_state=42, n_init="auto")
        labels = model.fit_predict(data)
        if len(set(labels)) < 2:
            continue
        score = silhouette_score(data, labels)
        if score > best_score:
            best_score = score
            best_k = k
    if best_k == 0:
        best_k = 3
        best_score = -1.0
    return best_k, best_score


def run_ticket_clustering(
    tickets: pd.DataFrame,
    output_dir: Path,
    *,
    k_values: Optional[Iterable[int]] = None,
) -> ClusteringResult:
    ensure_directory(output_dir)
    if k_values is None:
        k_values = range(3, 7)

    features = _prepare_features(tickets)
    scaler = StandardScaler()
    scaled = scaler.fit_transform(features)

    best_k, best_score = _find_best_k(scaled, k_values)
    model = KMeans(n_clusters=best_k, random_state=42, n_init="auto")
    labels = model.fit_predict(scaled)

    assignments = tickets.copy()
    assignments["cluster_ticket"] = labels

    centroids = pd.DataFrame(model.cluster_centers_, columns=features.columns)
    centroids = pd.DataFrame(scaler.inverse_transform(centroids), columns=features.columns)
    centroids["cluster_ticket"] = centroids.index

    assignments_path = output_dir / "clusters_tickets.parquet"
    centroids_path = output_dir / "clusters_tickets_centroides.parquet"

    assignments.to_parquet(assignments_path, index=False)
    centroids.to_parquet(centroids_path, index=False)

    return ClusteringResult(
        assignments=assignments,
        centroids=centroids,
        best_k=best_k,
        silhouette=best_score,
    )

