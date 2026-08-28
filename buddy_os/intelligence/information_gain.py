"""Active information-gathering primitives for Buddy.

Selects candidate observations using an explicit value heuristic. This layer
never performs the observation itself; callers decide whether an action is
safe and authorized.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import log2
from typing import Iterable


@dataclass(frozen=True)
class EvidenceAction:
    action_id: str
    description: str
    expected_outcomes: tuple[tuple[str, float], ...]
    cost: float = 1.0
    risk: float = 0.0

    def __post_init__(self) -> None:
        if self.cost <= 0:
            raise ValueError("cost must be positive")
        if not 0.0 <= self.risk <= 1.0:
            raise ValueError("risk must be between 0 and 1")
        total = sum(probability for _, probability in self.expected_outcomes)
        if self.expected_outcomes and abs(total - 1.0) > 1e-6:
            raise ValueError("expected outcome probabilities must sum to 1")


class InformationGainPlanner:
    @staticmethod
    def entropy(probabilities: Iterable[float]) -> float:
        return -sum(p * log2(p) for p in probabilities if p > 0)

    def rank(self, actions: Iterable[EvidenceAction]) -> tuple[EvidenceAction, ...]:
        def value(action: EvidenceAction) -> float:
            probabilities = [p for _, p in action.expected_outcomes]
            gain = self.entropy(probabilities) if probabilities else 0.0
            return gain / action.cost * (1.0 - action.risk)
        return tuple(sorted(actions, key=lambda a: (-value(a), a.action_id)))
