"""Buddy's deterministic innovation and evidence gate.

This module compares multiple architecture strategies instead of accepting the
first generated idea. Design-time scores are clearly separated from observed
test evidence so a novel concept cannot silently become a production claim.
"""

from __future__ import annotations

import hashlib
import json
import uuid
from dataclasses import asdict, dataclass, field
from typing import Any, Iterable

from dreamco_platform.ai.evolutionary_engine import EvolutionaryEngine
from dreamco_platform.orchestration.execution_runtime import ExecutionRuntime


SCORE_NAMES = ("utility", "novelty", "feasibility", "trust", "efficiency", "observability")


@dataclass(frozen=True)
class InnovationWeights:
    utility: float = 0.25
    novelty: float = 0.18
    feasibility: float = 0.18
    trust: float = 0.18
    efficiency: float = 0.11
    observability: float = 0.10

    @classmethod
    def for_mode(cls, mode: str) -> "InnovationWeights":
        modes = {
            "balanced": cls(),
            "bold": cls(utility=0.22, novelty=0.31, feasibility=0.12, trust=0.16, efficiency=0.08, observability=0.11),
            "trusted": cls(utility=0.22, novelty=0.10, feasibility=0.18, trust=0.30, efficiency=0.08, observability=0.12),
            "lean": cls(utility=0.23, novelty=0.12, feasibility=0.22, trust=0.16, efficiency=0.19, observability=0.08),
        }
        if mode not in modes:
            raise ValueError(f"Unknown innovation mode '{mode}'.")
        return modes[mode]

    def normalized(self) -> dict[str, float]:
        raw = asdict(self)
        total = sum(max(0.0, float(value)) for value in raw.values())
        if total <= 0:
            raise ValueError("Innovation weights must contain a positive value.")
        return {key: max(0.0, float(value)) / total for key, value in raw.items()}


@dataclass(frozen=True)
class InnovationRequest:
    objective: str
    audience: str
    mode: str = "balanced"
    tags: tuple[str, ...] = ()
    constraints: tuple[str, ...] = ()

    def validate(self) -> None:
        if len(self.objective.strip()) < 10:
            raise ValueError("Innovation objective must be at least ten characters.")
        if not self.audience.strip():
            raise ValueError("Innovation audience is required.")
        InnovationWeights.for_mode(self.mode)


@dataclass
class InnovationCandidate:
    candidate_id: str
    lens: str
    concept: str
    architecture: list[str]
    differentiators: list[str]
    risks: list[str]
    design_scores: dict[str, float]
    weighted_score: float = 0.0
    evidence_level: str = "design_time_heuristic"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ReleaseDecision:
    status: str
    observed_checks: dict[str, bool]
    missing_checks: list[str]
    reason: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class InnovationRun:
    run_id: str
    request: InnovationRequest
    candidates: list[InnovationCandidate]
    winner: InnovationCandidate
    design_coverage: list[dict[str, str]]
    rollback_checkpoint: dict[str, Any]
    implementation_graph: list[dict[str, Any]]
    release_gate: dict[str, Any]
    execution: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        request = asdict(self.request)
        return {
            "schema": "dreamco.buddy_innovation_run.v1",
            "run_id": self.run_id,
            "request": request,
            "candidates": [candidate.to_dict() for candidate in self.candidates],
            "winner": self.winner.to_dict(),
            "design_coverage": self.design_coverage,
            "rollback_checkpoint": self.rollback_checkpoint,
            "implementation_graph": self.implementation_graph,
            "release_gate": self.release_gate,
            "execution": self.execution,
        }


