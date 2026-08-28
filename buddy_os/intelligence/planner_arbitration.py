"""Arbitrate independent planning results without hiding disagreement."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PlannerResult:
    planner_id: str
    recommendation: str
    score: float
    confidence: float
    rationale: str = ""

    def __post_init__(self) -> None:
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("confidence must be between 0 and 1")


@dataclass(frozen=True)
class Arbitration:
    winner: PlannerResult | None
    agreement: float
    disagreement: tuple[str, ...]
    requires_verification: bool


class PlannerArbitrator:
    def arbitrate(self, results: tuple[PlannerResult, ...] | list[PlannerResult]) -> Arbitration:
        if not results:
            return Arbitration(None, 0.0, (), True)
        recommendations = {r.recommendation for r in results}
        agreement = 1.0 if len(recommendations) == 1 else 1.0 / len(recommendations)
        ranked = sorted(results, key=lambda r: (-r.score * r.confidence, r.planner_id))
        disagreement = tuple(sorted(recommendations))
        return Arbitration(ranked[0], agreement, disagreement, len(recommendations) > 1)
