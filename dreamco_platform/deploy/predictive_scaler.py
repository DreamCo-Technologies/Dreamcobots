from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, Iterable, List


@dataclass
class ScalingRecommendation:
    target_replicas: int
    scale_time: datetime
    confidence: float


class PredictiveModel:
    def __init__(self) -> None:
        self.by_hour: Dict[int, List[float]] = {}

    def fit(self, history: Iterable[dict]) -> None:
        for record in history:
            timestamp = record['timestamp']
            self.by_hour.setdefault(timestamp.hour, []).append(record['requests'])

    def forecast(self, when: datetime) -> float:
        hour_values = self.by_hour.get(when.hour, [0.0])
        base = sum(hour_values) / max(1, len(hour_values))
        prior = self.by_hour.get((when.hour - 1) % 24, hour_values)
        trend = base - (sum(prior) / max(1, len(prior)))
        return max(0.0, base + trend * 0.5)


class PredictiveScaler:
    def __init__(self, requests_per_replica: int = 120) -> None:
        self.model = PredictiveModel()
        self.requests_per_replica = requests_per_replica

    def train(self, history: Iterable[dict]) -> None:
        self.model.fit(history)

    def recommend(self, at_time: datetime) -> ScalingRecommendation:
        predicted = self.model.forecast(at_time + timedelta(minutes=15))
        replicas = max(1, int(predicted / self.requests_per_replica) + 1)
        confidence = min(0.95, 0.55 + predicted / max(self.requests_per_replica * 10, 1))
        return ScalingRecommendation(replicas, at_time, round(confidence, 3))
