from __future__ import annotations

import math
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass
class SemanticPheromone:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    trace_type: str = "opportunity"
    semantic_category: str = "general"
    strength: float = 0.5
    decay_rate: float = 0.05
    confidence: float = 0.5
    trust_score: float = 0.5
    economic_score: float = 0.0
    reinforcement_count: int = 0
    volatility_score: float = 0.0
    execution_outcome: str = "unknown"
    origin_lineage: list[str] = field(default_factory=list)
    embedding: list[float] = field(default_factory=list)
    context: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def effective_decay_rate(self) -> float:
        reinforcement_modifier = 1.0 / (1.0 + max(0, self.reinforcement_count) * 0.25)
        profitability_modifier = max(0.25, 1.0 - max(0.0, self.economic_score) * 0.5)
        outcome_modifier = 1.6 if self.execution_outcome == "failed" else 0.85
        volatility_modifier = 1.0 + max(0.0, self.volatility_score) * 0.5
        return self.decay_rate * reinforcement_modifier * profitability_modifier * outcome_modifier * volatility_modifier

    def current_strength(self, now: datetime | None = None) -> float:
        ts = now or datetime.now(timezone.utc)
        age_hours = max(0.0, (ts - self.created_at).total_seconds() / 3600.0)
        decayed = self.strength * math.exp(-self.effective_decay_rate() * age_hours)
        return max(0.0, min(1.0, decayed))

    def is_active(self, now: datetime | None = None, threshold: float = 0.01) -> bool:
        return self.current_strength(now=now) >= threshold

    def reinforce(self, *, profit_delta: float = 0.0, trust_delta: float = 0.02, success: bool = True) -> None:
        self.reinforcement_count += 1
        self.economic_score = max(0.0, self.economic_score + profit_delta)
        self.trust_score = max(0.0, min(1.0, self.trust_score + trust_delta))
        self.strength = max(0.0, min(1.0, self.strength + (0.1 if success else -0.15)))
        self.execution_outcome = "success" if success else "failed"

    def to_dict(self) -> dict[str, Any]:
        payload = self.__dict__.copy()
        payload["created_at"] = self.created_at.isoformat()
        return payload

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "SemanticPheromone":
        data = dict(payload)
        created_at = data.get("created_at")
        if isinstance(created_at, str):
            data["created_at"] = datetime.fromisoformat(created_at)
        return cls(**data)
