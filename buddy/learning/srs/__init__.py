"""Shared spaced-repetition schedulers for Buddy.

SM-2 and Leitner are available. FSRS integration is tracked in the design
contract and must pass its acceptance gate before becoming the default.
"""
from .leitner import DEFAULT_INTERVALS, LeitnerCard, due_leitner_cards, review_leitner
from .sm2 import Card, ReviewLog, review, due_cards, catalog_spaced_repetition_check

__all__ = [
    "Card", "ReviewLog", "review", "due_cards", "catalog_spaced_repetition_check",
    "DEFAULT_INTERVALS", "LeitnerCard", "review_leitner", "due_leitner_cards",
]
