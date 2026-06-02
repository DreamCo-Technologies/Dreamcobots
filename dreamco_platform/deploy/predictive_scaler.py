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

def predict_series(self, start: datetime, periods: int = 4, interval_minutes: int = 15) -> List[float]:
    return [
        round(self.model.forecast(start + timedelta(minutes=interval_minutes * index)), 2)
        for index in range(periods)
    ]


def scale_plan_for_day(self, start: datetime) -> List[ScalingRecommendation]:
    recommendations = []
    for hour in range(0, 24, 6):
        moment = start + timedelta(hours=hour)
        recommendations.append(self.recommend(moment))
    return recommendations


PredictiveScaler.predict_series = predict_series
PredictiveScaler.scale_plan_for_day = scale_plan_for_day
