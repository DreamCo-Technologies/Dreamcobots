"""Simple Leitner-box scheduler for beginner and classroom study modes.

Intervals are configurable and expressed in days. A successful review advances
one box; a failed review resets the card to box 1.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, timedelta

DEFAULT_INTERVALS = (1, 2, 4, 8, 14)


@dataclass
class LeitnerCard:
    card_id: str
    front: str
    back: str
    box: int = 1
    due: date = field(default_factory=date.today)
    reviews: int = 0
    lapses: int = 0


def review_leitner(
    card: LeitnerCard,
    correct: bool,
    on: date | None = None,
    intervals: tuple[int, ...] = DEFAULT_INTERVALS,
) -> LeitnerCard:
    """Record one answer and calculate the next due date.

    Boxes are one-indexed. The final box is a capped mastery interval.
    """
    if not intervals or any(not isinstance(day, int) or day < 1 for day in intervals):
        raise ValueError("intervals must contain positive whole days")
    if any(left >= right for left, right in zip(intervals, intervals[1:])):
        raise ValueError("intervals must be strictly increasing")
    if not 1 <= card.box <= len(intervals):
        raise ValueError("card.box must be within the configured box range")
    reviewed_on = on or date.today()
    card.reviews += 1
    if correct:
        card.box = min(card.box + 1, len(intervals))
    else:
        card.box = 1
        card.lapses += 1
    card.due = reviewed_on + timedelta(days=intervals[card.box - 1])
    return card


def due_leitner_cards(
    cards: list[LeitnerCard], on: date | None = None
) -> list[LeitnerCard]:
    """Return due cards ordered by due date, then lower box first."""
    today = on or date.today()
    return sorted(
        (card for card in cards if card.due <= today),
        key=lambda card: (card.due, card.box, card.card_id),
    )
