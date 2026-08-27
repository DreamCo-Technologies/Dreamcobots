"""Evidence-weighted causal hypotheses for Buddy.

The engine records hypotheses and evidence; it does not claim causality merely
because two events are correlated or ordered in time.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class Evidence:
    source: str
    supports: bool
    weight: float = 1.0
    note: str = ""


@dataclass
class CausalHypothesis:
    cause: str
    effect: str
    mechanism: str = ""
    evidence: List[Evidence] = field(default_factory=list)

    @property
    def support_score(self) -> float:
        positive = sum(max(0.0, e.weight) for e in self.evidence if e.supports)
        negative = sum(max(0.0, e.weight) for e in self.evidence if not e.supports)
        total = positive + negative
        return positive / total if total else 0.0

    def assess(self) -> Dict[str, object]:
        return {
            "cause": self.cause,
            "effect": self.effect,
            "mechanism": self.mechanism,
            "support_score": self.support_score,
            "evidence_count": len(self.evidence),
            "status": "supported" if self.support_score >= 0.7 else "uncertain",
        }


class CausalEngine:
    def __init__(self) -> None:
        self._hypotheses: Dict[str, CausalHypothesis] = {}

    def add(self, hypothesis_id: str, hypothesis: CausalHypothesis) -> CausalHypothesis:
        self._hypotheses[hypothesis_id] = hypothesis
        return hypothesis

    def get(self, hypothesis_id: str) -> CausalHypothesis | None:
        return self._hypotheses.get(hypothesis_id)

    def assess(self, hypothesis_id: str) -> Dict[str, object]:
        hypothesis = self.get(hypothesis_id)
        if hypothesis is None:
            return {"status": "missing", "hypothesis_id": hypothesis_id}
        return hypothesis.assess()
