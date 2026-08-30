"""Deterministic benchmark progress calculations for Buddy learning evidence."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class BenchmarkResult:
    capability_id: str
    passed: bool
    external_dependency: bool = False


def progress(results: list[BenchmarkResult]) -> dict[str, float]:
    if not results:
        return {"attempts": 0.0, "pass_rate": 0.0, "native_pass_rate": 0.0}
    passed = [r for r in results if r.passed]
    native = [r for r in results if r.passed and not r.external_dependency]
    return {
        "attempts": float(len(results)),
        "pass_rate": len(passed) / len(results),
        "native_pass_rate": len(native) / len(results),
    }


def mastery_ready(results: list[BenchmarkResult], minimum_passes: int = 3) -> bool:
    """Require repeated passes before a capability is treated as mastered."""
    if not results:
        return False
    by_capability: dict[str, list[BenchmarkResult]] = {}
    for result in results:
        by_capability.setdefault(result.capability_id, []).append(result)
    return all(
        sum(r.passed and not r.external_dependency for r in capability_results) >= minimum_passes
        for capability_results in by_capability.values()
    )
