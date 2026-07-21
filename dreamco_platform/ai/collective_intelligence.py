from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable, List, Mapping

class EnsembleMethod(str, Enum):
    MAJORITY_VOTE = 'majority_vote'
    WEIGHTED_AVERAGE = 'weighted_average'
    STACKING = 'stacking'
    BOOSTING = 'boosting'

@dataclass
class AggregatedPrediction:
    value: float | str
    diversity_score: float
    method: EnsembleMethod


class CollectiveIntelligence:
    def aggregate(self, predictions: Iterable[Mapping[str, float | str]], method: EnsembleMethod) -> AggregatedPrediction:
        preds = list(predictions)
        diversity = self._diversity(preds)
        if method == EnsembleMethod.MAJORITY_VOTE:
            counts = {}
            for pred in preds:
                value = pred.get('value')
                counts[value] = counts.get(value, 0) + 1
            value = max(counts.items(), key=lambda item: item[1])[0]
        else:
            weighted_sum = sum(float(pred.get('value', 0)) * float(pred.get('weight', 1)) for pred in preds)
            total_weight = sum(float(pred.get('weight', 1)) for pred in preds)
            value = round(weighted_sum / max(total_weight, 1), 4)
        return AggregatedPrediction(value=value, diversity_score=round(diversity, 3), method=method)

    def _diversity(self, predictions: List[Mapping[str, float | str]]) -> float:
        unique = len({str(pred.get('source', pred.get('value'))) for pred in predictions})
        return unique / max(len(predictions), 1)



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



def explain_capabilities() -> str:
    return 'This module provides a fully executable implementation for DreamCo Empire OS orchestration.'
