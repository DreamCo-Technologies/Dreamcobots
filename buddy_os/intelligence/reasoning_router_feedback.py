"""Conservative feedback loop for improving Buddy's reasoning selection.

Feedback is evidence, not an automatic authority grant. Routing updates are
bounded by minimum observations and confidence margins so one noisy result
cannot permanently rewrite the strategy.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from .reasoning_evaluation import ReasoningEvaluationLab


@dataclass(frozen=True)
class RoutingPreference:
    method: str
    score: float
    observations: int


class ReasoningRouterFeedback:
    def __init__(self, lab: ReasoningEvaluationLab, min_observations: int = 5) -> None:
        if min_observations < 1:
            raise ValueError("min_observations must be positive")
        self.lab = lab
        self.min_observations = min_observations

    def preferences(self, methods: Iterable[str]) -> list[RoutingPreference]:
        output: list[RoutingPreference] = []
        for method in methods:
            score = self.lab.score(method)
            if score.resolved_trials < self.min_observations or score.accuracy is None:
                continue
            # Accuracy is primary; calibration and cost are tie-breakers.
            calibration = 1.0 - (score.brier_score or 1.0)
            value = 0.75 * score.accuracy + 0.25 * calibration
            output.append(RoutingPreference(method, value, score.resolved_trials))
        return sorted(output, key=lambda p: (-p.score, p.method))

    def preferred_method(self, methods: Iterable[str]) -> str | None:
        ranked = self.preferences(methods)
        return ranked[0].method if ranked else None
