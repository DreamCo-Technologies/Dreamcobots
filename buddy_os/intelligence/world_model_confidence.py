"""Confidence-aware transition selection for Buddy's world model."""
from __future__ import annotations

from dataclasses import dataclass
from .world_model import State


@dataclass(frozen=True)
class PredictedState:
    state: State
    confidence: float
    action: str
    rationale: str = ""

    def __post_init__(self) -> None:
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("confidence must be between 0 and 1")


class WorldModelEvaluator:
    @staticmethod
    def evaluate_transition(transition) -> PredictedState:
        return PredictedState(
            state=transition.next_state,
            confidence=transition.probability,
            action=transition.action,
            rationale=transition.rationale,
        )

    @staticmethod
    def rollout_confidence(predictions: tuple[PredictedState, ...]) -> float:
        if not predictions:
            return 1.0
        confidence = 1.0
        for prediction in predictions:
            confidence *= prediction.confidence
        return confidence
