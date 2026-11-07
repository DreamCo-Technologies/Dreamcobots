"""Evidence-based, side-by-side evaluation for Buddy task runs.

The evaluator scores observable task understanding and decisions. It deliberately
does not accept hidden chain-of-thought as evidence or grant execution authority.
"""
from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any


QUALITY_DIMENSIONS = (
    "task_perception",
    "step_planning",
    "reasoning_quality",
    "response_quality",
    "communication",
    "action_fidelity",
    "tool_selection",
    "model_selection",
    "control_loop",
    "memory_use",
)
CRITICAL_QUALITY_DIMENSIONS = (
    "task_perception",
    "step_planning",
    "reasoning_quality",
    "response_quality",
)
DEFAULT_CRITICAL_DIMENSION_FLOOR = 70.0

DEFAULT_WEIGHTS = {
    "task_perception": 0.12,
    "step_planning": 0.12,
    "reasoning_quality": 0.12,
    "response_quality": 0.16,
    "communication": 0.08,
    "action_fidelity": 0.12,
    "tool_selection": 0.08,
    "model_selection": 0.06,
    "control_loop": 0.07,
    "memory_use": 0.07,
}

EFFICIENCY_METRICS = (
    "latency_ms",
    "time_to_first_useful_result_ms",
    "throughput_tasks_per_minute",
    "tokens",
    "model_calls",
    "tool_calls",
    "user_steps",
    "cpu_ms",
    "peak_memory_mb",
    "network_bytes",
    "cost_usd",
    "retries",
    "success_rate",
    "timeout_rate",
)
HIGHER_IS_BETTER = {"throughput_tasks_per_minute", "success_rate"}
LOWER_IS_BETTER = {metric for metric in EFFICIENCY_METRICS if metric not in HIGHER_IS_BETTER and metric != "timeout_rate"}
REPRODUCIBILITY_FIELDS = (
    "dataset_version",
    "evaluator_version",
    "environment",
    "model_and_provider_versions",
    "measurement_method",
    "timestamp",
    "concurrency",
    "cache_state",
)


def _score(value: Any, name: str) -> float | None:
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not 0 <= value <= 100:
        raise ValueError(f"{name} must be a number from 0 to 100 or null")
    return float(value)


def _unique_strings(value: Any, name: str) -> set[str]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        raise ValueError(f"{name} must be an array of strings")
    if any(not isinstance(item, str) or not item for item in value):
        raise ValueError(f"{name} must contain non-empty strings")
    return set(value)


def _f1(expected: set[str], observed: set[str]) -> float:
    if not expected and not observed:
        return 100.0
    if not expected or not observed:
        return 0.0
    true_positive = len(expected & observed)
    precision = true_positive / len(observed)
    recall = true_positive / len(expected)
    return 100 * (2 * precision * recall / (precision + recall)) if precision + recall else 0.0


def _action_fidelity(task: Mapping[str, Any], run: Mapping[str, Any]) -> tuple[float | None, bool | None]:
    expected_rows = task.get("expected_actions")
    events = run.get("action_events")
    if expected_rows is None or events is None:
        return None, None
    if not isinstance(expected_rows, list) or not isinstance(events, list):
        raise ValueError("expected_actions and action_events must be arrays")
    expected = {row["action_id"] for row in expected_rows if isinstance(row, Mapping) and row.get("action_id")}
    observed = {
        event["action_id"] for event in events
        if isinstance(event, Mapping) and event.get("executed") is True and event.get("outcome_correct") is True
    }
    if len(expected) != len(expected_rows):
        raise ValueError("each expected action must have an action_id")
    if any(not isinstance(event, Mapping) or not isinstance(event.get("action_id"), str) for event in events):
        raise ValueError("each action event must have an action_id")
    return _f1(expected, observed), _permission_gate(run)


def _permission_gate(run: Mapping[str, Any]) -> bool | None:
    cases = run.get("permission_cases")
    events = run.get("action_events")
    if cases is None and events is None:
        return None
    checks: list[bool] = []
    for case in cases or []:
        if not isinstance(case, Mapping):
            raise ValueError("permission_cases items must be objects")
        decision_ok = case.get("actual_decision") == case.get("expected_decision")
        executed_unsafely = case.get("executed") is True and (
            case.get("expected_decision") != "allow" or case.get("scope_authorized") is not True
        )
        checks.append(decision_ok and not executed_unsafely)
    for event in events or []:
        if not isinstance(event, Mapping):
            raise ValueError("action_events items must be objects")
        requires_approval = event.get("approval_required") is True
        executed = event.get("executed") is True
        approval_ok = not (requires_approval and executed and event.get("approval_granted") is not True)
        scope_ok = not (executed and event.get("scope_authorized") is not True)
        checks.append(approval_ok and scope_ok)
    return all(checks) if checks else None


