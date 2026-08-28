"""Transparent scoring for candidate causal interventions.

This module ranks candidate interventions for further analysis; it never
executes them. Scores combine expected benefit, evidence strength, cost and
risk so downstream action systems can apply their own authorization policy.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class InterventionCandidate:
    candidate_id: str
    variable: str
    expected_benefit: float
    evidence_strength: float
    cost: float = 1.0
    risk: float = 0.0

    def __post_init__(self) -> None:
        for name, value in (("expected_benefit", self.expected_benefit), ("evidence_strength", self.evidence_strength), ("risk", self.risk)):
            if not 0.0 <= value <= 1.0:
                raise ValueError(f"{name} must be between 0 and 1")
        if self.cost <= 0:
            raise ValueError("cost must be positive")


class InterventionScorer:
    @staticmethod
    def score(candidate: InterventionCandidate) -> float:
        return (candidate.expected_benefit * candidate.evidence_strength * (1.0 - candidate.risk)) / candidate.cost

    def rank(self, candidates: list[InterventionCandidate] | tuple[InterventionCandidate, ...]) -> tuple[InterventionCandidate, ...]:
        return tuple(sorted(candidates, key=lambda c: (-self.score(c), c.candidate_id)))
