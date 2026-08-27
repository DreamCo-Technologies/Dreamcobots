"""Unified, explainable decision scoring for Buddy.

Combines independent evidence signals without allowing a learned signal to
bypass policy or authorization. The engine ranks candidates; it never acts.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Dict, Iterable, List


@dataclass(frozen=True)
class CandidateEvidence:
    name: str
    capability: float = 0.0
    historical_success: float = 0.0
    transition_probability: float = 0.0
    expected_value: float = 0.0
    reliability: float = 0.0
    evidence_quality: float = 0.0
    cost_efficiency: float = 0.0
    latency_efficiency: float = 0.0
    risk: float = 0.0
    authorized: bool = True


@dataclass(frozen=True)
class Decision:
    selected: str | None
    confidence: float
    ranked: List[Dict[str, object]]
    reason: str
    policy: str = "advisory-ranking"


class BuddyDecisionEngine:
    """Deterministic weighted scorer for candidate routes.

    Scores are normalized to 0..1. Risk is a penalty. Unauthorized routes are
    excluded before scoring, so ranking cannot grant permissions.
    """

    DEFAULT_WEIGHTS = {
        "capability": 0.20,
        "historical_success": 0.15,
        "transition_probability": 0.10,
        "expected_value": 0.15,
        "reliability": 0.12,
        "evidence_quality": 0.10,
        "cost_efficiency": 0.05,
        "latency_efficiency": 0.03,
        "risk": -0.10,
    }

    def __init__(self, weights: Dict[str, float] | None = None) -> None:
        self.weights = dict(weights or self.DEFAULT_WEIGHTS)

    def score(self, candidate: CandidateEvidence) -> float:
        return max(0.0, min(1.0, sum(getattr(candidate, key) * weight for key, weight in self.weights.items())))

    def rank(self, candidates: Iterable[CandidateEvidence]) -> List[Dict[str, object]]:
        ranked = []
        for candidate in candidates:
            if not candidate.authorized:
                continue
            ranked.append({"name": candidate.name, "score": round(self.score(candidate), 6), "evidence": asdict(candidate)})
        ranked.sort(key=lambda item: (-item["score"], item["name"]))
        return ranked

    def decide(self, candidates: Iterable[CandidateEvidence], minimum_confidence: float = 0.55) -> Decision:
        ranked = self.rank(candidates)
        if not ranked:
            return Decision(None, 0.0, [], "No authorized candidate available.")
        confidence = float(ranked[0]["score"])
        if confidence < minimum_confidence:
            return Decision(None, confidence, ranked, "Best candidate is below the confidence threshold; request more evidence or human review.")
        return Decision(ranked[0]["name"], confidence, ranked, "Selected highest-scoring authorized candidate from explicit evidence signals.")
