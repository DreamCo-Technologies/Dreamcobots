from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
import math
from typing import Dict, List, Optional


@dataclass
class ABTest:
    name: str
    variant_a: str
    variant_b: str
    traffic_split: float
    metric: str
    duration_hours: int
    started_at: datetime = field(default_factory=datetime.utcnow)


class ABOrchestrator:
    def __init__(self) -> None:
        self.tests: Dict[str, ABTest] = {}
        self.results: Dict[str, Dict[str, List[float]]] = {}

    def start_test(self, test: ABTest) -> None:
        self.tests[test.name] = test
        self.results[test.name] = {'a': [], 'b': []}

    def assign_variant(self, test_name: str, subject_id: str) -> str:
        test = self.tests[test_name]
        threshold = int(test.traffic_split * 100)
        return 'a' if sum(map(ord, subject_id)) % 100 < threshold else 'b'

    def record_metric(self, test_name: str, variant: str, value: float) -> None:
        self.results[test_name][variant].append(value)

    def monitor(self, test_name: str) -> Dict[str, float]:
        a = self.results[test_name]['a']
        b = self.results[test_name]['b']
        return {'variant_a_mean': self._mean(a), 'variant_b_mean': self._mean(b), 'chi_squared': self._chi_squared(a, b)}

    def conclude(self, test_name: str) -> Dict[str, object]:
        test = self.tests[test_name]
        finished = datetime.utcnow() >= test.started_at + timedelta(hours=test.duration_hours)
        a = self.results[test_name]['a']
        b = self.results[test_name]['b']
        t_score = self._t_test(a, b)
        winner = test.variant_a if self._mean(a) >= self._mean(b) else test.variant_b
        return {'complete': finished, 'winner': winner, 't_score': round(t_score, 4), 'promote': finished and abs(t_score) > 1.96}

    def promote_winner(self, test_name: str) -> Optional[str]:
        result = self.conclude(test_name)
        return result['winner'] if result['promote'] else None

    def next_variant_bandit(self, test_name: str) -> str:
        pulls = self.results[test_name]
        total = len(pulls['a']) + len(pulls['b']) + 1
        scores = {}
        for variant in ('a', 'b'):
            mean_reward = self._mean(pulls[variant])
            count = max(1, len(pulls[variant]))
            scores[variant] = mean_reward + math.sqrt(2 * math.log(total) / count)
        return max(scores, key=scores.get)

    def _mean(self, values: List[float]) -> float:
        return sum(values) / len(values) if values else 0.0

    def _variance(self, values: List[float]) -> float:
        if len(values) < 2:
            return 0.0
        avg = self._mean(values)
        return sum((value - avg) ** 2 for value in values) / (len(values) - 1)

    def _t_test(self, a: List[float], b: List[float]) -> float:
        if not a or not b:
            return 0.0
        denom = math.sqrt((self._variance(a) / len(a)) + (self._variance(b) / len(b))) or 1.0
        return (self._mean(a) - self._mean(b)) / denom

    def _chi_squared(self, a: List[float], b: List[float]) -> float:
        success_a = sum(1 for value in a if value > 0)
        success_b = sum(1 for value in b if value > 0)
        total = max(1, success_a + success_b)
        expected = total / 2
        return ((success_a - expected) ** 2 + (success_b - expected) ** 2) / max(expected, 1.0)
