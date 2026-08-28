import pytest

from buddy_os.intelligence.decision_planning import DecisionPlan, DecisionPlanner, PlanStep


def test_expected_utility_and_reversibility():
    planner = DecisionPlanner()
    plan = DecisionPlan("p1", (
        PlanStep("a", "try reversible test", probability=.9, utility=10, cost=1, reversible=True),
        PlanStep("b", "follow-up", probability=.5, utility=4, cost=1, reversible=False),
    ))
    assert planner.expected_utility(plan) == pytest.approx(7.5)
    assert planner.reversibility(plan) == pytest.approx(.5)


def test_plan_ranking_is_deterministic():
    planner = DecisionPlanner()
    a = DecisionPlan("a", (PlanStep("a1", "A", probability=1, utility=5),))
    b = DecisionPlan("b", (PlanStep("b1", "B", probability=1, utility=3),))
    assert planner.rank([b, a]) == (a, b)
