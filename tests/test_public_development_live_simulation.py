from decimal import Decimal

from dreamco_platform.public_development.live_simulation import ScenarioInputs, compare_scenarios, simulate_development


def test_simulation_is_deterministic_and_labeled_estimated():
    inputs = ScenarioInputs(
        population=65000,
        jobs=30000,
        median_household_income=Decimal("60000"),
        residential_vacancy_rate=Decimal("7.5"),
        commercial_vacancy_rate=Decimal("14"),
        annual_visitors=50000,
        new_housing_units=300,
        new_jobs=1200,
        new_businesses=25,
        infrastructure_investment=Decimal("10000000"),
        tourism_investment=Decimal("1000000"),
        housing_investment=Decimal("5000000"),
    )
    first = simulate_development(inputs)
    second = simulate_development(inputs)
    assert first == second
    assert first.evidence_label == "ESTIMATED"
    assert first.projected_jobs > inputs.jobs
    assert 0 <= first.opportunity_score <= 100


def test_compare_scenarios_returns_highest_score_first():
    base = ScenarioInputs(10000, 4000, Decimal("50000"), Decimal("8"), Decimal("15"))
    investment = ScenarioInputs(
        10000, 4000, Decimal("50000"), Decimal("8"), Decimal("15"),
        new_jobs=500, new_businesses=20, infrastructure_investment=Decimal("5000000")
    )
    results = compare_scenarios([base, investment])
    assert results[0].opportunity_score >= results[1].opportunity_score
