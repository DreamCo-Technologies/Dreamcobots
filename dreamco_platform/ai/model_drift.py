from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List, Mapping, Sequence
import math

@dataclass
class DriftMetric:
    feature: str
    baseline_distribution: List[float]
    current_distribution: List[float]
    psi_score: float

@dataclass
class DriftReport:
    metrics: List[DriftMetric]
    retraining_triggered: bool
    submitted_job: str | None


class ModelDrift:
    def detect(self, baseline_data: Mapping[str, Sequence[float]], current_data: Mapping[str, Sequence[float]]) -> DriftReport:
        metrics: List[DriftMetric] = []
        triggered = False
        for feature, baseline in baseline_data.items():
            current = current_data.get(feature, baseline)
            base_dist = self._normalize(baseline)
            curr_dist = self._normalize(current)
            psi = sum((c - b) * math.log((c + 1e-6) / (b + 1e-6)) for b, c in zip(base_dist, curr_dist))
            metrics.append(DriftMetric(feature, [round(x, 4) for x in base_dist], [round(x, 4) for x in curr_dist], round(psi, 4)))
            if psi > 0.25:
                triggered = True
        job = 'retrain-job-submitted' if triggered else None
        return DriftReport(metrics=metrics, retraining_triggered=triggered, submitted_job=job)

    def _normalize(self, values: Sequence[float], bins: int = 5) -> List[float]:
        if not values:
            return [1.0 / bins] * bins
        lo, hi = min(values), max(values)
        if lo == hi:
            return [1.0 / bins] * bins
        counts = [0] * bins
        for value in values:
            index = min(bins - 1, int((value - lo) / (hi - lo) * bins))
            counts[index] += 1
        total = sum(counts)
        return [count / total for count in counts]



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
