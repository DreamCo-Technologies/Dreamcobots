from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, Iterable, List, Sequence
import math

DIVISIONS = [
    'finance', 'health', 'education', 'retail', 'logistics', 'security', 'energy', 'media',
    'government', 'agriculture', 'travel', 'real_estate', 'legal', 'customer_success', 'sales',
    'marketing', 'hr', 'analytics', 'robotics', 'iot', 'cloud', 'mobile', 'gaming', 'payments',
    'insurance', 'telecom', 'manufacturing', 'biotech', 'climate', 'space', 'defense', 'fashion',
    'food', 'automotive', 'semiconductor', 'quantum', 'cyber_ai', 'compliance', 'support',
    'operations', 'research', 'venture', 'platform', 'ecosystem'
]

BOT_RESPONSES = {
    'finance': ['treasury-bot', 'forecast-bot'],
    'security': ['sentinel-bot', 'incident-bot'],
    'media': ['publisher-bot', 'viral-bot'],
    'operations': ['ops-bot', 'supply-bot'],
    'research': ['analyst-bot', 'briefing-bot'],
    'platform': ['router-bot', 'devrel-bot'],
}

@dataclass
class NewsSignal:
    headline: str
    source: str
    sentiment: float
    relevance_to_divisions: Dict[str, float]
    publish_time: datetime
    impact_bots: List[str] = field(default_factory=list)

    @property
    def top_divisions(self) -> List[str]:
        ranked = sorted(self.relevance_to_divisions.items(), key=lambda item: item[1], reverse=True)
        return [name for name, score in ranked[:5] if score > 0]


class NewsIntelligence:
    """Deterministic news intelligence suitable for offline strategy simulations."""

    _source_map = {
        'ai': 'DreamCo Wire', 'market': 'Global Markets TV', 'regulation': 'Policy Ledger',
        'energy': 'GridWatch', 'security': 'Cyber Desk', 'supply': 'Port Intelligence'
    }
    _sentiment_words = {
        'surge': 0.7, 'record': 0.5, 'breakthrough': 0.8, 'partnership': 0.4,
        'risk': -0.5, 'breach': -0.9, 'slowdown': -0.6, 'probe': -0.4,
        'growth': 0.6, 'expansion': 0.5, 'warning': -0.6,
    }

    def fetch(self, topics: Sequence[str], lookback_hours: int = 24) -> List[NewsSignal]:
        now = datetime.utcnow()
        signals: List[NewsSignal] = []
        for idx, topic in enumerate(topics):
            headline = self._synthesize_headline(topic, idx)
            publish_time = now - timedelta(hours=min(lookback_hours, idx * 3))
            relevance = self._score_relevance(headline, topic)
            sentiment = self._score_sentiment(headline)
            impact_bots = self._assess_impact(relevance, sentiment)
            signals.append(NewsSignal(headline, self._pick_source(topic), sentiment, relevance, publish_time, impact_bots))
        return sorted(signals, key=lambda signal: (signal.publish_time, max(signal.relevance_to_divisions.values() or [0])), reverse=True)

    def _synthesize_headline(self, topic: str, seed: int) -> str:
        templates = [
            'Global {topic} markets show surge in enterprise demand',
            '{topic} regulation triggers new platform compliance race',
            'Breakthrough in {topic} infrastructure reshapes deployment economics',
            '{topic} leaders warn of supply slowdown amid rapid automation',
        ]
        return templates[seed % len(templates)].format(topic=topic.replace('_', ' '))

    def _pick_source(self, topic: str) -> str:
        for key, source in self._source_map.items():
            if key in topic.lower():
                return source
        return 'World Signal Network'

    def _score_sentiment(self, headline: str) -> float:
        total = 0.0
        for word, weight in self._sentiment_words.items():
            if word in headline.lower():
                total += weight
        return max(-1.0, min(1.0, total if total else 0.05))

    def _score_relevance(self, headline: str, topic: str) -> Dict[str, float]:
        tokens = set((headline + ' ' + topic).lower().replace('-', ' ').split())
        scores: Dict[str, float] = {}
        for division in DIVISIONS:
            keywords = set(division.replace('_', ' ').split())
            overlap = len(tokens & keywords)
            semantic_bonus = 0.2 if any(part in topic.lower() for part in keywords) else 0.0
            magnitude = math.tanh((overlap * 0.7) + semantic_bonus)
            if division in {'platform', 'operations', 'research'}:
                magnitude += 0.15
            scores[division] = round(min(1.0, magnitude), 3)
        return scores

    def _assess_impact(self, relevance: Dict[str, float], sentiment: float) -> List[str]:
        bots: List[str] = []
        for division, score in relevance.items():
            if score < 0.35:
                continue
            bots.extend(BOT_RESPONSES.get(division, [f'{division}-watcher']))
        if sentiment < -0.4:
            bots.append('executive-escalation-bot')
        return sorted(set(bots))
