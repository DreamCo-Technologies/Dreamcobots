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
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: float = field(default_factory=time.time)

    def with_strength(self, strength: float) -> "PheromoneTrace":
        return PheromoneTrace(
            trace_type=self.trace_type,
            strength=strength,
            position=self.position,
            bot_id=self.bot_id,
            risk=self.risk,
            metadata=dict(self.metadata),
            created_at=self.created_at,
        )
