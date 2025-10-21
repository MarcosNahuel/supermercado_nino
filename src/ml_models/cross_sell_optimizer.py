"""Cross-selling opportunity optimizer based on association rules."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass
class CrossSellOptimizer:
    """
    Evaluate merchandising improvements by leveraging association rules.
    """

    reglas: pd.DataFrame

    def __post_init__(self) -> None:
        rename_map = {
            "antecedents": "antecedent",
            "consequents": "consequent",
            "antecedent support": "support_antecedent",
            "consequent support": "support_consequent",
        }
        self.reglas = self.reglas.rename(columns=rename_map).copy()
        if "antecedent" in self.reglas.columns:
            self.reglas["antecedent"] = self.reglas["antecedent"].apply(_flatten_itemset)
        if "consequent" in self.reglas.columns:
            self.reglas["consequent"] = self.reglas["consequent"].apply(_flatten_itemset)

    def identify_opportunities(
        self,
        *,
        min_lift: float = 5.0,
        max_current_confidence: float = 0.30,
    ) -> pd.DataFrame:
        """Filter high-lift yet under-exploited rule pairs."""
        required_columns = {
            "lift",
            "confidence",
            "antecedent",
            "consequent",
            "support_antecedent",
        }
        missing = required_columns.difference(self.reglas.columns)
        if missing:
            raise ValueError(f"Rules dataset missing columns: {sorted(missing)}")

        opportunities = self.reglas[
            (self.reglas["lift"] > min_lift) & (self.reglas["confidence"] < max_current_confidence)
        ].sort_values("lift", ascending=False)

        return opportunities.reset_index(drop=True)

    def simulate_layout_change(
        self,
        opportunities: pd.DataFrame,
        *,
        confidence_multiplier: float = 1.5,
        avg_consequent_price: float = 2_800.0,
        avg_margin_rate: float = 0.32,
    ) -> dict:
        """Simulate ROI from re-merchandising the top opportunity pairs."""
        if opportunities.empty:
            return {
                "strategy": "Estrategia #3: Cross-Merchandising (Layout Impulsor)",
                "num_opportunities": 0,
                "top_pairs_implemented": 0,
                "avg_confidence_lift": 0.0,
                "incremental_margin_monthly": 0.0,
                "investment": 80_000.0,
                "roi_percentage": 0.0,
                "payback_months": float("inf"),
                "detailed_opportunities": opportunities,
            }

        rows = []
        monthly_tickets_total = 306_000 / 12  # 306k yearly tickets baseline

        for _, rule in opportunities.head(10).iterrows():
            current_confidence = float(rule["confidence"])
            target_confidence = min(current_confidence * confidence_multiplier, 0.50)

            support_ant = float(rule["support_antecedent"])
            tickets_with_antecedent = monthly_tickets_total * support_ant

            current_consequent_purchases = tickets_with_antecedent * current_confidence
            target_consequent_purchases = tickets_with_antecedent * target_confidence
            incremental_purchases = max(target_consequent_purchases - current_consequent_purchases, 0.0)

            incremental_revenue = incremental_purchases * avg_consequent_price
            incremental_margin = incremental_revenue * avg_margin_rate

            rows.append(
                {
                    "antecedent": rule["antecedent"],
                    "consequent": rule["consequent"],
                    "current_confidence": current_confidence,
                    "target_confidence": target_confidence,
                    "lift": float(rule["lift"]),
                    "incremental_purchases_monthly": incremental_purchases,
                    "incremental_revenue_monthly": incremental_revenue,
                    "incremental_margin_monthly": incremental_margin,
                }
            )

        df_results = pd.DataFrame(rows)

        total_incremental_margin = float(df_results["incremental_margin_monthly"].sum())
        investment = 80_000.0
        roi_percentage = (
            (total_incremental_margin * 12) / investment * 100 if investment > 0 else float("inf")
        )
        payback_months = investment / total_incremental_margin if total_incremental_margin > 0 else float("inf")

        return {
            "strategy": "Estrategia #3: Cross-Merchandising (Layout Impulsor)",
            "num_opportunities": int(len(opportunities)),
            "top_pairs_implemented": int(len(df_results)),
            "avg_confidence_lift": float(
                df_results["target_confidence"]
                .div(df_results["current_confidence"].replace(0, np.nan))
                .replace([np.inf, -np.inf], np.nan)
                .mean()
            ),
            "incremental_margin_monthly": total_incremental_margin,
            "investment": investment,
            "roi_percentage": roi_percentage,
            "payback_months": payback_months,
            "detailed_opportunities": df_results,
        }


def _flatten_itemset(value):
    """Convert frozenset/list with one element into a readable string."""
    if isinstance(value, (set, frozenset, list, tuple)):
        return ", ".join(sorted(str(v) for v in value))
    return str(value)
