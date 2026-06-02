from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List, Mapping

@dataclass
class FunnelStage:
    name: str
    entry_count: int
    exit_count: int
    conversion_rate: float
    avg_time: float

@dataclass
class OptimizationRecommendations:
    stages: List[FunnelStage]
    recommendations: List[str]
    revenue_impact_per_point: float
    ab_tests: Dict[str, List[str]]


class FunnelOptimizer:
    def analyze(self, funnel_data: Iterable[Mapping[str, float]]) -> OptimizationRecommendations:
        stages: List[FunnelStage] = []
        recommendations: List[str] = []
        ab_tests: Dict[str, List[str]] = {}
        revenue_base = 0.0
        for item in funnel_data:
            entry = int(item.get('entry_count', 0))
            exit_count = int(item.get('exit_count', 0))
            conversion = exit_count / entry if entry else 0.0
            stage = FunnelStage(str(item.get('name', 'unknown')), entry, exit_count, round(conversion, 4), float(item.get('avg_time', 0.0)))
            stages.append(stage)
            revenue_base += float(item.get('revenue_value', exit_count * 10))
            if conversion < 0.35:
                recommendations.append(f'Improve {stage.name} messaging and simplify CTA to recover drop-off.')
                ab_tests[stage.name] = ['message_variant', 'cta_placement', 'trust_badges']
            elif stage.avg_time > 120:
                recommendations.append(f'Reduce friction in {stage.name}; long dwell time indicates confusion.')
                ab_tests[stage.name] = ['shorter_form', 'guided_flow']
            else:
                ab_tests[stage.name] = ['headline_polish']
        revenue_impact = round(revenue_base * 0.01, 2)
        return OptimizationRecommendations(stages=stages, recommendations=recommendations, revenue_impact_per_point=revenue_impact, ab_tests=ab_tests)



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
