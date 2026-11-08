"""Task-to-learning router for the Buddy Bootcamp.

This module ranks registered learning resources for a requested task and emits
an auditable study/practice plan. It does not scrape courses, bypass logins,
launch paid compute, or claim that a provider integration was executed.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
import re
from typing import Iterable, Sequence


@dataclass(frozen=True)
class LearningResource:
    id: str
    name: str
    url: str
    skills: tuple[str, ...]
    modes: tuple[str, ...] = ("read", "practice")
    access: str = "free"
    quality: float = 0.7
    cost_per_hour_usd: float = 0.0
    requires_account: bool = False
    supports_execution: bool = False
    license_review_required: bool = True
    provider_kind: str = "course"


@dataclass(frozen=True)
class TaskRequest:
    request: str
    skills: tuple[str, ...]
    preferred_mode: str = "practice"
    max_cost_per_hour_usd: float = 0.0
    allow_paid: bool = False
    allow_external_access: bool = False


def _tokens(value: str) -> set[str]:
    return {token for token in re.findall(r"[a-z0-9+#.]+", value.lower()) if len(token) > 1}


def _skill_overlap(requested: Sequence[str], offered: Sequence[str]) -> float:
    wanted = set().union(*(_tokens(item) for item in requested)) if requested else set()
    available = set().union(*(_tokens(item) for item in offered)) if offered else set()
    return len(wanted & available) / max(1, len(wanted))


def rank_resources(task: TaskRequest, resources: Iterable[LearningResource]) -> list[dict]:
    """Rank eligible resources; paid and external access are opt-in."""
    ranked = []
    for resource in resources:
        if resource.cost_per_hour_usd > task.max_cost_per_hour_usd:
            continue
        if resource.cost_per_hour_usd > 0 and not task.allow_paid:
            continue
        if resource.requires_account and not task.allow_external_access:
            continue
        overlap = _skill_overlap(task.skills, resource.skills)
        if task.skills and overlap == 0:
            continue
        mode_fit = 1.0 if task.preferred_mode in resource.modes else 0.55
        execution_fit = 1.0 if resource.supports_execution else 0.0
        # Quality and task relevance dominate; price is a small tie-breaker.
        score = (0.55 * overlap) + (0.25 * resource.quality) + (0.15 * mode_fit) + (0.05 * execution_fit)
        ranked.append({
            "resource": asdict(resource),
            "relevance": round(overlap, 4),
            "score": round(score, 4),
            "requires_user_connection": resource.requires_account,
            "execution_verified": False,
        })
    return sorted(ranked, key=lambda item: (-item["score"], item["resource"]["cost_per_hour_usd"], item["resource"]["id"]))


def build_learning_route(task: TaskRequest, resources: Iterable[LearningResource]) -> dict:
    ranked = rank_resources(task, resources)
    if not ranked:
        return {
            "schema": "dreamco.task_learning_route.v1",
            "status": "no_eligible_resource",
            "task": task.request,
            "missing_skills": list(task.skills),
            "next_action": "discover_or_register_a_rights_cleared_resource",
            "training_started": False,
        }
    return {
        "schema": "dreamco.task_learning_route.v1",
        "status": "route_ready",
        "task": task.request,
        "skills": list(task.skills),
        "selected_resource": ranked[0],
        "alternatives": ranked[1:4],
        "course_plan": [
            "confirm_resource_access_and_license",
            "retrieve_authorized_learning_material",
            "extract_skill_objectives_and_prerequisites",
            "create_original_task_specific_lesson",
            "practice_in_isolated_sandbox",
            "run_targeted_benchmark",
            "run_unseen_holdout_without_training_on_it",
            "run_regression_and_safety_checks",
            "record_evidence_cost_latency_and_provenance",
        ],
        "training_started": False,
        "execution_verified": False,
        "promotion_requires": ["three_repeated_successful_runs", "unseen_holdout_pass", "cross_domain_transfer", "no_critical_regression"],
    }
