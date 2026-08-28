import pytest

from buddy_os.intelligence.reasoning_evaluation import ReasoningEvaluationLab, ReasoningTrial


def test_reasoning_lab_scores_accuracy_and_brier():
    lab = ReasoningEvaluationLab()
    lab.record(ReasoningTrial("1", "causal", 0.9, True, cost=2))
    lab.record(ReasoningTrial("2", "causal", 0.8, False, cost=4, failure_mode="false_cause"))
    score = lab.score("causal")
    assert score.observed_trials == 2
    assert score.resolved_trials == 2
    assert score.accuracy == 0.5
    assert score.brier_score == pytest.approx((0.1**2 + 0.8**2) / 2)
    assert score.failures == ("false_cause",)


def test_unresolved_trials_are_preserved():
    lab = ReasoningEvaluationLab()
    trial = ReasoningTrial("3", "spatial", 0.6, None)
    lab.record(trial)
    assert lab.unresolved() == [trial]
