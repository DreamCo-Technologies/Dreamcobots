"""MRR and ARR projection engine for DreamCo SaaS subscriptions."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class ChurnAdjustedMRR:
    gross_mrr: float
    churn_rate: float

    @property
    def net_mrr(self) -> float:
        return self.gross_mrr * (1 - self.churn_rate)


@dataclass
class RevenueGrowthModel:
    monthly_growth_rate: float

    def project_arr(self, current_mrr: float, months: int = 12) -> float:
        projected = current_mrr
        total = 0.0
        for _ in range(months):
            projected *= 1 + self.monthly_growth_rate
            total += projected * 12 / months
        return total


def compute_mrr(subscriptions: list[dict[str, Any]]) -> dict[str, Any]:
    gross_mrr = sum(float(item.get("active_subscriptions", 0)) * float(item.get("monthly_price", 0)) for item in subscriptions)
    churn = sum(float(item.get("churn_rate", 0)) for item in subscriptions) / max(len(subscriptions), 1)
    adjusted = ChurnAdjustedMRR(gross_mrr=gross_mrr, churn_rate=churn)
    growth = RevenueGrowthModel(monthly_growth_rate=0.05)
    return {"mrr": gross_mrr, "arr": gross_mrr * 12, "churn_adjusted_mrr": adjusted.net_mrr, "projected_arr_12m": growth.project_arr(adjusted.net_mrr)}
