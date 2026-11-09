"""Bridge DreamCo Bootcamp learning routes to Buddy's task execution contract.

This adapter prepares an auditable execution request and evaluates completion
events. It does not execute tools, fetch course content, launch paid compute, or
train model weights; the existing Buddy runtime remains the execution authority.
"""
from __future__ import annotations

from dataclasses import asdict
from typing import Iterable, Mapping, Any

from buddy.bootcamp.task_learning_router import (
    LearningResource,
    TaskRequest,
    build_learning_route,
)

REQUEST_SCHEMA = "dreamco.learning_execution_request.v1"
RESULT_SCHEMA = "dreamco.learning_execution_result.v1"


def prepare_learning_execution(
    task: TaskRequest,
    resources: Iterable[LearningResource],
    *,
    request_id: str,
    task_id: str,
    sandbox_profile: str,
    allowed_tools: Iterable[str] = (),
    source_rights_refs: Iterable[str] = (),
    original_lesson_id: str | None = None,
    practice_task_ids: Iterable[str] = (),
    benchmark_ids: Iterable[str] = (),
    compute_budget_usd: float = 0.0,
    time_budget_seconds: int = 300,
    approval_requirements: Iterable[str] = (),
) -> dict[str, Any]:
    """Create a packet for Buddy's existing authorized execution runtime."""
    route = build_learning_route(task, resources)
    if route["status"] != "route_ready":
        return {
            "schema": REQUEST_SCHEMA,
            "request_id": request_id,
            "task_id": task_id,
            "status": "blocked",
            "reason": route.get("next_action", "no_eligible_learning_resource"),
            "route": route,
            "execution_started": False,
            "weights_trained": False,
        }
    approvals = set(approval_requirements)
    selected_resource = route["selected_resource"]["resource"]
    if selected_resource.get("requires_account"):
        approvals.add("user_authorizes_external_learning_source_connection")
    if float(selected_resource.get("cost_per_hour_usd", 0.0)) > 0:
        approvals.add("user_approves_paid_learning_resource_or_compute")
    approvals = sorted(approvals)
    return {
        "schema": REQUEST_SCHEMA,
        "request_id": request_id,
        "user_goal": task.request,
        "task_id": task_id,
        "required_capabilities": list(task.skills),
        "selected_resources": [route["selected_resource"]],
        "source_rights_refs": sorted(set(source_rights_refs)),
        "original_lesson_id": original_lesson_id,
        "practice_task_ids": list(practice_task_ids),
        "benchmark_ids": list(benchmark_ids),
        "execution_mode": "sandbox",
        "sandbox_profile": sandbox_profile,
        "allowed_tools": sorted(set(allowed_tools)),
        "approval_requirements": approvals,
        "data_policy": {
            "client_data_training_default": False,
            "unknown_rights_blocked": True,
            "external_access_requires_consent": True,
        },
        "compute_budget": {"max_cost_usd": max(0.0, float(compute_budget_usd))},
        "time_budget": {"max_seconds": max(1, int(time_budget_seconds))},
        "expected_artifacts": ["execution_report", "test_results", "provenance_record"],
        "acceptance_criteria": [
            "task_specific_benchmark_pass",
            "unseen_transfer_task_pass",
            "regression_pass",
            "safety_pass",
        ],
        "rollback_plan": "discard sandbox changes and preserve failure evidence",
        "route": route,
        "status": "awaiting_user_approval" if approvals else "proposed",
        "execution_started": False,
        "training_started": False,
        "weights_trained": False,
    }


def evaluate_learning_completion(event: Mapping[str, Any]) -> dict[str, Any]:
    """Validate a runtime completion event and derive a conservative promotion result."""
    from buddy.learning.continuous_learning_controller import (
        EventType,
        LearningEvent,
        evaluate_event,
    )

    required = (
        "request_id", "run_id", "status", "capability", "success", "verified",
        "regression_passed", "safety_passed",
    )
    missing = [key for key in required if key not in event]
    if missing:
        return {
            "schema": RESULT_SCHEMA,
            "accepted": False,
            "promote": False,
            "missing_fields": missing,
            "weights_trained": False,
        }
    boolean_fields = ("success", "verified", "regression_passed", "safety_passed")
    optional_boolean_fields = ("external_assistance", "holdout_passed", "weights_trained")
    malformed = [
        key for key in boolean_fields
        if type(event[key]) is not bool
    ] + [
        key for key in optional_boolean_fields
        if key in event and type(event[key]) is not bool
    ]
    if malformed:
        return {
            "schema": RESULT_SCHEMA,
            "accepted": False,
            "promote": False,
            "reason": "boolean_fields_must_be_json_booleans",
            "invalid_fields": malformed,
            "weights_trained": False,
        }
    try:
        event_type = EventType(str(event.get("event_type", "tool_outcome")))
    except ValueError:
        return {
            "schema": RESULT_SCHEMA,
            "accepted": False,
            "promote": False,
            "reason": "unknown_event_type",
            "weights_trained": False,
        }
    learning_event = LearningEvent(
        event_id=str(event["run_id"]),
        event_type=event_type,
        capability=str(event["capability"]),
        success=event["success"],
        verified=event["verified"],
        regression_passed=event["regression_passed"],
        safety_passed=event["safety_passed"],
        external_assistance=event.get("external_assistance", False),
    )
    decision = evaluate_event(learning_event)
    holdout_passed = event.get("holdout_passed", False)
    promote = bool(decision.promote and holdout_passed and event["status"] == "succeeded")
    return {
        "schema": RESULT_SCHEMA,
        "accepted": True,
        "request_id": str(event["request_id"]),
        "run_id": str(event["run_id"]),
        "status": str(event["status"]),
        "capability": str(event["capability"]),
        "learn": decision.learn,
        "promote": promote,
        "promotion_reason": (
            "verified_success_with_holdout_regression_and_safety"
            if promote else decision.reason if not decision.promote
            else "holdout_or_execution_status_blocks_promotion"
        ),
        "artifact_refs": list(event.get("artifact_refs", [])),
        "provenance_refs": list(event.get("provenance_refs", [])),
        "external_assistance": bool(event.get("external_assistance", False)),
        "training_job_id": event.get("training_job_id"),
        "weights_trained": bool(event.get("weights_trained", False)),
    }
