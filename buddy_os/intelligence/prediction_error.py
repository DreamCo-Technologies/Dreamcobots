"""Prediction-vs-observation tracking for Buddy's learning loop."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List


@dataclass(frozen=True)
class PredictionRecord:
    prediction_id: str
    predicted: float
    observed: float
    context: Dict[str, str]

    @property
    def absolute_error(self) -> float:
        return abs(self.observed - self.predicted)

    @property
    def signed_error(self) -> float:
        return self.observed - self.predicted


class PredictionLedger:
    def __init__(self) -> None:
        self.records: List[PredictionRecord] = []

    def record(self, prediction_id: str, predicted: float, observed: float, context: Dict[str, str] | None = None) -> PredictionRecord:
        item = PredictionRecord(prediction_id, predicted, observed, dict(context or {}))
        self.records.append(item)
        return item

    def mean_absolute_error(self) -> float:
        if not self.records:
            return 0.0
        return sum(item.absolute_error for item in self.records) / len(self.records)
