"""Track whether Buddy's confidence matches observed outcomes."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PredictionOutcome:
    prediction_id: str
    confidence: float
    correct: bool

    def __post_init__(self) -> None:
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("confidence must be between 0 and 1")


class ConfidenceCalibrator:
    def __init__(self) -> None:
        self._outcomes: list[PredictionOutcome] = []

    def record(self, outcome: PredictionOutcome) -> None:
        self._outcomes.append(outcome)

    def accuracy(self) -> float:
        if not self._outcomes:
            return 0.0
        return sum(o.correct for o in self._outcomes) / len(self._outcomes)

    def mean_confidence(self) -> float:
        if not self._outcomes:
            return 0.0
        return sum(o.confidence for o in self._outcomes) / len(self._outcomes)

    def calibration_gap(self) -> float:
        return abs(self.mean_confidence() - self.accuracy())

    def sample_count(self) -> int:
        return len(self._outcomes)