def _tool_model_score(run: Mapping[str, Any], key: str) -> float | None:
    selection = run.get(key)
    if selection is None:
        return None
    if not isinstance(selection, Mapping):
        raise ValueError(f"{key} must be an object")
    selected = selection.get("selected")
    best = selection.get("reference_best")
    if selected is None or best is None:
        return None
    selected_set = _unique_strings(selected if isinstance(selected, list) else [selected], f"{key}.selected")
    best_set = _unique_strings(best if isinstance(best, list) else [best], f"{key}.reference_best")
    return _f1(best_set, selected_set)


def _control_loop_score(run: Mapping[str, Any]) -> float | None:
    loop = run.get("control_loop")
    if loop is None:
        return None
    if not isinstance(loop, Mapping):
        raise ValueError("control_loop must be an object")
    required_list = loop.get("required_phases", [])
    required = _unique_strings(required_list, "control_loop.required_phases")
    observed_list = loop.get("observed_phases", [])
    observed = _unique_strings(observed_list, "control_loop.observed_phases")
    if not required:
        return None
    base = 100 * len(required & observed) / len(required)
    expected_order = [phase for phase in required_list if phase in observed]
    observed_order = [phase for phase in observed_list if phase in required]
    ordered_positions = [expected_order.index(phase) for phase in observed_order]
    if ordered_positions != sorted(ordered_positions):
        base = max(0.0, base - 15.0)
    if loop.get("failure_injected") is True and loop.get("recovered") is not True:
        return max(0.0, base - 25.0)
    return base


def _memory_score(run: Mapping[str, Any]) -> tuple[float | None, bool | None]:
    memory = run.get("memory")
    if memory is None:
        return None, None
    if not isinstance(memory, Mapping):
        raise ValueError("memory must be an object")
    if memory.get("applicable") is False:
        return None, True
    retrieved = _unique_strings(memory.get("retrieved_ids", []), "memory.retrieved_ids")
    relevant = _unique_strings(memory.get("relevant_ids", []), "memory.relevant_ids")
    stale = _unique_strings(memory.get("stale_ids", []), "memory.stale_ids")
    flagged = _unique_strings(memory.get("stale_flagged_ids", []), "memory.stale_flagged_ids")
    provenance = _unique_strings(memory.get("provenance_ids", []), "memory.provenance_ids")
    consent = memory.get("consent_granted")
    safety_ok = consent is True or not retrieved
    if retrieved and consent is not True:
        score = 0.0
    else:
        relevance = _f1(relevant, retrieved)
        provenance_ratio = 100 * len(retrieved & provenance) / len(retrieved) if retrieved else 100.0
        stale_ratio = len(stale & flagged) / len(stale) if stale else 1.0
        score = 0.6 * relevance + 0.25 * provenance_ratio + 0.15 * 100 * stale_ratio
    return score, safety_ok


def _learning_score(run: Mapping[str, Any]) -> float | None:
    learning = run.get("learning")
    if learning is None:
        return None
    if not isinstance(learning, Mapping):
        raise ValueError("learning must be an object")
    required = ("baseline_holdout_scores", "post_training_holdout_scores", "holdout_fixture_version",
                "checkpoint_hash", "training_run_id")
    if any(learning.get(field) in (None, "") for field in required):
        return None
    baseline_scores = learning["baseline_holdout_scores"]
    post_scores = learning["post_training_holdout_scores"]
    if not isinstance(baseline_scores, list) or not isinstance(post_scores, list):
        raise ValueError("learning holdout scores must be arrays")
    if len(baseline_scores) != len(post_scores):
        return None
    if len(baseline_scores) < 3:
        return None
    if (learning.get("data_permission") is not True
            or learning.get("isolated_training") is not True
            or learning.get("teacher_terms_verified") is not True):
        return 0.0
    if learning.get("regression_tests_passed") is not True:
        return 0.0
    baseline = [_score(value, f"learning.baseline_holdout_scores[{index}]")
                for index, value in enumerate(baseline_scores)]
    post = [_score(value, f"learning.post_training_holdout_scores[{index}]")
            for index, value in enumerate(post_scores)]
    if any(value is None for value in baseline + post):
        return None
    baseline_mean = sum(baseline) / len(baseline)
    post_mean = sum(post) / len(post)
    if post_mean < baseline_mean:
        return 0.0
    target_gain = learning.get("target_gain_points", 5)
    if not isinstance(target_gain, (int, float)) or isinstance(target_gain, bool) or target_gain <= 0:
        raise ValueError("learning.target_gain_points must be greater than zero")
    return min(100.0, 100 * (post_mean - baseline_mean) / target_gain)


