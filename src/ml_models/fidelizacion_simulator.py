"""Loyalty program simulator leveraging ticket clustering as customer proxy."""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


@dataclass
class FidelizacionSimulator:
    """
    Estimate ROI for a loyalty programme without explicit customer IDs.
    """

    def estimate_customer_base(self, tickets: pd.DataFrame) -> float:
        """Approximate unique customers per month using ticket counts."""
        if tickets.empty:
            return 0.0
        monthly_tickets = len(tickets) / 12.0
        # Heuristic: ~60% of tickets correspond to unique customers
        return monthly_tickets * 0.60

    def simulate_loyalty_program(
        self,
        tickets: pd.DataFrame,
        *,
        enrollment_rate: float = 0.35,
        frequency_lift: float = 0.15,
        ticket_lift: float = 0.10,
        discount_pct: float = 0.02,
        setup_investment: float = 300_000.0,
    ) -> dict:
        """Simulate the economic impact of launching a loyalty programme."""
        if tickets.empty:
            raise ValueError("Tickets dataset is empty.")

        monthly_customers = self.estimate_customer_base(tickets)
        enrolled_customers = monthly_customers * enrollment_rate

        monto_col = "monto_total" if "monto_total" in tickets.columns else "ventas_totales"
        avg_ticket = float(tickets[monto_col].mean())
        avg_margin = float(tickets["margen_total"].mean())

        baseline_frequency = 1.2  # visits per month
        new_frequency = baseline_frequency * (1 + frequency_lift)
        incremental_visits = enrolled_customers * (new_frequency - baseline_frequency)

        incremental_ticket_value = enrolled_customers * baseline_frequency * avg_ticket * ticket_lift

        incremental_revenue = incremental_visits * avg_ticket + incremental_ticket_value
        margin_ratio = avg_margin / avg_ticket if avg_ticket else 0.0
        incremental_margin_gross = incremental_revenue * margin_ratio

        enrolled_sales = enrolled_customers * new_frequency * avg_ticket * (1 + ticket_lift)
        discount_cost = enrolled_sales * discount_pct

        net_margin_monthly = incremental_margin_gross - discount_cost

        roi_percentage = (
            (net_margin_monthly * 12) / setup_investment * 100 if setup_investment > 0 else float("inf")
        )
        payback_months = (
            setup_investment / net_margin_monthly if net_margin_monthly > 0 else float("inf")
        )

        return {
            "strategy": "Estrategia #5: Programa Fidelización",
            "estimated_monthly_customers": monthly_customers,
            "enrolled_customers": enrolled_customers,
            "enrollment_rate": enrollment_rate,
            "frequency_lift": frequency_lift,
            "ticket_lift": ticket_lift,
            "incremental_visits_monthly": incremental_visits,
            "incremental_revenue_monthly": incremental_revenue,
            "incremental_margin_gross_monthly": incremental_margin_gross,
            "discount_cost_monthly": discount_cost,
            "net_margin_monthly": net_margin_monthly,
            "investment": setup_investment,
            "roi_percentage": roi_percentage,
            "payback_months": payback_months,
        }
