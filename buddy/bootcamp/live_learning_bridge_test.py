from buddy.bootcamp.live_learning_bridge import (
    evaluate_learning_completion,
    prepare_learning_execution,
)
from buddy.bootcamp.task_learning_router import LearningResource, TaskRequest


def test_prepare_packet_is_not_execution_or_training():
    task = TaskRequest("Build a tested Python API", ("python", "api"), preferred_mode="practice")
    resources = [LearningResource(
        id="python-lab",
        name="Python API practice",
        url="https://example.org/python-api",
        skills=("python", "api"),
        supports_execution=True,
    )]
    packet = prepare_learning_execution(
        task,
        resources,
        request_id="req-1",
        task_id="task-1",
        sandbox_profile="python-isolated",
        allowed_tools=("python_tests",),
        source_rights_refs=("source-1",),
    )
    assert packet["schema"] == "dreamco.learning_execution_request.v1"
    assert packet["status"] == "proposed"
    assert packet["execution_started"] is False
    assert packet["weights_trained"] is False
    assert packet["required_capabilities"] == ["python", "api"]


def test_no_eligible_resource_blocks_packet():
    packet = prepare_learning_execution(
        TaskRequest("Build a Rust app", ("rust",)),
        [],
        request_id="req-2",
        task_id="task-2",
        sandbox_profile="restricted",
    )
    assert packet["status"] == "blocked"
    assert packet["execution_started"] is False


def test_completion_requires_holdout_in_addition_to_controller_gates():
    base = {
        "request_id": "req-3",
        "run_id": "run-3",
        "status": "succeeded",
        "capability": "python",
        "success": True,
        "verified": True,
        "regression_passed": True,
        "safety_passed": True,
    }
    without_holdout = evaluate_learning_completion(base)
    assert without_holdout["accepted"] is True
    assert without_holdout["promote"] is False
    with_holdout = evaluate_learning_completion({**base, "holdout_passed": True})
    assert with_holdout["promote"] is True
    assert with_holdout["weights_trained"] is False


def test_missing_completion_evidence_is_rejected():
    result = evaluate_learning_completion({"request_id": "req-4"})
    assert result["accepted"] is False
    assert result["promote"] is False



def test_completion_rejects_string_false_permission_evidence():
    base = {
        "request_id": "req-5",
        "run_id": "run-5",
        "status": "succeeded",
        "capability": "python",
        "success": "false",
        "verified": True,
        "regression_passed": True,
        "safety_passed": True,
        "holdout_passed": True,
    }
    result = evaluate_learning_completion(base)
    assert result["accepted"] is False
    assert result["promote"] is False
    assert result["reason"] == "boolean_fields_must_be_json_booleans"
    assert result["invalid_fields"] == ["success"]


def test_completion_rejects_malformed_optional_boolean_evidence():
    base = {
        "request_id": "req-6",
        "run_id": "run-6",
        "status": "succeeded",
        "capability": "python",
        "success": True,
        "verified": True,
        "regression_passed": True,
        "safety_passed": True,
        "holdout_passed": "false",
    }
    result = evaluate_learning_completion(base)
    assert result["accepted"] is False
    assert result["promote"] is False
    assert result["invalid_fields"] == ["holdout_passed"]
