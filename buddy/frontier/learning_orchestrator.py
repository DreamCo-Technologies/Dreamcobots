"""Deterministic capability-learning orchestration primitives.

This module intentionally does not train models or auto-close production work by
itself. It creates auditable learning jobs from benchmark failures and requires
independent validation before a capability is promoted.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Iterable


class LearningAction(str, Enum):
    RETRIEVE = "retrieve"
    TOOL = "tool"
    TRAIN = "train"
    REVERSE_ENGINEER = "reverse_engineer"
    DISTILL = "distill"
    DIAGNOSE = "diagnose"
    ROUTING = "routing"
    ARCHITECTURE = "architecture"
    HUMAN_REVIEW = "human_review"


@dataclass(frozen=True)
class EvaluationFailure:
    evaluation_id: str
    capability: str
    failure_mode: str
    baseline_score: float
    current_score: float
    external_assistance_used: bool = False
    evidence_refs: tuple[str, ...] = ()
    system_area: str = ""


@dataclass
class LearningJob:
    capability: str
    action: LearningAction
    source_failures: list[str] = field(default_factory=list)
    regression_tests: list[str] = field(default_factory=list)
    held_out_required: bool = True
    status: str = "proposed"
    proposed_steps: list[str] = field(default_factory=list)
    execution_started: bool = False
    source_code_copied: bool = False
    model_weights_changed: bool = False


def propose_learning_jobs(failures: Iterable[EvaluationFailure]) -> list[LearningJob]:
    """Cluster failures by capability/failure mode into bounded learning jobs."""
    groups: dict[tuple[str, str, str], LearningJob] = {}
    for failure in failures:
        key = (failure.capability, failure.failure_mode, failure.system_area)
        job = groups.get(key)
        if job is None:
            mode = failure.failure_mode.lower()
            capability = failure.capability.lower()
            area = failure.system_area.lower()
            if area in {"code", "repository", "source_tracking", "provenance"} or any(token in mode for token in ("trace", "tracking", "provenance", "missing_evidence", "unknown_code_path", "code_path")) or any(
                token in capability for token in ("code", "coding", "software", "repository", "source_navigation")
            ):
                action = LearningAction.REVERSE_ENGINEER
                steps = [
                    "Pin the failing commit, benchmark version, run ID, and capability signature.",
                    "Trace the tested behavior through modules, manifests, routes, training logs, and artifact hashes; record file-and-line evidence.",
                    "Reproduce the gap with a synthetic fixture and isolate the smallest failing path.",
                    "Write a DreamCo-specific repair and regression test; do not copy third-party protected source.",
                    "Retest on a fresh holdout and confirm the code, dataset, and checkpoint provenance chain.",
                ]
            elif area in {"training", "model_training", "distillation", "checkpoint"} or any(token in mode for token in ("distill", "training", "model_quality", "adapter", "checkpoint", "underfit", "overfit", "training_loss")) or any(
                token in capability for token in ("training", "distill", "model_quality", "checkpoint", "training_data")
            ):
                action = LearningAction.DISTILL
                steps = [
                    "Inspect baseline, training configuration, hardware, data rights, teacher terms, and checkpoint hashes.",
                    "Diagnose with a small reproducible experiment and an unchanged held-out evaluation set.",
                    "Prepare a candidate distillation or training run only for a user-owned student and explicitly licensed/consented data and teacher outputs.",
                    "Do not start training until the separate approval, compute, budget, and data-permission gates pass.",
                    "Compare three repeated evaluations, holdout, safety, regression, latency, and cost before proposing promotion.",
                ]
            elif mode.startswith("tool"):
                action = LearningAction.TOOL
                steps = ["Inspect the adapter contract and permission scope.", "Reproduce with a mock, then retest in an isolated sandbox."]
            else:
                action = LearningAction.TRAIN
                steps = ["Cluster the failure evidence.", "Create a minimal reproducible fixture.", "Propose a bounded repair and a held-out regression test."]
            job = LearningJob(capability=failure.capability, action=action, proposed_steps=steps)
            groups[key] = job
        job.source_failures.append(failure.evaluation_id)
        job.regression_tests.extend(failure.evidence_refs)
    return list(groups.values())


def can_promote(*, held_out_passed: bool, regression_passed: bool, safety_passed: bool) -> bool:
    """Promotion requires independent held-out, regression, and safety evidence."""
    return held_out_passed and regression_passed and safety_passed
