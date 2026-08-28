import pytest

from buddy_os.intelligence.monte_carlo_planner import MonteCarloPlanner, Simulation


def test_monte_carlo_planner_is_reproducible_with_seed():
    planner = MonteCarloPlanner(simulations=10, seed=42)
    def sampler(rng, state):
        return Simulation(state, 1.0 if rng.random() >= .5 else 0.0)
    assert planner.evaluate((), sampler) == planner.evaluate((), sampler)


def test_planner_rejects_empty_budget_and_bad_probability():
    with pytest.raises(ValueError):
        MonteCarloPlanner(simulations=0)
    with pytest.raises(ValueError):
        Simulation((), 1, 1.1)
