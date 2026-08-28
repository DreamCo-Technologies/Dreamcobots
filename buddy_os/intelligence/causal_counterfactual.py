"""Counterfactual scenario records for Buddy's causal reasoning.

Counterfactuals are represented as hypotheses about alternate worlds. This
module does not claim the alternate outcome is factual and never executes an
intervention.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CounterfactualScenario:
    scenario_id: str
    observed_state: tuple[tuple[str, str], ...]
    intervention: tuple[str, str]
    predicted_outcome: str
    confidence: float
    assumptions: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("confidence must be between 0 and 1")
        if not self.intervention[0] or not self.predicted_outcome.strip():
            raise ValueError("intervention and predicted outcome are required")


class CounterfactualLedger:
    def __init__(self) -> None:
        self._scenarios: dict[str, CounterfactualScenario] = {}

    def record(self, scenario: CounterfactualScenario) -> None:
        if scenario.scenario_id in self._scenarios:
            raise ValueError(f"duplicate scenario: {scenario.scenario_id}")
        self._scenarios[scenario.scenario_id] = scenario

    def get(self, scenario_id: str) -> CounterfactualScenario | None:
        return self._scenarios.get(scenario_id)

    def scenarios_for_variable(self, variable: str) -> tuple[CounterfactualScenario, ...]:
        return tuple(s for s in self._scenarios.values() if s.intervention[0] == variable)
