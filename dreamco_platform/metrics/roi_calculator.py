from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List, Tuple


@dataclass
class ROICalculation:
    investment_usd: float
    return_usd: float
    roi_pct: float
    payback_days: float
    irr: float


class ROICalculator:
    def compute(self, cost_events: Iterable[dict], revenue_events: Iterable[dict]) -> ROICalculation:
        costs = sum(event['amount'] for event in cost_events)
        returns = sum(event['amount'] for event in revenue_events)
        roi = ((returns - costs) / costs * 100) if costs else 0.0
        daily_return = returns / max(1, len(list(revenue_events)) or 1)
        payback = costs / max(daily_return, 1.0)
        irr = self._irr([-costs, returns])
        return ROICalculation(round(costs, 2), round(returns, 2), round(roi, 2), round(payback, 2), round(irr, 4))

    def scenario_analysis(self, base_return: float) -> dict:
        return {'optimistic': round(base_return * 1.25, 2), 'base': round(base_return, 2), 'pessimistic': round(base_return * 0.75, 2)}

    def _irr(self, cash_flows: List[float], guess: float = 0.1) -> float:
        rate = guess
        for _ in range(20):
            npv = sum(flow / ((1 + rate) ** index) for index, flow in enumerate(cash_flows))
            derivative = sum(-index * flow / ((1 + rate) ** (index + 1)) for index, flow in enumerate(cash_flows[1:], start=1)) or 1.0
            rate -= npv / derivative
        return rate

def investment_type(self, cost_events: Iterable[dict]) -> str:
    categories = {event.get('type', 'custom') for event in cost_events}
    if 'purchase' in categories:
        return 'bot purchase ROI'
    if 'subscription' in categories:
        return 'subscription ROI'
    return 'custom workflow ROI'


def cash_flow_table(self, cost_events: Iterable[dict], revenue_events: Iterable[dict]) -> List[tuple[str, float]]:
    rows = [('cost', -event['amount']) for event in cost_events]
    rows.extend(('revenue', event['amount']) for event in revenue_events)
    return rows


ROICalculator.investment_type = investment_type
ROICalculator.cash_flow_table = cash_flow_table

def break_even_revenue(self, cost_events: Iterable[dict]) -> float:
    return round(sum(event['amount'] for event in cost_events), 2)


def roi_ratio(self, calculation: ROICalculation) -> float:
    return round(calculation.return_usd / max(calculation.investment_usd, 1e-9), 4)


ROICalculator.break_even_revenue = break_even_revenue
ROICalculator.roi_ratio = roi_ratio
