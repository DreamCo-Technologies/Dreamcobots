from __future__ import annotations

from dataclasses import dataclass, field
import time
from typing import Any


@dataclass(frozen=True)
class PheromoneTrace:
    trace_type: str
    strength: float
    position: tuple[int, int]
    bot_id: str
    risk: float = 0.0
    embedding: tuple[float, ...] = ()
    semantic_category: str = "general"
    trust_score: float = 0.5
    economic_score: float = 0.0
    origin_lineage: tuple[str, ...] = ()
    foraging_role: str = "scout"
    decay_bias: float = 1.0
    profitability_signal: float = 0.0
    volatility_signal: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: float = field(default_factory=time.time)

    def with_strength(self, strength: float) -> "PheromoneTrace":
        return PheromoneTrace(
            trace_type=self.trace_type,
            strength=strength,
            position=self.position,
            bot_id=self.bot_id,
            risk=self.risk,
            embedding=self.embedding,
            semantic_category=self.semantic_category,
            trust_score=self.trust_score,
            economic_score=self.economic_score,
            origin_lineage=self.origin_lineage,
            foraging_role=self.foraging_role,
            decay_bias=self.decay_bias,
            profitability_signal=self.profitability_signal,
            volatility_signal=self.volatility_signal,
            metadata=dict(self.metadata),
            created_at=self.created_at,
        )

    def with_semantic_feedback(
        self,
        *,
        trust_score: float | None = None,
        economic_score: float | None = None,
        profitability_signal: float | None = None,
        volatility_signal: float | None = None,
    ) -> "PheromoneTrace":
        return PheromoneTrace(
            trace_type=self.trace_type,
            strength=self.strength,
            position=self.position,
            bot_id=self.bot_id,
            risk=self.risk,
            embedding=self.embedding,
            semantic_category=self.semantic_category,
            trust_score=max(0.0, min(1.0, trust_score if trust_score is not None else self.trust_score)),
            economic_score=economic_score if economic_score is not None else self.economic_score,
            origin_lineage=self.origin_lineage,
            foraging_role=self.foraging_role,
            decay_bias=self.decay_bias,
            profitability_signal=(
                profitability_signal if profitability_signal is not None else self.profitability_signal
            ),
            volatility_signal=volatility_signal if volatility_signal is not None else self.volatility_signal,
            metadata=dict(self.metadata),
            created_at=self.created_at,
        )

    def adaptive_decay(self, base_decay_rate: float = 0.05) -> "PheromoneTrace":
        profitability_bonus = max(-0.2, min(0.2, self.profitability_signal / 10_000.0))
        volatility_penalty = max(0.0, self.volatility_signal) * 0.15
        trust_modifier = (1.0 - self.trust_score) * 0.08
        decay_rate = max(
            0.0,
            base_decay_rate + volatility_penalty + trust_modifier - profitability_bonus,
        ) * max(0.1, self.decay_bias)
        new_strength = max(0.0, self.strength * (1.0 - decay_rate))
        return self.with_strength(new_strength)