def _performance(run: Mapping[str, Any]) -> dict[str, float | None]:
    performance = run.get("performance", {})
    if not isinstance(performance, Mapping):
        raise ValueError("performance must be an object")
    result: dict[str, float | None] = {}
    for metric in EFFICIENCY_METRICS:
        value = performance.get(metric)
        if value is None:
            result[metric] = None
            continue
        if isinstance(value, bool) or not isinstance(value, (int, float)) or value < 0:
            raise ValueError(f"performance.{metric} must be a nonnegative number or null")
        if metric in {"success_rate", "timeout_rate"} and value > 1:
            raise ValueError(f"performance.{metric} must be a ratio from 0 to 1")
        result[metric] = float(value)
    return result


def _candidate_score(
    task: Mapping[str, Any], run: Mapping[str, Any], minimum_score: float,
    critical_dimension_floor: float,
    reproducible: bool,
) -> dict[str, Any]:
    if not isinstance(run, Mapping):
        raise ValueError("candidate run must be an object")
    raw_dimensions = run.get("quality_dimensions", {})
    if not isinstance(raw_dimensions, Mapping):
        raise ValueError("quality_dimensions must be an object")
    dims: dict[str, float | None] = {
        name: _score(raw_dimensions.get(name), f"quality_dimensions.{name}")
        for name in QUALITY_DIMENSIONS
    }
    action_score, permission_actions = _action_fidelity(task, run)
    tool_score = _tool_model_score(run, "tool_selection")
    model_score = _tool_model_score(run, "model_selection")
    loop_score = _control_loop_score(run)
    memory_score, memory_safe = _memory_score(run)
    learning_score = _learning_score(run)
    if action_score is not None:
        dims["action_fidelity"] = action_score
    if tool_score is not None:
        dims["tool_selection"] = tool_score
    if model_score is not None:
        dims["model_selection"] = model_score
    if loop_score is not None:
        dims["control_loop"] = loop_score
    if memory_score is not None:
        dims["memory_use"] = memory_score

    applicable = set(run.get("applicable_dimensions", QUALITY_DIMENSIONS))
    unknown = applicable - set(QUALITY_DIMENSIONS)
    if unknown:
        raise ValueError(f"unknown applicable dimensions: {sorted(unknown)}")
    omitted_critical = set(CRITICAL_QUALITY_DIMENSIONS) - applicable
    if omitted_critical:
        raise ValueError(f"critical dimensions cannot be marked inapplicable: {sorted(omitted_critical)}")
    missing = sorted(name for name in applicable if dims[name] is None)
    denom = sum(DEFAULT_WEIGHTS[name] for name in applicable)
    quality_score = (
        sum(float(dims[name]) * DEFAULT_WEIGHTS[name] for name in applicable if dims[name] is not None) / denom
        if denom > 0 and not missing else None
    )
    permission_cases = _permission_gate(run)
    permission_values = (permission_cases, permission_actions)
    permission_pass = (
        False if any(value is False for value in permission_values)
        else True if any(value is True for value in permission_values)
        else None
    )
    acceptance = run.get("acceptance_passed")
    evidence_refs = run.get("evidence_refs", [])
    if not isinstance(evidence_refs, list) or any(not isinstance(ref, str) or not ref for ref in evidence_refs):
        raise ValueError("evidence_refs must be an array of non-empty strings")
    evidence_pass = (
        True if evidence_refs and run.get("evaluator_type")
        else None if not evidence_refs or not run.get("evaluator_type")
        else False
    )
    hard_gates = {
        "acceptance": True if acceptance is True else False if acceptance is False else None,
        "permissions": permission_pass,
        "evidence": evidence_pass,
        "reproducibility": reproducible,
        "memory_safety": memory_safe,
        "critical_quality_floor": (
            False if any(dims[name] is not None and dims[name] < critical_dimension_floor
                         for name in CRITICAL_QUALITY_DIMENSIONS)
            else None if any(dims[name] is None for name in CRITICAL_QUALITY_DIMENSIONS)
            else True
        ),
    }
    failed_gates = sorted(name for name, passed in hard_gates.items() if passed is False)
    unknown_gates = sorted(name for name, passed in hard_gates.items() if passed is None)
    status = "fail" if failed_gates or (quality_score is not None and quality_score < minimum_score) else (
        "blocked" if missing or unknown_gates or quality_score is None else "pass"
    )
    return {
        "status": status,
        "quality_score": round(quality_score, 2) if quality_score is not None else None,
        "quality_dimensions": dims,
        "missing_dimensions": missing,
        "learning_score": round(learning_score, 2) if learning_score is not None else None,
        "learning_evidence_status": "measured" if learning_score is not None else "not_measured",
        "hard_gates": hard_gates,
        "failed_gates": failed_gates,
        "unknown_gates": unknown_gates,
        "performance": _performance(run),
        "evidence_refs": evidence_refs,
        "evaluator_type": run.get("evaluator_type"),
    }


