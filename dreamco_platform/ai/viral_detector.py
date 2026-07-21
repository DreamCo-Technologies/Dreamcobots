from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Mapping
import math

@dataclass
class ViralSignal:
    content_id: str
    early_engagement_velocity: float
    predicted_reach: int
    topic: str

@dataclass
class ViralScore:
    signal: ViralSignal
    score: float
    channels: List[str]
    explanation: str


class ViralDetector:
    """Scores content for virality using first-30-minute engagement indicators."""

    CHANNEL_RULES = {
        'developer': ['x', 'linkedin', 'email'],
        'consumer': ['tiktok', 'instagram', 'youtube_shorts'],
        'enterprise': ['linkedin', 'newsletter', 'webinar'],
    }

    def score(self, content_metrics: Mapping[str, float]) -> ViralScore:
        impressions = float(content_metrics.get('impressions_30m', 1))
        engagements = float(content_metrics.get('engagements_30m', 0))
        shares = float(content_metrics.get('shares_30m', 0))
        comments = float(content_metrics.get('comments_30m', 0))
        velocity = (engagements + shares * 2 + comments * 1.5) / max(impressions, 1.0)
        score = self._sigmoid((velocity * 18) + (shares / max(engagements, 1.0) * 4) - 2)
        predicted_reach = int(impressions * (2 + score * 18))
        topic = str(content_metrics.get('topic', 'general'))
        audience = str(content_metrics.get('audience', 'consumer'))
        signal = ViralSignal(str(content_metrics.get('content_id', 'unknown')), round(velocity, 4), predicted_reach, topic)
        channels = self._recommend_channels(audience, score, topic)
        explanation = f'Predicted viral score {score:.2f} from velocity={velocity:.3f} and share ratio {shares/max(engagements,1.0):.2f}.'
        return ViralScore(signal=signal, score=round(score, 3), channels=channels, explanation=explanation)

    def _recommend_channels(self, audience: str, score: float, topic: str) -> List[str]:
        base = list(self.CHANNEL_RULES.get(audience, ['x', 'blog']))
        if score > 0.75:
            base.append('paid_boost')
        if 'ai' in topic.lower() or 'tech' in topic.lower():
            base.append('hacker_news')
        return sorted(set(base))

    @staticmethod
    def _sigmoid(value: float) -> float:
        return 1 / (1 + math.exp(-value))



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
