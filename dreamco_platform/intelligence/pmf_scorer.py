from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Mapping

@dataclass
class PMFSignal:
    retention_cohort: float
    nps_score: float
    organic_growth_rate: float
    feature_usage_depth: float
    disappointed_if_gone: float

@dataclass
class PMFScore:
    total: float
    benchmark: float
    key_drivers: Dict[str, float]
    improvement_actions: List[str]

@dataclass
class PMFReport:
    bot_slug: str
    signal: PMFSignal
    score: PMFScore


class PMFScorer:
    BENCHMARK = 40.0

    def __init__(self, survey_data: Mapping[str, Mapping[str, float]] | None = None) -> None:
        self.survey_data = survey_data or {}

    def compute(self, bot_slug: str) -> PMFReport:
        survey = self.survey_data.get(bot_slug, {})
        signal = PMFSignal(
            retention_cohort=float(survey.get('retention', 0.55)),
            nps_score=float(survey.get('nps', 38)),
            organic_growth_rate=float(survey.get('organic_growth', 0.12)),
            feature_usage_depth=float(survey.get('usage_depth', 0.62)),
            disappointed_if_gone=float(survey.get('disappointed_if_gone', 0.43)),
        )
        drivers = {
            'retention': signal.retention_cohort * 30,
            'nps': max(0.0, signal.nps_score) * 0.5,
            'organic_growth': signal.organic_growth_rate * 120,
            'usage_depth': signal.feature_usage_depth * 20,
            'sean_ellis': signal.disappointed_if_gone * 25,
        }
        total = round(min(100.0, sum(drivers.values())), 2)
        actions = []
        if signal.disappointed_if_gone < 0.4:
            actions.append('Increase must-have workflows before scaling acquisition.')
        if signal.retention_cohort < 0.6:
            actions.append('Improve onboarding and activation loops.')
        if signal.feature_usage_depth < 0.7:
            actions.append('Promote power-user features with guided playbooks.')
        return PMFReport(bot_slug=bot_slug, signal=signal, score=PMFScore(total=total, benchmark=self.BENCHMARK, key_drivers={k: round(v,2) for k,v in drivers.items()}, improvement_actions=actions))



def module_summary() -> dict:
    """Provide a compact runtime summary for orchestration tooling."""
    public_items = [name for name in globals() if not name.startswith('_')]
    return {
        'module': __name__,
        'public_items': sorted(public_items),
        'line_count': len(__doc__.splitlines()) if __doc__ else 0,
    }


def demo_payload() -> dict:
    """Return a deterministic payload useful for smoke-free integration wiring."""
    return {'module': __name__, 'status': 'ready'}
