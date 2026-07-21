from __future__ import annotations

from dreamco_platform.swarm.stigmergy.pheromone import PheromoneTrace


class StigmergicBot:
    def __init__(self, *, profit_weight: float = 0.3, risk_weight: float = 0.5) -> None:
        self.profit_weight = profit_weight
        self.risk_weight = risk_weight

    def reinforce_trace(self, trace: PheromoneTrace, outcome: dict[str, float]) -> PheromoneTrace:
        profit = float(outcome.get("profit", 0.0))
        loss = float(outcome.get("loss", 0.0))
        risk = max(0.0, float(outcome.get("risk", trace.risk)))
        net = profit - loss
        economic_term = net / 10_000.0
        factor = 1.0 + (economic_term * self.profit_weight) - (risk * self.risk_weight)
        if net < 0:
            factor *= 0.6
        new_strength = max(0.0, min(1.0, trace.strength * factor))
        return trace.with_strength(new_strength)
