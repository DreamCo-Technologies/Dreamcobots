from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

@dataclass
class CognitiveDimension:
    reasoning: float
    memory: float
    planning: float
    learning: float
    communication: float

@dataclass
class CognitiveProfile:
    bot_id: str
    dimensions: CognitiveDimension
    gaps: Dict[str, float]
    recommendations: Dict[str, str]


class CognitiveMaps:
    BASELINES = {
        'support': CognitiveDimension(0.72, 0.68, 0.64, 0.6, 0.86),
        'sales': CognitiveDimension(0.74, 0.66, 0.78, 0.58, 0.82),
        'research': CognitiveDimension(0.88, 0.8, 0.84, 0.79, 0.75),
    }

    def profile(self, bot_id: str) -> CognitiveProfile:
        bot_type = next((kind for kind in self.BASELINES if kind in bot_id.lower()), 'support')
        dimensions = self.BASELINES[bot_type]
        target = {'reasoning': 0.85, 'memory': 0.8, 'planning': 0.82, 'learning': 0.75, 'communication': 0.85}
        current = dimensions.__dict__
        gaps = {name: round(max(0.0, target[name] - value), 3) for name, value in current.items()}
        recommendations = {
            name: self._recommend(name, gap)
            for name, gap in gaps.items() if gap > 0
        }
        return CognitiveProfile(bot_id=bot_id, dimensions=dimensions, gaps=gaps, recommendations=recommendations)

    @staticmethod
    def _recommend(name: str, gap: float) -> str:
        if name == 'memory':
            return 'Add vector memory replay and summarization checkpoints.'
        if name == 'planning':
            return 'Introduce explicit task decomposition with milestone verification.'
        if name == 'learning':
            return 'Capture feedback loops from outcomes and user corrections.'
        if name == 'communication':
            return 'Improve response style transfer and structured explanations.'
        return 'Increase tool-use validation and chain-of-thought distillation.'



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
