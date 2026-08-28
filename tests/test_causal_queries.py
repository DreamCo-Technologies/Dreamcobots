import pytest

from buddy_os.intelligence.causal_queries import CausalQuery, CausalQueryPlanner


def test_query_planner_keeps_causal_question_types_explicit():
    planner = CausalQueryPlanner()
    observe = CausalQuery("q1", "observe", "temperature")
    intervene = CausalQuery("q2", "intervene", "coolant", "on")
    counterfactual = CausalQuery("q3", "counterfactual", "coolant", target="temperature")
    assert [planner.classify(q) for q in (observe, intervene, counterfactual)] == ["observe", "intervene", "counterfactual"]
    assert all(planner.requires_external_evidence(q) for q in (observe, intervene, counterfactual))


def test_query_validation():
    with pytest.raises(ValueError):
        CausalQuery("q", "intervene", "x")
    with pytest.raises(ValueError):
        CausalQuery("q", "counterfactual", "x")
    with pytest.raises(ValueError):
        CausalQuery("q", "unknown", "x")
