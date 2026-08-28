"""Small, deterministic benchmark harness for Buddy reasoning methods."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Iterable


@dataclass(frozen=True)
class BenchmarkCase:
    case_id: str
    domain: str
    prompt: str
    expected: object


@dataclass(frozen=True)
class BenchmarkResult:
    case_id: str
    method: str
    predicted: object
    correct: bool
    error: str | None = None


class ReasoningBenchmark:
    def __init__(self, cases: Iterable[BenchmarkCase]) -> None:
        self.cases = tuple(cases)

    def run(self, method: str, solver: Callable[[str], object]) -> list[BenchmarkResult]:
        results: list[BenchmarkResult] = []
        for case in self.cases:
            try:
                predicted = solver(case.prompt)
                results.append(BenchmarkResult(case.case_id, method, predicted, predicted == case.expected))
            except Exception as exc:  # benchmark harness records failures instead of hiding them
                results.append(BenchmarkResult(case.case_id, method, None, False, type(exc).__name__ + ": " + str(exc)))
        return results

    @staticmethod
    def accuracy(results: Iterable[BenchmarkResult]) -> float:
        rows = list(results)
        return sum(r.correct for r in rows) / len(rows) if rows else 0.0

    @staticmethod
    def failure_modes(results: Iterable[BenchmarkResult]) -> dict[str, int]:
        counts: dict[str, int] = {}
        for result in results:
            if result.error:
                key = result.error.split(":", 1)[0]
                counts[key] = counts.get(key, 0) + 1
        return counts
