"""Monte Carlo revenue simulation for DreamCo sandbox bots."""

from __future__ import annotations

import math
import random
from dataclasses import dataclass


@dataclass
class SimulationResult:
    bot_id: str
    mean_monthly_revenue: float
    p5: float
    p95: float
    confidence_interval: tuple[float, float]


class RevenueSimulator:
    """Estimate revenue distributions using simple Monte Carlo sampling."""

    def simulate(self, bot_id: str, n_calls: int = 1000, n_simulations: int = 500) -> SimulationResult:
        monthly_values = []
        for _ in range(n_simulations):
            call_volume = max(0, int(random.gauss(n_calls, max(n_calls * 0.1, 1))))
            conversion_rate = min(max(random.gauss(0.08, 0.02), 0.0), 1.0)
            avg_revenue = max(random.gauss(12.0, 3.0), 0.1)
            monthly_values.append(call_volume * conversion_rate * avg_revenue)
        monthly_values.sort()
        mean = sum(monthly_values) / len(monthly_values)
        p5 = monthly_values[max(int(len(monthly_values) * 0.05) - 1, 0)]
        p95 = monthly_values[max(int(len(monthly_values) * 0.95) - 1, 0)]
        stdev = math.sqrt(sum((value - mean) ** 2 for value in monthly_values) / len(monthly_values))
        margin = 1.96 * (stdev / math.sqrt(len(monthly_values)))
        return SimulationResult(bot_id=bot_id, mean_monthly_revenue=mean, p5=p5, p95=p95, confidence_interval=(mean - margin, mean + margin))
