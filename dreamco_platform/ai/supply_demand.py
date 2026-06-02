from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

@dataclass
class DemandForecast:
    bot_slug: str
    predicted_queries_30d: int
    confidence: float
    drivers: List[str]

@dataclass
class SupplyCapacity:
    available_instances: int
    max_throughput: int
    cost_per_instance: float

@dataclass
class BalancingActions:
    actions: List[str]
    projected_margin_impact: float


class SupplyDemandBalancer:
    def __init__(self, forecasts: List[DemandForecast] | None = None, capacities: Dict[str, SupplyCapacity] | None = None) -> None:
        self.forecasts = forecasts or []
        self.capacities = capacities or {}

    def optimize(self) -> BalancingActions:
        actions: List[str] = []
        margin_impact = 0.0
        for forecast in self.forecasts:
            capacity = self.capacities.get(forecast.bot_slug, SupplyCapacity(1, 1000, 50.0))
            expected = forecast.predicted_queries_30d
            total_capacity = capacity.available_instances * capacity.max_throughput
            if expected > total_capacity:
                extra = max(1, (expected - total_capacity + capacity.max_throughput - 1) // capacity.max_throughput)
                actions.append(f'pre_provision:{forecast.bot_slug}:{extra}')
                margin_impact -= extra * capacity.cost_per_instance
            else:
                actions.append(f'hold_capacity:{forecast.bot_slug}')
                margin_impact += max(0.0, (total_capacity - expected) / capacity.max_throughput * 5)
        return BalancingActions(actions=actions, projected_margin_impact=round(margin_impact, 2))



def module_summary() -> dict:
    """Provide a compact runtime summary for orchestration tooling."""
    public_items = [name for name in globals() if not name.startswith('_')]
    return {
        'module': __name__,
        'public_items': sorted(public_items),
        'line_count': len(__doc__.splitlines()) if __doc__ else 0,
    }


def demo_payload() -> dict:
    """Return a deterministic payload useful for smoke-free integration wiring."""
    return {'module': __name__, 'status': 'ready'}
