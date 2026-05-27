from __future__ import annotations

from dreamco_platform.swarm.stigmergy.pheromone import PheromoneTrace


class StigmergicBot:
    FORAGING_ROLE_FACTORS = {
        "scout": 0.9,
        "forager": 1.05,
        "exploiter": 1.12,
        "sentinel": 0.8,
    }

    def __init__(self, *, profit_weight: float = 0.3, risk_weight: float = 0.5) -> None:
        self.profit_weight = profit_weight
        self.risk_weight = risk_weight

    def assign_foraging_role(self, outcome: dict[str, float]) -> str:
        profit = float(outcome.get("profit", 0.0))
        risk = float(outcome.get("risk", 0.0))
        volatility = abs(float(outcome.get("volatility", 0.0)))
        if volatility >= 0.7:
            return "sentinel"
        if profit >= 5_000 and risk <= 0.25:
            return "exploiter"
        if profit > 0:
            return "forager"
        return "scout"

    def reinforce_trace(self, trace: PheromoneTrace, outcome: dict[str, float]) -> PheromoneTrace:
        profit = float(outcome.get("profit", 0.0))
        loss = float(outcome.get("loss", 0.0))
        risk = max(0.0, float(outcome.get("risk", trace.risk)))
        volatility = abs(float(outcome.get("volatility", trace.volatility_signal)))
        net = profit - loss
        economic_term = net / 10_000.0
        role = outcome.get("foraging_role") or trace.foraging_role or self.assign_foraging_role(outcome)
        role_factor = self.FORAGING_ROLE_FACTORS.get(role, 1.0)
        factor = (1.0 + (economic_term * self.profit_weight) - (risk * self.risk_weight)) * role_factor
        if net < 0:
            factor *= 0.6
        new_strength = max(0.0, min(1.0, trace.strength * factor))
        updated = trace.with_strength(new_strength)
        trust_score = max(0.0, min(1.0, trace.trust_score + (0.05 if net > 0 else -0.08)))
        return PheromoneTrace(
            trace_type=updated.trace_type,
            strength=updated.strength,
            position=updated.position,
            bot_id=updated.bot_id,
            risk=risk,
            embedding=updated.embedding,
            semantic_category=updated.semantic_category,
            trust_score=trust_score,
            economic_score=trace.economic_score + net,
            origin_lineage=updated.origin_lineage,
            foraging_role=str(role),
            decay_bias=updated.decay_bias,
            profitability_signal=net,
            volatility_signal=volatility,
            metadata=dict(updated.metadata),
            created_at=updated.created_at,
        )

    def decay_trace(self, trace: PheromoneTrace, base_decay_rate: float = 0.05) -> PheromoneTrace:
        return trace.adaptive_decay(base_decay_rate=base_decay_rate)
