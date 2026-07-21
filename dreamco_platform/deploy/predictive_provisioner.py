from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Iterable, List


@dataclass
class ProvisioningPlan:
    resource_type: str
    quantity: int
    region: str
    scheduled_at: datetime
    cost_estimate: float


class PredictiveProvisioner:
    def __init__(self, baseline_region: str = 'us-east-1') -> None:
        self.baseline_region = baseline_region

    def plan(self, forecasts: Iterable[dict], forecast_hours: int = 72) -> List[ProvisioningPlan]:
        plans = []
        for forecast in forecasts:
            if forecast['hours_ahead'] > forecast_hours:
                continue
            stable = forecast.get('volatility', 0.0) < 0.2
            resource_type = 'spot-instance' if stable else 'on-demand-instance'
            quantity = max(1, int(forecast['cpu_cores'] / 4) + (1 if forecast['spike_risk'] > 0.5 else 0))
            scheduled = datetime.utcnow() + timedelta(hours=max(forecast['hours_ahead'] - 2, 0))
            cost = quantity * (0.12 if stable else 0.28) * min(forecast['hours_ahead'], 24)
            plans.append(ProvisioningPlan(resource_type, quantity, forecast.get('region', self.baseline_region), scheduled, round(cost, 2)))
        return plans

def total_cost(self, plans: Iterable[ProvisioningPlan]) -> float:
    return round(sum(plan.cost_estimate for plan in plans), 2)


def by_region(self, plans: Iterable[ProvisioningPlan]) -> dict:
    summary = {}
    for plan in plans:
        summary[plan.region] = summary.get(plan.region, 0) + plan.quantity
    return summary


def stable_mix(self, plans: Iterable[ProvisioningPlan]) -> dict:
    plans = list(plans)
    return {
        'spot': sum(1 for plan in plans if 'spot' in plan.resource_type),
        'on_demand': sum(1 for plan in plans if 'on-demand' in plan.resource_type),
    }


PredictiveProvisioner.total_cost = total_cost
PredictiveProvisioner.by_region = by_region
PredictiveProvisioner.stable_mix = stable_mix

def next_window(self, forecast_hours: int = 24) -> tuple[int, int]:
    return (24, forecast_hours)


def resource_mix(self, plans: Iterable[ProvisioningPlan]) -> dict:
    plans = list(plans)
    return {'total_quantity': sum(plan.quantity for plan in plans), 'plan_count': len(plans)}


PredictiveProvisioner.next_window = next_window
PredictiveProvisioner.resource_mix = resource_mix
