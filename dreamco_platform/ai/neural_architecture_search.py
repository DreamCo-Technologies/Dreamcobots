from __future__ import annotations

from dataclasses import dataclass
import math
import random
from typing import Dict, List


@dataclass
class EvaluationMetric:
    accuracy: float
    latency: float
    cost_per_token: float


@dataclass
class NASResult:
    best_architecture: Dict[str, float]
    validation_score: float
    search_iterations: int


class NASController:
    def __init__(self, seed: int = 11) -> None:
        self.random = random.Random(seed)
        self.history: List[tuple[Dict[str, float], float]] = []

    def search(self, iterations: int = 20) -> NASResult:
        best_params: Dict[str, float] = {}
        best_score = float('-inf')
        for _ in range(iterations):
            candidate = self._propose_candidate()
            score = self._evaluate(candidate)
            self.history.append((candidate, score))
            if score > best_score:
                best_params, best_score = candidate, score
        return NASResult(best_architecture=best_params, validation_score=round(best_score, 4), search_iterations=iterations)

    def _propose_candidate(self) -> Dict[str, float]:
        if len(self.history) < 3:
            return {
                'temperature': self.random.uniform(0.1, 0.9),
                'examples': self.random.randint(1, 6),
                'constraint_weight': self.random.uniform(0.0, 1.0),
            }
        top = sorted(self.history, key=lambda entry: entry[1], reverse=True)[:3]
        mean_temp = sum(item[0]['temperature'] for item in top) / len(top)
        mean_examples = sum(item[0]['examples'] for item in top) / len(top)
        mean_constraint = sum(item[0]['constraint_weight'] for item in top) / len(top)
        return {
            'temperature': min(1.0, max(0.0, self.random.gauss(mean_temp, 0.08))),
            'examples': max(1, round(self.random.gauss(mean_examples, 1.0))),
            'constraint_weight': min(1.0, max(0.0, self.random.gauss(mean_constraint, 0.12))),
        }

    def _evaluate(self, candidate: Dict[str, float]) -> float:
        accuracy = 0.65 + (1 - abs(candidate['temperature'] - 0.35)) * 0.2 + min(candidate['examples'], 6) * 0.02
        latency = 0.2 + candidate['examples'] * 0.05 + candidate['constraint_weight'] * 0.03
        cost = 0.001 + candidate['examples'] * 0.0004
        metric = EvaluationMetric(accuracy=accuracy, latency=latency, cost_per_token=cost)
        return metric.accuracy - metric.latency * 0.25 - metric.cost_per_token * 20 - math.fabs(candidate['temperature'] - 0.4) * 0.05
