"""Auditable orchestration pipeline for Buddy's reasoning stack."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Iterable

from .reasoning_conflict import ReasoningConflictResolver
from .reasoning_ensemble import EnsembleResult, ReasoningEnsemble, ReasoningOpinion
from .reasoning_fabric import ReasoningFabric, ReasoningPlan


@dataclass(frozen=True)
class ReasoningPipelineResult:
    plan: ReasoningPlan
    ensemble: EnsembleResult
    conflict: Any | None
    status: str


class ReasoningPipeline:
    """Coordinate routing, independent opinions, conflict analysis and gating."""

    def __init__(self, fabric: ReasoningFabric | None = None) -> None:
        self.fabric = fabric or ReasoningFabric()
        self.ensemble = ReasoningEnsemble()
        self.conflicts = ReasoningConflictResolver()

    def run(
        self,
        problem_type: str,
        required_domains: Iterable[str],
        solvers: dict[str, Callable[[str], ReasoningOpinion]],
        prompt: str,
    ) -> ReasoningPipelineResult:
        plan = self.fabric.route(problem_type, required_domains)
        opinions: list[ReasoningOpinion] = []
        for method in plan.methods:
            solver = solvers.get(method.name)
            if solver is None:
                continue
            opinion = solver(prompt)
            if opinion.method != method.name:
                raise ValueError(f"solver returned method {opinion.method!r}; expected {method.name!r}")
            opinions.append(opinion)
        ensemble = self.ensemble.combine(opinions)
        conflict = self.conflicts.analyze(opinions)
        status = "verification_required" if ensemble.requires_verification else "candidate_ready"
        return ReasoningPipelineResult(plan, ensemble, conflict, status)
