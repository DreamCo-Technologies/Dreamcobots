"""Deterministic sandbox harness for Buddy study experiments.

The sandbox is deliberately constrained: study exercises are represented as
trusted Python callables/data, not arbitrary remote code. Production changes
must never be executed by this harness.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from time import monotonic
from typing import Callable, Any


@dataclass
class SandboxResult:
    passed: bool
    score: float
    duration_ms: float
    failures: list[str] = field(default_factory=list)
    evidence: dict[str, Any] = field(default_factory=dict)


class BuddySandbox:
    def run(self, name: str, exercise: Callable[[], tuple[bool, float, list[str]]]) -> SandboxResult:
        start = monotonic()
        try:
            passed, score, failures = exercise()
            return SandboxResult(
                passed=bool(passed),
                score=max(0.0, min(1.0, float(score))),
                duration_ms=(monotonic() - start) * 1000,
                failures=list(failures),
                evidence={"exercise": name, "sandbox": "buddy-sandbox-v1"},
            )
        except Exception as exc:
            return SandboxResult(
                passed=False,
                score=0.0,
                duration_ms=(monotonic() - start) * 1000,
                failures=[f"sandbox-exception:{type(exc).__name__}"],
                evidence={"exercise": name, "sandbox": "buddy-sandbox-v1"},
            )
