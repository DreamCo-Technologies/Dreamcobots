import pytest

from buddy_os.learning.mdp_engine import MarkovDecisionModel


def test_value_iteration_prefers_higher_expected_reward():
    model = MarkovDecisionModel(discount=0.9)
    model.add_transition("plan", "safe_route", "done", 1.0)
    model.add_transition("plan", "cheap_route", "done", 1.0)
    model.set_reward("plan", "safe_route", 10)
    model.set_reward("plan", "cheap_route", 3)
    model.transitions["done"] = {}
    decisions = model.recommend("plan")
    assert decisions[0].action == "safe_route"


def test_invalid_transition_distribution_is_rejected():
    model = MarkovDecisionModel()
    model.add_transition("a", "x", "b", 0.5)
    with pytest.raises(ValueError):
        model.validate()