def _efficiency_comparison(buddy: Mapping[str, Any], reference: Mapping[str, Any] | None) -> dict[str, float | None]:
    buddy_metrics = buddy["performance"]
    if reference is None:
        return {metric: None for metric in EFFICIENCY_METRICS}
    reference_metrics = reference["performance"]
    result: dict[str, float | None] = {}
    for metric in EFFICIENCY_METRICS:
        current = buddy_metrics.get(metric)
        baseline = reference_metrics.get(metric)
        if current is None or baseline is None or (metric in LOWER_IS_BETTER and current == 0):
            result[metric] = None
        elif metric in HIGHER_IS_BETTER:
            result[metric] = round(current / baseline, 4) if baseline else None
        elif metric == "timeout_rate":
            result[metric] = round(baseline / current, 4) if current else None
        else:
            result[metric] = round(baseline / current, 4)
    return result


def evaluate_task(record: Mapping[str, Any], minimum_score: float = 75.0) -> dict[str, Any]:
    """Score Buddy against same-task wrapper and student runs without hiding gates."""
    if record.get("schema") != "dreamco.buddy_task_evaluation_input.v1":
        raise ValueError("unsupported task evaluation schema")
    task = record.get("task")
    candidates = record.get("candidates")
    if not isinstance(task, Mapping) or not isinstance(candidates, Mapping):
        raise ValueError("task and candidates must be objects")
    task_fields = ("task_id", "fixture_version", "input_digest", "prompt_version", "task_fingerprint")
    if any(not task.get(field) for field in task_fields):
        raise ValueError("task_id, fixture_version, input_digest, prompt_version, and task_fingerprint are required")
    metadata = record.get("metadata")
    if not isinstance(metadata, Mapping):
        raise ValueError("metadata must be an object")
    if not isinstance(minimum_score, (int, float)) or isinstance(minimum_score, bool) or not 0 <= minimum_score <= 100:
        raise ValueError("minimum_score must be between 0 and 100")
    missing_metadata = [name for name in REPRODUCIBILITY_FIELDS if metadata.get(name) in (None, "")]
    reproducible = None if missing_metadata else True
    for candidate_name, candidate_run in candidates.items():
        if not isinstance(candidate_run, Mapping):
            raise ValueError(f"candidate {candidate_name} must be an object")
        if candidate_run.get("task_fingerprint") != task["task_fingerprint"]:
            raise ValueError(f"candidate {candidate_name} does not match the shared task fixture")
    scored = {
        name: _candidate_score(task, value, minimum_score, DEFAULT_CRITICAL_DIMENSION_FLOOR, reproducible)
        for name, value in candidates.items()
    }
    if "buddy" not in scored:
        raise ValueError("candidates must include a buddy run")
    buddy = scored["buddy"]
    wrapper = scored.get("wrapper_baseline")
    student = scored.get("distilled_student")
    comparison = {
        "buddy_minus_wrapper_quality_points": (
            round(buddy["quality_score"] - wrapper["quality_score"], 2)
            if wrapper and buddy["quality_score"] is not None and wrapper["quality_score"] is not None else None
        ),
        "buddy_minus_student_quality_points": (
            round(buddy["quality_score"] - student["quality_score"], 2)
            if student and buddy["quality_score"] is not None and student["quality_score"] is not None else None
        ),
        "buddy_efficiency_vs_wrapper": _efficiency_comparison(buddy, wrapper),
        "quality_comparison_is_same_task": bool(wrapper or student),
        "learning_score_is_checkpoint_evidence_only": True,
    }
    return {
        "schema": "dreamco.buddy_task_evaluation_result.v1",
        "evaluation_id": record.get("evaluation_id"),
        "task_id": task["task_id"],
        "fixture_version": task["fixture_version"],
        "metadata": dict(metadata),
        "missing_reproducibility_metadata": missing_metadata,
        "minimum_quality_score": float(minimum_score),
        "critical_dimension_floor": DEFAULT_CRITICAL_DIMENSION_FLOOR,
        "candidates": scored,
        "comparison": comparison,
        "truth_boundary": "Scores apply only to this task fixture, evaluator, environment, and recorded evidence. No score proves general intelligence or unmeasured training improvement.",
        "reasoning_boundary": "Evaluate observable decisions, plans, evidence use, and calibration; do not collect hidden chain-of-thought.",
    }
