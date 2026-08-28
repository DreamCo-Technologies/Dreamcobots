from buddy_os.intelligence.reasoning_evaluation import ReasoningEvaluationLab, ReasoningTrial
from buddy_os.intelligence.reasoning_router_feedback import ReasoningRouterFeedback


def test_feedback_requires_minimum_evidence_before_preference():
    lab = ReasoningEvaluationLab()
    for i in range(5):
        lab.record(ReasoningTrial(str(i), "causal", 0.9, True, cost=1))
    feedback = ReasoningRouterFeedback(lab, min_observations=5)
    assert feedback.preferred_method(["causal"]) == "causal"


def test_feedback_does_not_overfit_single_observation():
    lab = ReasoningEvaluationLab()
    lab.record(ReasoningTrial("1", "causal", 1.0, True))
    assert ReasoningRouterFeedback(lab, min_observations=5).preferred_method(["causal"]) is None
