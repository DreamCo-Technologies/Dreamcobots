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
