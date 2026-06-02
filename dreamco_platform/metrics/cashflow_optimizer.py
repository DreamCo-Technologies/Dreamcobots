"""Real-time cash flow optimizer with a 13-week model."""
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Sequence


@dataclass
class CashFlowForecast:
    period: str
    inflows: float
    outflows: float
    net: float
    cumulative: float
    risk: float


@dataclass
class OptimizationActions:
    accelerate_collections: List[str]
    defer_payments: List[str]
    optimize_subscriptions: List[str]
    projected_cash: List[CashFlowForecast]


class CashFlowOptimizer:
    def project_13_weeks(self, starting_cash: float, inflows: Sequence[float], outflows: Sequence[float]) -> List[CashFlowForecast]:
        cumulative = starting_cash
        projection: List[CashFlowForecast] = []
        for week in range(13):
            inflow = float(inflows[week] if week < len(inflows) else inflows[-1] if inflows else 0.0)
            outflow = float(outflows[week] if week < len(outflows) else outflows[-1] if outflows else 0.0)
            net = inflow - outflow
            cumulative += net
            risk = max(0.0, min(1.0, (outflow - inflow + 1) / max(1.0, abs(cumulative) + 1)))
            projection.append(CashFlowForecast(f"week_{week + 1}", inflow, outflow, net, cumulative, round(risk, 3)))
        return projection

    def optimize(self, forecast: Sequence[CashFlowForecast]) -> OptimizationActions:
        accelerate: List[str] = []
        defer: List[str] = []
        subscriptions: List[str] = []
        for period in forecast:
            if period.net < 0 and period.risk > 0.2:
                accelerate.append(f"Accelerate collections in {period.period} by tightening invoice follow-up.")
            if period.outflows > period.inflows:
                defer.append(f"Defer non-critical vendor payments in {period.period}.")
            if period.risk > 0.35:
                subscriptions.append(f"Optimize or downgrade underused SaaS subscriptions before {period.period}.")
        return OptimizationActions(accelerate, defer, subscriptions, list(forecast))
