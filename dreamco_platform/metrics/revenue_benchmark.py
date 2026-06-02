"""Revenue benchmarking primitives for DreamCo bots."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass
class RevenueBenchmark:
    bot_id: str
    revenue_per_hour: float
    cost_per_call: float
    roi_ratio: float
    payback_period: float

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def compute_revenue_benchmark(bot_id: str, revenue_history: list[dict[str, Any]]) -> RevenueBenchmark:
    total_revenue = sum(float(item.get("revenue_usd", 0)) for item in revenue_history)
    total_cost = sum(float(item.get("cost_usd", 0)) for item in revenue_history)
    total_hours = sum(float(item.get("hours", 0)) for item in revenue_history) or 1.0
    total_calls = sum(int(item.get("calls", 0)) for item in revenue_history) or 1
    revenue_per_hour = total_revenue / total_hours
    cost_per_call = total_cost / total_calls
    roi_ratio = total_revenue / total_cost if total_cost else float("inf")
    payback_period = total_cost / revenue_per_hour if revenue_per_hour else float("inf")
    return RevenueBenchmark(bot_id, revenue_per_hour, cost_per_call, roi_ratio, payback_period)
