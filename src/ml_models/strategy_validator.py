"""Coordinator that runs every strategy simulator and collates ROI metrics."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Tuple

import pandas as pd

from src.utils.load_data import ensure_directory

from .combo_simulator import ComboSimulator
from .cross_sell_optimizer import CrossSellOptimizer
from .fidelizacion_simulator import FidelizacionSimulator
from .marca_propia_estimator import MarcaPropiaEstimator
from .ticket_predictor import TicketPredictor
from .upselling_detector import UpsellingDetector


@dataclass
class StrategyValidator:
    """High-level orchestrator for the ML-driven strategy ROI validation."""

    ticket_predictor: TicketPredictor = field(default_factory=TicketPredictor)
    combo_sim: ComboSimulator = field(default_factory=ComboSimulator)
    marca_propia_est: MarcaPropiaEstimator = field(default_factory=MarcaPropiaEstimator)
    upsell_det: UpsellingDetector = field(default_factory=UpsellingDetector)
    fidelizacion_sim: FidelizacionSimulator = field(default_factory=FidelizacionSimulator)

    def run_all_strategies(
        self,
        tickets: pd.DataFrame,
        detalle: pd.DataFrame,
        reglas: pd.DataFrame,
        pareto_cat: pd.DataFrame,
    ) -> Tuple[pd.DataFrame, List[dict]]:
        """
        Execute every strategy simulator and produce a consolidated summary.
        """
        if tickets.empty:
            raise ValueError("El dataset de tickets no puede estar vacío.")

        results: List[dict] = []

        # Baseline predictor (optional metrics usage)
        baseline_metrics = self.ticket_predictor.train(tickets)

        # Estrategia 1: Combos focalizados
        results.append(self.combo_sim.simulate_roi(tickets, detalle))

        # Estrategia 2: Marca propia
        results.append(self.marca_propia_est.simulate_marca_propia(pareto_cat, detalle))

        # Estrategia 3: Cross-merchandising
        cross_sell = CrossSellOptimizer(reglas)
        cross_ops = cross_sell.identify_opportunities()
        results.append(cross_sell.simulate_layout_change(cross_ops))

        # Estrategia 4: Upselling en caja
        results.append(self.upsell_det.simulate_upselling(tickets))

        # Estrategia 5: Programa fidelización
        loyalty = self.fidelizacion_sim.simulate_loyalty_program(tickets)
        results.append(loyalty)

        summary_records = []
        for strategy_result in results:
            marginal_margin = strategy_result.get(
                "incremental_margin_monthly",
                strategy_result.get("net_margin_monthly", 0.0),
            )
            confidence = strategy_result.get("confidence_score", 0.75) * 100

            summary_records.append(
                {
                    "Estrategia": strategy_result["strategy"].split(":")[1].strip()
                    if ":" in strategy_result["strategy"]
                    else strategy_result["strategy"],
                    "Inversión": strategy_result.get("investment", 0.0),
                    "Margen Incremental Mensual": marginal_margin,
                    "ROI %": strategy_result.get("roi_percentage", 0.0),
                    "Payback (meses)": strategy_result.get("payback_months", float("inf")),
                    "Confianza": confidence,
                }
            )

        summary_df = pd.DataFrame(summary_records).sort_values("ROI %", ascending=False).reset_index(drop=True)
        summary_df.attrs["baseline_metrics"] = baseline_metrics
        return summary_df, results

    def export_results(
        self,
        summary_df: pd.DataFrame,
        detailed_results: List[dict],
        *,
        output_dir: Path | str = "data/ml_results",
    ) -> None:
        """Persist summary and per-strategy details for dashboard consumption."""
        output_path = Path(output_dir)
        ensure_directory(output_path)

        summary_path = output_path / "strategy_roi_summary.parquet"
        details_path = output_path / "strategy_roi_details.json"

        summary_df.to_parquet(summary_path, index=False)
        with details_path.open("w", encoding="utf-8") as stream:
            json.dump(detailed_results, stream, indent=2, default=_json_serializer)


def _json_serializer(value):
    """Simple JSON serializer for Pandas/Numpy types."""
    if isinstance(value, pd.DataFrame):
        return value.to_dict(orient="records")
    if isinstance(value, (pd.Timestamp, pd.Timedelta)):
        return value.isoformat()
    if hasattr(value, "tolist"):
        return value.tolist()
    return value