class InnovationEngine:
    """Generate, compare, challenge, and checkpoint competing designs."""

    REQUIRED_OBSERVED_CHECKS = (
        "functional_tests",
        "failure_recovery",
        "privacy_and_permissions",
        "accessibility",
        "cost_budget",
        "human_acceptance",
    )

    LENSES: dict[str, dict[str, Any]] = {
        "adaptive_experience": {
            "concept": "A mastery-aware experience that changes difficulty and presentation from observed progress.",
            "architecture": ["mastery graph", "adaptive state machine", "local learner profile", "checkpoint replay"],
            "differentiators": ["difficulty adapts without rebuilding", "progress remains explainable"],
            "risks": ["adaptation can overfit sparse behavior"],
            "scores": {"utility": 91, "novelty": 82, "feasibility": 82, "trust": 84, "efficiency": 80, "observability": 88},
        },
        "simulation_twin": {
            "concept": "A deterministic digital twin that lets users replay decisions and compare counterfactual outcomes.",
            "architecture": ["seeded world model", "event ledger", "counterfactual replay", "rollback checkpoint"],
            "differentiators": ["every outcome can be replayed", "users can compare alternate decisions"],
            "risks": ["the model can simplify real-world uncertainty"],
            "scores": {"utility": 88, "novelty": 91, "feasibility": 76, "trust": 84, "efficiency": 74, "observability": 94},
        },
        "multimodal_creator": {
            "concept": "A creator-controlled pipeline that turns one brief into interactive, visual, and narrated variants.",
            "architecture": ["asset provenance graph", "renderer adapters", "caption timeline", "consent gate"],
            "differentiators": ["one source project produces several formats", "media rights remain attached to assets"],
            "risks": ["render quality depends on configured engines"],
            "scores": {"utility": 92, "novelty": 88, "feasibility": 74, "trust": 89, "efficiency": 72, "observability": 86},
        },
        "trust_trace": {
            "concept": "A transparent build where every decision, permission, source, and rollback point is inspectable.",
            "architecture": ["decision trace", "policy gate", "content lineage", "reversible checkpoint"],
            "differentiators": ["users can inspect why Buddy acted", "unsafe actions fail closed"],
            "risks": ["additional evidence can add interface complexity"],
            "scores": {"utility": 86, "novelty": 79, "feasibility": 90, "trust": 98, "efficiency": 80, "observability": 97},
        },
        "local_first_mesh": {
            "concept": "A device-resilient runtime that works offline and activates optional engines only when useful.",
            "architecture": ["offline core", "capability adapters", "resource budget", "deterministic fallback"],
            "differentiators": ["core work survives provider outages", "cost is constrained before execution"],
            "risks": ["local devices can limit heavy media rendering"],
            "scores": {"utility": 87, "novelty": 83, "feasibility": 88, "trust": 92, "efficiency": 96, "observability": 84},
        },
        "human_ai_workbench": {
            "concept": "A collaborative workbench where Buddy proposes, users steer, and every major change is reversible.",
            "architecture": ["visible task graph", "approval checkpoints", "variant comparison", "reversible edits"],
            "differentiators": ["automation stays legible", "users can branch from any checkpoint"],
            "risks": ["too many choices can slow simple tasks"],
            "scores": {"utility": 90, "novelty": 86, "feasibility": 86, "trust": 94, "efficiency": 82, "observability": 96},
        },
    }

    TAG_MODIFIERS: dict[str, dict[str, int]] = {
        "education": {"adaptive_experience": 7, "simulation_twin": 4, "human_ai_workbench": 3},
        "game": {"simulation_twin": 7, "adaptive_experience": 5, "multimodal_creator": 3},
        "simulation": {"simulation_twin": 8, "trust_trace": 2},
        "multimodal": {"multimodal_creator": 8, "trust_trace": 3},
        "privacy": {"trust_trace": 7, "local_first_mesh": 6},
        "low_cost": {"local_first_mesh": 8, "adaptive_experience": 2},
        "accessibility": {"human_ai_workbench": 5, "adaptive_experience": 5},
    }

    CONSTRAINT_MODIFIERS: dict[str, dict[str, int]] = {
        "local_first": {"local_first_mesh": 8, "trust_trace": 2},
        "reversible": {"human_ai_workbench": 5, "trust_trace": 4, "simulation_twin": 2},
        "owner_approval_before_publish": {"trust_trace": 5, "human_ai_workbench": 3},
        "strict_cost_ceiling": {"local_first_mesh": 7, "adaptive_experience": 2},
    }

    def __init__(self, runtime: ExecutionRuntime | None = None) -> None:
        self._runtime = runtime or ExecutionRuntime(default_max_attempts=1, default_backoff_seconds=0)

    def run(self, request: InnovationRequest) -> InnovationRun:
        request.validate()
        run_id = f"innovation-{uuid.uuid4().hex[:12]}"
        holder: dict[str, InnovationRun] = {}

        def execute(ctx) -> dict[str, Any]:
            candidates = self._generate_candidates(request)
            ctx.checkpoint({"stage": "variants_generated", "candidate_ids": [item.candidate_id for item in candidates]})
            ranked = self._rank(candidates, InnovationWeights.for_mode(request.mode))
            winner = ranked[0]
            ctx.checkpoint({"stage": "winner_selected", "candidate_id": winner.candidate_id, "score": winner.weighted_score})
            coverage = self._design_coverage(winner)
            checkpoint = self._rollback_checkpoint(winner)
            graph = self._implementation_graph(winner)
            run = InnovationRun(
                run_id=run_id,
                request=request,
                candidates=ranked,
                winner=winner,
                design_coverage=coverage,
                rollback_checkpoint=checkpoint,
                implementation_graph=graph,
                release_gate={
                    "status": "observed_evidence_required",
                    "required_checks": list(self.REQUIRED_OBSERVED_CHECKS),
                    "design_score_is_not_production_evidence": True,
                    "live_external_action_taken": False,
                },
            )
            holder["run"] = run
            ctx.checkpoint({"stage": "implementation_graph_ready", "checkpoint_digest": checkpoint["digest"]})
            return run.to_dict()

        record = self._runtime.run(run_id, execute, max_attempts=1, backoff_seconds=0)
        if record.status.value != "succeeded" or "run" not in holder:
            raise RuntimeError(record.error or "Innovation loop failed without a result.")
        result = holder["run"]
        result.execution = {
            "job_id": record.job_id,
            "status": record.status.value,
            "attempts": record.attempts,
            "checkpoints": record.checkpoints,
        }
        return result

    def evaluate_release(self, observed_checks: dict[str, bool]) -> ReleaseDecision:
        normalized = {name: bool(observed_checks.get(name, False)) for name in self.REQUIRED_OBSERVED_CHECKS}
        missing = [name for name, passed in normalized.items() if not passed]
        if missing:
            return ReleaseDecision(
                status="blocked",
                observed_checks=normalized,
                missing_checks=missing,
                reason="Production remains blocked until every observed check passes.",
            )
        return ReleaseDecision(
            status="production_candidate_owner_approval_required",
            observed_checks=normalized,
            missing_checks=[],
            reason="Observed checks passed; owner approval is still required before release.",
        )

    def _generate_candidates(self, request: InnovationRequest) -> list[InnovationCandidate]:
        candidates: list[InnovationCandidate] = []
        tags = {tag.strip().lower() for tag in request.tags}
        constraints = {constraint.strip().lower() for constraint in request.constraints}
        for lens, profile in self.LENSES.items():
            scores = dict(profile["scores"])
            modifier = sum(self.TAG_MODIFIERS.get(tag, {}).get(lens, 0) for tag in tags)
            modifier += sum(
                self.CONSTRAINT_MODIFIERS.get(constraint, {}).get(lens, 0)
                for constraint in constraints
            )
            scores["utility"] = min(100, scores["utility"] + modifier)
            candidate_seed = f"{request.objective}:{request.audience}:{lens}"
            candidates.append(
                InnovationCandidate(
                    candidate_id="candidate-" + hashlib.sha256(candidate_seed.encode("utf-8")).hexdigest()[:12],
                    lens=lens,
                    concept=f"{profile['concept']} Objective: {request.objective.strip()}",
                    architecture=list(profile["architecture"]),
                    differentiators=list(profile["differentiators"]),
                    risks=list(profile["risks"]),
                    design_scores=scores,
                )
            )
        return candidates

    @staticmethod
    def _rank(candidates: Iterable[InnovationCandidate], weights: InnovationWeights) -> list[InnovationCandidate]:
        normalized = weights.normalized()
        evolution = EvolutionaryEngine()
        by_id: dict[str, InnovationCandidate] = {}
        for candidate in candidates:
            candidate.weighted_score = round(
                sum(candidate.design_scores[name] * normalized[name] for name in SCORE_NAMES),
                2,
            )
            by_id[candidate.candidate_id] = candidate
            evolution.add(candidate.candidate_id, candidate.weighted_score, 1.0, [candidate.lens])
        order = [item["name"] for item in evolution.evolve(limit=len(by_id))]
        return [by_id[str(candidate_id)] for candidate_id in order]

    @staticmethod
    def _design_coverage(candidate: InnovationCandidate) -> list[dict[str, str]]:
        architecture_text = " ".join(candidate.architecture).lower()
        requirements = {
            "offline_and_cost": ("offline", "resource budget"),
            "rollback": ("rollback", "reversible"),
            "traceability": ("trace", "lineage", "event ledger", "visible task graph"),
            "permissions": ("consent", "approval", "policy gate"),
            "adaptation": ("adaptive", "variant comparison", "counterfactual"),
        }
        return [
            {
                "area": area,
                "status": "covered" if any(term in architecture_text for term in terms) else "requires_implementation_detail",
            }
            for area, terms in requirements.items()
        ]

    @staticmethod
    def _rollback_checkpoint(candidate: InnovationCandidate) -> dict[str, Any]:
        snapshot = {
            "candidate_id": candidate.candidate_id,
            "lens": candidate.lens,
            "architecture": list(candidate.architecture),
            "design_scores": dict(candidate.design_scores),
        }
        canonical = json.dumps(snapshot, sort_keys=True, separators=(",", ":"))
        return {
            "digest": "sha256:" + hashlib.sha256(canonical.encode("utf-8")).hexdigest(),
            "snapshot": snapshot,
            "restore_rule": "restore this design before applying an unverified iteration",
        }

    @staticmethod
    def _implementation_graph(candidate: InnovationCandidate) -> list[dict[str, Any]]:
        stages = [
            ("contract", [], ["inputs", "outputs", "permissions", "success metrics"]),
            ("sandbox", ["contract"], ["deterministic fixtures", "failure injection", "cost ceiling"]),
            ("prototype", ["sandbox"], list(candidate.architecture)),
            ("evaluation", ["prototype"], list(InnovationEngine.REQUIRED_OBSERVED_CHECKS)),
            ("owner_gate", ["evaluation"], ["evidence packet", "rollback digest", "release decision"]),
        ]
        return [
            {"stage": stage, "depends_on": dependencies, "outputs": outputs}
            for stage, dependencies, outputs in stages
        ]
