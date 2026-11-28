"""Regression tests for governed learning-job routing."""
from buddy.frontier.learning_orchestrator import (
    EvaluationFailure,
    LearningAction,
    propose_learning_jobs,
)


def test_code_provenance_failure_routes_to_reviewable_reverse_engineering():
    failure = EvaluationFailure(
        evaluation_id="eval-code-1",
        capability="repository navigation",
        failure_mode="missing_evidence_trace",
        baseline_score=0.9,
        current_score=0.5,
        system_area="provenance",
        evidence_refs=("sha256:fixture",),
    )
    jobs = propose_learning_jobs([failure])
    assert len(jobs) == 1
    assert jobs[0].action is LearningAction.REVERSE_ENGINEER
    assert jobs[0].source_failures == ["eval-code-1"]
    assert jobs[0].regression_tests == ["sha256:fixture"]
    assert jobs[0].execution_started is False
    assert jobs[0].source_code_copied is False
    assert jobs[0].model_weights_changed is False
    assert jobs[0].proposed_steps


def test_training_failure_routes_to_distillation_without_starting_training():
    failure = EvaluationFailure(
        evaluation_id="eval-training-1",
        capability="model quality",
        failure_mode="underfit_training_loss",
        baseline_score=0.8,
        current_score=0.4,
        system_area="training",
    )
    jobs = propose_learning_jobs([failure])
    assert len(jobs) == 1
    assert jobs[0].action is LearningAction.DISTILL
    assert jobs[0].execution_started is False
    assert jobs[0].model_weights_changed is False
    assert any("approval" in step.lower() for step in jobs[0].proposed_steps)
