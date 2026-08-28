"""Buddy capability self-sufficiency engine.

Purpose: turn successful work performed with external models/bots into
validated Buddy-native skills. This is an evidence loop, not uncontrolled
self-modification: promotion requires repeated evaluation and retirement of
an external dependency is only a recommendation until policy approves it.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from statistics import mean


@dataclass
class CapabilityEvidence:
    capability: str
    source: str
    success: bool
    quality: float
    latency_ms: float = 0.0
    cost: float = 0.0
    tests_passed: int = 0
    tests_total: int = 0

    @property
    def test_rate(self) -> float:
        return self.tests_passed / self.tests_total if self.tests_total else 0.0


@dataclass
class CapabilityState:
    capability: str
    external_dependencies: set[str] = field(default_factory=set)
    native_scores: list[float] = field(default_factory=list)
    evidence_count: int = 0
    native_ready: bool = False


class CapabilityMastery:
    """Tracks whether Buddy can replace an external dependency safely."""

    def __init__(self, minimum_trials: int = 30, quality_threshold: float = 0.90):
        self.minimum_trials = minimum_trials
        self.quality_threshold = quality_threshold
        self.states: dict[str, CapabilityState] = {}

    def observe(self, evidence: CapabilityEvidence) -> None:
        state = self.states.setdefault(evidence.capability, CapabilityState(evidence.capability))
        state.evidence_count += 1
        if evidence.source != "buddy-native":
            state.external_dependencies.add(evidence.source)
        elif evidence.success:
            state.native_scores.append(evidence.quality)

        if (
            len(state.native_scores) >= self.minimum_trials
            and mean(state.native_scores[-self.minimum_trials :]) >= self.quality_threshold
        ):
            state.native_ready = True

    def dependency_report(self) -> dict[str, dict[str, object]]:
        return {
            capability: {
                "native_ready": state.native_ready,
                "external_dependencies": sorted(state.external_dependencies),
                "native_trials": len(state.native_scores),
                "native_quality": round(mean(state.native_scores), 4) if state.native_scores else 0.0,
                "recommendation": (
                    "migrate-to-buddy-native" if state.native_ready else "keep-teachers-and-validate"
                ),
            }
            for capability, state in self.states.items()
        }

    def can_replace(self, capability: str, dependency: str) -> bool:
        state = self.states.get(capability)
        return bool(state and state.native_ready and dependency in state.external_dependencies)
