"""Dependency reduction planner for Buddy.

It produces recommendations only. Existing DreamCo models/bots remain intact
until a separate, governed retirement process explicitly approves a change.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CapabilityRecord:
    capability: str
    native_quality: float
    native_trials: int
    external_dependencies: int
    unique_external_capability: bool = False


class DependencyReductionPlanner:
    def __init__(self, quality_threshold: float = 0.90, trial_threshold: int = 30):
        self.quality_threshold = quality_threshold
        self.trial_threshold = trial_threshold

    def recommend(self, record: CapabilityRecord) -> str:
        if record.unique_external_capability:
            return "retain-external-specialist"
        if record.native_trials < self.trial_threshold:
            return "continue-learning"
        if record.native_quality < self.quality_threshold:
            return "continue-learning"
        if record.external_dependencies == 0:
            return "buddy-native"
        return "shadow-test-buddy-native"
