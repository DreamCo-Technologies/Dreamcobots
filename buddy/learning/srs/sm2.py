"""SM-2 scheduling (SuperMemo 2, Wozniak 1990) with a review log.

quality: 0-5. quality < 3 is a lapse (repetition resets, interval 1 day).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, timedelta

MIN_EASE = 1.3


@dataclass
class ReviewLog:
    reviewed_on: date
    quality: int
    interval_before: int
    interval_after: int
    ease_after: float


@dataclass
class Card:
    card_id: str
    front: str
    back: str
    ease: float = 2.5
    interval: int = 0
    repetitions: int = 0
    due: date = field(default_factory=date.today)
    lapses: int = 0
    history: list[ReviewLog] = field(default_factory=list)

    @property
    def retained(self) -> bool:
        """Catalog rule: retained once passed (quality >= 3) at least twice."""
        return sum(1 for h in self.history if h.quality >= 3) >= 2


def review(card: Card, quality: int, on: date | None = None) -> Card:
    if not 0 <= quality <= 5:
        raise ValueError("quality must be 0..5")
    on = on or date.today()
    before = card.interval
    if quality < 3:
        card.repetitions = 0
        card.interval = 1
        card.lapses += 1
    else:
        if card.repetitions == 0:
            card.interval = 1
        elif card.repetitions == 1:
            card.interval = 6
        else:
            card.interval = round(card.interval * card.ease)
        card.repetitions += 1
    card.ease = max(MIN_EASE, card.ease + 0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
    card.due = on + timedelta(days=card.interval)
    card.history.append(ReviewLog(on, quality, before, card.interval, round(card.ease, 4)))
    return card


def due_cards(cards: list[Card], on: date | None = None) -> list[Card]:
    on = on or date.today()
    return sorted((c for c in cards if c.due <= on), key=lambda c: (c.due, c.ease))


def catalog_spaced_repetition_check(passes: list[bool], start: date | None = None) -> dict:
    """Mirror the catalog test in buddy/learning/learning_strategies_catalog.json:
    review at day 1, 3, 7; retained if passed twice."""
    start = start or date.today()
    days = [1, 3, 7]
    schedule = [start + timedelta(days=d) for d in days[: len(passes)]]
    return {
        "schedule_days": days,
        "review_dates": [d.isoformat() for d in schedule],
        "retained": passes.count(True) >= 2,
        "weights_trained": False,
    }
