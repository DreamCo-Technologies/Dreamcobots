"""Evidence-aware ensembles for Buddy reasoning methods.

The ensemble never treats a vote as ground truth. It exposes disagreement,
method diversity and unresolved status so a verifier or external observation
can resolve conflicts.
"""
from __future__ import annotations

from dataclasses import dataclass
from collections import Counter
from typing import Iterable


@dataclass(frozen=True)
class ReasoningOpinion:
    method: str
    answer: object
    confidence: float
    evidence: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("confidence must be between 0 and 1")


@dataclass(frozen=True)
class EnsembleResult:
    answer: object | None
    confidence: float
    agreement: float
    opinions: tuple[ReasoningOpinion, ...]
    disputed: bool
    requires_verification: bool


class ReasoningEnsemble:
    def combine(self, opinions: Iterable[ReasoningOpinion]) -> EnsembleResult:
        rows = tuple(opinions)
        if not rows:
            return EnsembleResult(None, 0.0, 0.0, (), True, True)
        weights: dict[object, float] = {}
        for opinion in rows:
            weights[opinion.answer] = weights.get(opinion.answer, 0.0) + opinion.confidence
        answer, total = max(weights.items(), key=lambda item: item[1])
        agreement = total / sum(weights.values()) if weights else 0.0
        disputed = len(weights) > 1
        # Low agreement or conflicting answers always require verification.
        requires_verification = disputed or agreement < 0.75
        confidence = min(agreement, sum(o.confidence for o in rows) / len(rows))
        return EnsembleResult(answer, confidence, agreement, rows, disputed, requires_verification)
