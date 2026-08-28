import pytest

from buddy_os.intelligence.causal_counterfactual import CounterfactualLedger, CounterfactualScenario


def test_counterfactual_ledger_keeps_scenarios_explicit():
    ledger = CounterfactualLedger()
    scenario = CounterfactualScenario(
        "cf1", (("temperature", "high"),), ("coolant", "on"), "temperature decreases", 0.7,
        ("causal edge is valid",),
    )
    ledger.record(scenario)
    assert ledger.get("cf1") == scenario
    assert ledger.scenarios_for_variable("coolant") == (scenario,)


def test_counterfactual_validation():
    with pytest.raises(ValueError):
        CounterfactualScenario("bad", (), ("x", "y"), "outcome", 1.1)
