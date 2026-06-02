from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List

@dataclass
class WorkloadForecast:
    bot_id: str
    predicted_load_24h: float
    confidence: float

@dataclass
class StaffingPlan:
    actions: List[str]
    expected_cost: float
    sla_buffer_pct: float


class StaffingOptimizer:
    def rebalance(self, forecasts: Iterable[WorkloadForecast]) -> StaffingPlan:
        actions: List[str] = []
        expected_cost = 0.0
        total_capacity = 0.0
        total_load = 0.0
        for forecast in forecasts:
            total_load += forecast.predicted_load_24h
            if forecast.predicted_load_24h > 0.8:
                actions.append(f'spin_up_instance:{forecast.bot_id}')
                expected_cost += 120
                total_capacity += 1.2
            elif forecast.predicted_load_24h > 0.55:
                actions.append(f'upgrade_tier:{forecast.bot_id}')
                expected_cost += 60
                total_capacity += 1.0
            elif forecast.predicted_load_24h < 0.15:
                actions.append(f'retire_underused:{forecast.bot_id}')
                expected_cost -= 30
                total_capacity += 0.3
            else:
                actions.append(f'migrate_load:{forecast.bot_id}')
                expected_cost += 20
                total_capacity += 0.8
        sla_buffer = round(max(0.0, (total_capacity - total_load) / max(total_capacity, 0.1) * 100), 2)
        return StaffingPlan(actions=actions, expected_cost=round(expected_cost, 2), sla_buffer_pct=sla_buffer)



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
