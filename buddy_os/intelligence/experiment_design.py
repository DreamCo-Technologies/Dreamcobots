"""Reproducible experiment design primitives for Buddy.

Experiments describe what may be tested; they do not execute experiments or
bypass action authorization. Designed to support hypothesis-driven learning.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class Experiment:
    experiment_id: str
    objective: str
    hypotheses: tuple[str, ...]
    variables: tuple[str, ...]
    controls: tuple[str, ...] = ()
    expected_outcomes: tuple[str, ...] = ()
    stopping_criteria: tuple[str, ...] = ()
    safety_constraints: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.objective.strip():
            raise ValueError("objective cannot be empty")
        if not self.hypotheses:
            raise ValueError("at least one hypothesis is required")
        if not self.variables:
            raise ValueError("at least one variable is required")


class ExperimentDesigner:
    def __init__(self) -> None:
        self.experiments: dict[str, Experiment] = {}

    def register(self, experiment: Experiment) -> None:
        if experiment.experiment_id in self.experiments:
            raise ValueError(f"duplicate experiment: {experiment.experiment_id}")
        self.experiments[experiment.experiment_id] = experiment

    def readiness_gaps(self, experiment: Experiment) -> tuple[str, ...]:
        gaps: list[str] = []
        if not experiment.controls:
            gaps.append("control_definition")
        if not experiment.expected_outcomes:
            gaps.append("expected_outcomes")
        if not experiment.stopping_criteria:
            gaps.append("stopping_criteria")
        if not experiment.safety_constraints:
            gaps.append("safety_constraints")
        return tuple(gaps)

    def reproducibility_key(self, experiment: Experiment) -> tuple[str, ...]:
        return (experiment.experiment_id, experiment.objective,
                *experiment.hypotheses, *experiment.variables,
                *experiment.controls, *experiment.expected_outcomes,
                *experiment.stopping_criteria, *experiment.safety_constraints)
