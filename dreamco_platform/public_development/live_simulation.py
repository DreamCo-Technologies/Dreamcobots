from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from typing import Iterable


@dataclass(frozen=True)
class ScenarioInputs:
    population: int
    jobs: int
    median_household_income: Decimal
    residential_vacancy_rate: Decimal
    commercial_vacancy_rate: Decimal
    annual_visitors: int = 0
    new_housing_units: int = 0
    new_jobs: int = 0
    new_businesses: int = 0
    infrastructure_investment: Decimal = Decimal("0")
    tourism_investment: Decimal = Decimal("0")
    housing_investment: Decimal = Decimal("0")


@dataclass(frozen=True)
class ScenarioResult:
    projected_jobs: int
    projected_population_pressure: int
    projected_residential_vacancy_rate: Decimal
    projected_commercial_vacancy_rate: Decimal
    projected_annual_visitors: int
    opportunity_score: Decimal
    actions: tuple[str, ...] = field(default_factory=tuple)
    evidence_label: str = "ESTIMATED"


def _clamp_rate(value: Decimal) -> Decimal:
    return max(Decimal("0"), min(Decimal("100"), value))


def simulate_development(inputs: ScenarioInputs) -> ScenarioResult:
    """Transparent planning simulation, not a forecast or guarantee.

    The model is deliberately simple and deterministic so users can see how
    assumptions change the output. Production simulations should replace these
    heuristic coefficients with jurisdiction-specific calibrated models.
    """
    job_effect = inputs.new_jobs + int(inputs.new_businesses * 6)
    housing_absorption = Decimal(inputs.new_jobs) / Decimal("1500")
    business_absorption = Decimal(inputs.new_businesses) / Decimal("120")
    housing_supply_effect = Decimal(inputs.new_housing_units) / Decimal("1000")
    visitor_effect = int(inputs.tourism_investment / Decimal("250")) if inputs.tourism_investment > 0 else 0

    residential_vacancy = _clamp_rate(
        inputs.residential_vacancy_rate + housing_supply_effect - housing_absorption
    )
    commercial_vacancy = _clamp_rate(
        inputs.commercial_vacancy_rate - business_absorption
    )
    population_pressure = max(0, int(job_effect * 0.55) - inputs.new_housing_units)

    score = Decimal("50")
    score += min(Decimal("20"), Decimal(job_effect) / Decimal("500"))
    score += min(Decimal("10"), inputs.infrastructure_investment / Decimal("5000000"))
    score += min(Decimal("10"), inputs.housing_investment / Decimal("5000000"))
    score += min(Decimal("10"), inputs.tourism_investment / Decimal("2500000"))
    if residential_vacancy > Decimal("10"):
        score -= Decimal("8")
    if commercial_vacancy > Decimal("15"):
        score -= Decimal("8")
    score = max(Decimal("0"), min(Decimal("100"), score.quantize(Decimal("0.1"))))

    actions: list[str] = []
    if residential_vacancy > Decimal("8"):
        actions.append("prioritize housing absorption, rehabilitation, employer recruitment, and neighborhood demand")
    if commercial_vacancy > Decimal("12"):
        actions.append("target business attraction, adaptive reuse, pop-up activation, and corridor redevelopment")
    if population_pressure > 0:
        actions.append("increase housing pipeline and infrastructure capacity alongside job growth")
    if inputs.annual_visitors + visitor_effect < max(10000, inputs.population):
        actions.append("strengthen tourism, events, placemaking, regional marketing, and visitor infrastructure")
    if not actions:
        actions.append("continue balanced growth while monitoring affordability, vacancies, infrastructure, and fiscal capacity")

    return ScenarioResult(
        projected_jobs=inputs.jobs + job_effect,
        projected_population_pressure=population_pressure,
        projected_residential_vacancy_rate=residential_vacancy,
        projected_commercial_vacancy_rate=commercial_vacancy,
        projected_annual_visitors=inputs.annual_visitors + visitor_effect,
        opportunity_score=score,
        actions=tuple(actions),
    )


def compare_scenarios(scenarios: Iterable[ScenarioInputs]) -> list[ScenarioResult]:
    return sorted((simulate_development(s) for s in scenarios), key=lambda r: r.opportunity_score, reverse=True)
