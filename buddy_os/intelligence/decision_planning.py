"""Small, transparent decision-planning primitives for Buddy.

Plans are scored as decision-support candidates. Execution remains outside
this module and must pass the application's authorization/safety controls.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PlanStep:
    step_id: str
    description: str
    probability: float = 1.0
    utility: float = 0.0
    cost: float = 0.0
    reversible: bool = True

    def __post_init__(self) -> None:
        if not 0.0 <= self.probability <= 1.0:
            raise ValueError("probability must be between 0 and 1")
        if self.cost < 0:
            raise ValueError("cost cannot be negative")


@dataclass(frozen=True)
class DecisionPlan:
    plan_id: str
    steps: tuple[PlanStep, ...]


class DecisionPlanner:
    @staticmethod
    def expected_utility(plan: DecisionPlan) -> float:
        value = 0.0
        for step in plan.steps:
            value += step.probability * step.utility - step.cost
        return value

    @staticmethod
    def reversibility(plan: DecisionPlan) -> float:
        if not plan.steps:
            return 1.0
        return sum(step.reversible for step in plan.steps) / len(plan.steps)

    def rank(self, plans: tuple[DecisionPlan, ...] | list[DecisionPlan]) -> tuple[DecisionPlan, ...]:
        return tuple(sorted(plans, key=lambda p: (-self.expected_utility(p), -self.reversibility(p), p.plan_id)))
