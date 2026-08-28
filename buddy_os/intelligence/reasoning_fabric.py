"""Reasoning-method registry and routing fabric for Buddy.

The fabric selects complementary reasoning methods; it does not assume that
consensus implies correctness. Methods remain auditable and can be benchmarked
against outcomes before their historical reliability is used for routing.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable


@dataclass(frozen=True)
class ReasoningMethod:
    name: str
    domains: frozenset[str]
    strengths: frozenset[str]
    cost: float = 1.0
    requires_verification: bool = True


@dataclass(frozen=True)
class ReasoningPlan:
    problem_type: str
    methods: tuple[ReasoningMethod, ...]
    rationale: tuple[str, ...]


DEFAULT_METHODS = (
    ReasoningMethod("deductive", frozenset({"logic", "rules", "verification"}), frozenset({"proof", "guarantees"})),
    ReasoningMethod("inductive", frozenset({"learning", "pattern"}), frozenset({"generalization"})),
    ReasoningMethod("abductive", frozenset({"diagnosis", "causal"}), frozenset({"explanation"})),
    ReasoningMethod("causal", frozenset({"causal", "systems", "diagnosis"}), frozenset({"intervention", "root-cause"})),
    ReasoningMethod("probabilistic", frozenset({"uncertainty", "prediction"}), frozenset({"uncertainty"})),
    ReasoningMethod("temporal", frozenset({"temporal", "planning"}), frozenset({"sequence", "change"})),
    ReasoningMethod("counterfactual", frozenset({"causal", "planning"}), frozenset({"what-if"})),
    ReasoningMethod("spatial", frozenset({"geometry", "navigation", "vision"}), frozenset({"location", "shape"})),
    ReasoningMethod("constraint", frozenset({"optimization", "planning", "engineering"}), frozenset({"feasibility"})),
    ReasoningMethod("optimization", frozenset({"optimization", "planning", "resource"}), frozenset({"best-choice"}), cost=2.0),
    ReasoningMethod("simulation", frozenset({"planning", "systems", "risk"}), frozenset({"forecast", "stress-test"}), cost=3.0),
    ReasoningMethod("adversarial", frozenset({"security", "verification", "strategy"}), frozenset({"red-team"}), cost=2.0),
    ReasoningMethod("formal-verification", frozenset({"verification", "software", "logic"}), frozenset({"correctness"}), cost=3.0),
    ReasoningMethod("metacognitive", frozenset({"all"}), frozenset({"uncertainty", "self-critique"})),
)


class ReasoningFabric:
    def __init__(self, methods: Iterable[ReasoningMethod] = DEFAULT_METHODS) -> None:
        self.methods = tuple(methods)
        self.history: list[ReasoningPlan] = []

    def route(self, problem_type: str, required_domains: Iterable[str] = ()) -> ReasoningPlan:
        domains = set(required_domains) | {problem_type}
        selected = [m for m in self.methods if "all" in m.domains or m.domains & domains]
        selected.sort(key=lambda m: (m.name == "metacognitive", m.cost))
        if not any(m.name == "metacognitive" for m in selected):
            selected.append(next(m for m in self.methods if m.name == "metacognitive"))
        rationale = tuple(f"{m.name}: matches {sorted(m.domains & domains)}" for m in selected)
        plan = ReasoningPlan(problem_type, tuple(selected), rationale)
        self.history.append(plan)
        return plan
