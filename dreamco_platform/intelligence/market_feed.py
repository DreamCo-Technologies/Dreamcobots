from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Iterable, List


@dataclass
class MarketSignal:
    source: str
    content: str
    sentiment: float
    relevance_score: float
    timestamp: datetime


class SignalFilter:
    def __init__(self, division: str | None = None, keyword: str | None = None, sentiment_threshold: float = -1.0) -> None:
        self.division = division
        self.keyword = keyword.lower() if keyword else None
        self.sentiment_threshold = sentiment_threshold

    def apply(self, signals: Iterable[MarketSignal]) -> List[MarketSignal]:
        selected = []
        for signal in signals:
            if self.keyword and self.keyword not in signal.content.lower():
                continue
            if signal.sentiment < self.sentiment_threshold:
                continue
            if self.division and self.division.lower() not in signal.content.lower():
                continue
            selected.append(signal)
        return selected


class Dispatcher:
    def __init__(self) -> None:
        self.command_queues: dict[str, list[MarketSignal]] = {}

    def push(self, queue_name: str, signals: Iterable[MarketSignal]) -> None:
        self.command_queues.setdefault(queue_name, []).extend(signals)


class MarketFeedAggregator:
    POSITIVE = {'growth', 'surge', 'win', 'partnership', 'expansion'}
    NEGATIVE = {'drop', 'lawsuit', 'outage', 'loss', 'layoff'}

    def __init__(self, dispatcher: Dispatcher | None = None) -> None:
        self.dispatcher = dispatcher or Dispatcher()

    def ingest(self, source: str, entries: Iterable[str]) -> List[MarketSignal]:
        signals = []
        for entry in entries:
            sentiment = self._sentiment(entry)
            relevance = min(1.0, len(entry.split()) / 20 + abs(sentiment) * 0.4)
            signals.append(MarketSignal(source, entry, sentiment, round(relevance, 3), datetime.utcnow()))
        return signals

    def dispatch_high_relevance(self, queue_name: str, signals: Iterable[MarketSignal], threshold: float = 0.6) -> List[MarketSignal]:
        selected = [signal for signal in signals if signal.relevance_score >= threshold]
        self.dispatcher.push(queue_name, selected)
        return selected

    def _sentiment(self, text: str) -> float:
        tokens = {token.strip('.,!?').lower() for token in text.split()}
        score = sum(1 for token in tokens if token in self.POSITIVE) - sum(1 for token in tokens if token in self.NEGATIVE)
        return max(-1.0, min(1.0, score / 3))
