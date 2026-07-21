# Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.
"""Learning method benchmarks for the Global AI Learning Matrix."""

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum


class LearningMethod(Enum):
    SUPERVISED = "supervised"
    UNSUPERVISED = "unsupervised"
    TRANSFER = "transfer"
    SELF_SUPERVISED = "self_supervised"
    REINFORCEMENT = "reinforcement"
    FEDERATED = "federated"
    SEMI_SUPERVISED = "semi_supervised"


@dataclass
class BenchmarkResult:
    method: LearningMethod
    accuracy: float       # 0-100
    speed_score: float    # 0-100
    cost_score: float     # 0-100 (higher = cheaper)
    use_cases: list[str] = field(default_factory=list)


_BENCHMARK_DATA: dict[LearningMethod, BenchmarkResult] = {
    LearningMethod.SUPERVISED: BenchmarkResult(
        method=LearningMethod.SUPERVISED,
        accuracy=91.5,
        speed_score=82.0,
        cost_score=60.0,
        use_cases=["image classification", "spam detection", "sentiment analysis", "fraud detection"],
    ),
    LearningMethod.UNSUPERVISED: BenchmarkResult(
        method=LearningMethod.UNSUPERVISED,
        accuracy=74.2,
        speed_score=76.0,
        cost_score=80.0,
        use_cases=["customer segmentation", "anomaly detection", "topic modeling", "data compression"],
    ),
    LearningMethod.TRANSFER: BenchmarkResult(
        method=LearningMethod.TRANSFER,
        accuracy=93.8,
        speed_score=88.0,
        cost_score=70.0,
        use_cases=["fine-tuning LLMs", "domain adaptation", "low-resource NLP", "medical imaging"],
    ),
    LearningMethod.SELF_SUPERVISED: BenchmarkResult(
        method=LearningMethod.SELF_SUPERVISED,
        accuracy=89.1,
        speed_score=78.0,
        cost_score=72.0,
        use_cases=["pretraining transformers", "contrastive learning", "masked auto-encoders"],
    ),
    LearningMethod.REINFORCEMENT: BenchmarkResult(
        method=LearningMethod.REINFORCEMENT,
        accuracy=85.4,
        speed_score=55.0,
        cost_score=40.0,
        use_cases=["game playing", "robotics", "recommendation systems", "autonomous driving"],
    ),
    LearningMethod.FEDERATED: BenchmarkResult(
        method=LearningMethod.FEDERATED,
        accuracy=83.7,
        speed_score=62.0,
        cost_score=65.0,
        use_cases=["privacy-preserving ML", "healthcare data", "mobile keyboard prediction", "cross-silo training"],
    ),
    LearningMethod.SEMI_SUPERVISED: BenchmarkResult(
        method=LearningMethod.SEMI_SUPERVISED,
        accuracy=87.6,
        speed_score=79.0,
        cost_score=75.0,
        use_cases=["label-scarce tasks", "medical record classification", "speech recognition"],
    ),
}


class LearningBenchmarks:
    """Provides benchmarks and comparisons across learning methods."""

    def __init__(self):
        self._benchmarks: dict[LearningMethod, BenchmarkResult] = dict(_BENCHMARK_DATA)

    def get_benchmark(self, method: LearningMethod) -> BenchmarkResult:
        return self._benchmarks[method]

    def list_benchmarks(self) -> list[BenchmarkResult]:
        return list(self._benchmarks.values())

    def get_best_method(self, criteria: str) -> LearningMethod:
        """Return the method with the best score for the given criteria.

        criteria: "accuracy" | "speed" | "cost"
        """
        attr_map = {"accuracy": "accuracy", "speed": "speed_score", "cost": "cost_score"}
        if criteria not in attr_map:
            raise ValueError(f"Unknown criteria '{criteria}'. Choose from: accuracy, speed, cost")
        attr = attr_map[criteria]
        return max(self._benchmarks.values(), key=lambda b: getattr(b, attr)).method

    def compare_methods(self, methods: list[LearningMethod]) -> dict:
        results = {}
        for m in methods:
            b = self._benchmarks[m]
            results[m.value] = {
                "accuracy": b.accuracy,
                "speed_score": b.speed_score,
                "cost_score": b.cost_score,
                "use_cases": b.use_cases,
            }
        return results

    def rank_methods(self) -> list[tuple[LearningMethod, float]]:
        """Return methods ranked by overall score (equal weight on accuracy, speed, cost)."""
        scored = []
        for b in self._benchmarks.values():
            overall = (b.accuracy + b.speed_score + b.cost_score) / 3.0
            scored.append((b.method, round(overall, 2)))
        return sorted(scored, key=lambda x: x[1], reverse=True)
