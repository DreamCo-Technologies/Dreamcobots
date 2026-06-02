from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List, Mapping

@dataclass
class ESGMetric:
    category: str
    indicator: str
    value: float
    target: float
    score: float

@dataclass
class ESGReport:
    metrics: List[ESGMetric]
    overall_score: float
    benchmark: float
    notes: List[str]


class ESGMonitor:
    INDUSTRY_BENCHMARK = 76.0

    def __init__(self, token_co2_grams: float = 0.0002) -> None:
        self.token_co2_grams = token_co2_grams

    def compute_score(self, telemetry: Mapping[str, float] | None = None) -> ESGReport:
        telemetry = dict(telemetry or {})
        carbon_tokens = telemetry.get('compute_tokens', 0.0)
        co2 = carbon_tokens * self.token_co2_grams
        bias_findings = telemetry.get('bias_incidents', 0.0)
        fair_pricing_gap = telemetry.get('fair_pricing_gap_pct', 0.0)
        governance_coverage = telemetry.get('policy_coverage_pct', 90.0)
        metrics = [
            self._metric('E', 'co2_grams', co2, 500, max(0.0, 100 - co2 / 5)),
            self._metric('S', 'bias_detection', bias_findings, 0, max(0.0, 100 - bias_findings * 20)),
            self._metric('S', 'fair_pricing_gap_pct', fair_pricing_gap, 3, max(0.0, 100 - fair_pricing_gap * 8)),
            self._metric('G', 'policy_coverage_pct', governance_coverage, 95, min(100.0, governance_coverage)),
        ]
        overall = round(sum(metric.score for metric in metrics) / len(metrics), 2)
        notes = [
            f'Estimated compute emissions: {co2:.3f}g CO2e.',
            'Bias detection covers output parity checks and fair pricing thresholds.',
        ]
        return ESGReport(metrics=metrics, overall_score=overall, benchmark=self.INDUSTRY_BENCHMARK, notes=notes)

    @staticmethod
    def _metric(category: str, indicator: str, value: float, target: float, score: float) -> ESGMetric:
        return ESGMetric(category=category, indicator=indicator, value=round(value, 3), target=target, score=round(score, 2))



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
