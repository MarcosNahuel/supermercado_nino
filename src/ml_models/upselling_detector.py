"""Upselling opportunity detector for checkout interventions."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple

import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingClassifier


@dataclass
class UpsellingDetector:
    """
    Estimate incremental margin from training cashiers on upselling scripts.
    """

    opportunity_detector: GradientBoostingClassifier = field(
        default_factory=lambda: GradientBoostingClassifier(random_state=42)
    )

    def classify_tickets(self, tickets: pd.DataFrame) -> pd.DataFrame:
        """Assign a basket size segment to each ticket."""
        valor_col = "monto_total" if "monto_total" in tickets.columns else "ventas_totales"
        if valor_col not in tickets.columns:
            raise ValueError("Tickets dataset must include 'monto_total' o 'ventas_totales'.")

        tickets = tickets.copy()
        monto = tickets[valor_col].astype(float)
        conditions = [
            monto < 5_000,
            (monto >= 5_000) & (monto < 15_000),
            (monto >= 15_000) & (monto < 30_000),
            monto >= 30_000,
        ]
        labels = ["Conveniencia", "Estándar", "Abastecimiento", "Grande"]
        tickets["segmento_monto"] = np.select(conditions, labels, default="Estándar")
        tickets["monto_total_sim"] = monto
        return tickets

    def simulate_upselling(
        self,
        tickets: pd.DataFrame,
        *,
        success_rate: float = 0.10,
        avg_upsell_value: float = 800.0,
        training_investment: float = 120_000.0,
        margin_rate: float = 0.38,
    ) -> dict:
        """Simulate ROI of checkout upselling incentives."""
        if tickets.empty:
            raise ValueError("Tickets dataset is empty.")

        tickets_segmented = self.classify_tickets(tickets)
        target_mask = tickets_segmented["monto_total_sim"] < 15_000
        monthly_target_tickets = target_mask.sum() / 12.0
        successful_upsells = monthly_target_tickets * success_rate

        incremental_revenue_monthly = successful_upsells * avg_upsell_value
        incremental_margin_monthly = incremental_revenue_monthly * margin_rate

        roi_percentage = (
            (incremental_margin_monthly * 12) / training_investment * 100
            if training_investment > 0
            else float("inf")
        )
        payback_months = (
            training_investment / incremental_margin_monthly
            if incremental_margin_monthly > 0
            else float("inf")
        )

        return {
            "strategy": "Estrategia #4: Upselling en Caja",
            "target_segment": "Tickets < $15,000",
            "monthly_target_tickets": monthly_target_tickets,
            "success_rate": success_rate,
            "successful_upsells_monthly": successful_upsells,
            "avg_upsell_value": avg_upsell_value,
            "incremental_revenue_monthly": incremental_revenue_monthly,
            "incremental_margin_monthly": incremental_margin_monthly,
            "investment": training_investment,
            "roi_percentage": roi_percentage,
            "payback_months": payback_months,
        }
