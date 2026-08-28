import pytest

from buddy_os.intelligence.planner_arbitration import PlannerArbitrator, PlannerResult


def test_arbitrator_detects_disagreement_and_requests_verification():
    arbitrator = PlannerArbitrator()
    results = [
        PlannerResult("tree", "plan_a", .9, .8),
        PlannerResult("monte_carlo", "plan_b", .8, .9),
    ]
    decision = arbitrator.arbitrate(results)
    assert decision.winner is not None
    assert decision.winner.planner_id == "tree"
    assert decision.requires_verification is True
    assert set(decision.disagreement) == {"plan_a", "plan_b"}


def test_empty_arbitration_requires_verification():
    decision = PlannerArbitrator().arbitrate([])
    assert decision.winner is None
    assert decision.requires_verification is True


def test_confidence_is_bounded():
    with pytest.raises(ValueError):
        PlannerResult("x", "y", 1, 1.1)
