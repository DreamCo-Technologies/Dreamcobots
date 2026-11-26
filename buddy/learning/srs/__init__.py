"""Shared, division-independent spaced-repetition engine for Buddy.

FSRS is the default adaptive scheduler. Leitner supports beginner/classroom
mode, SM-2 remains available for legacy decks, and Anki Classic-style scheduling
is exposed as an explicitly versioned compatibility profile.
"""
DEFAULT_ADAPTIVE_SCHEDULER = "fsrs"

from .anki_classic import AnkiClassicCard, AnkiClassicConfig, AnkiClassicScheduler
from .fsrs import FSRSAdapter, FSRSConfig, FSRSReviewResult, FSRS_SCHEDULER_VERSION
from .leitner import DEFAULT_INTERVALS, LeitnerCard, due_leitner_cards, review_leitner
from .sm2 import Card, ReviewLog, review, due_cards, catalog_spaced_repetition_check
from .store import IdempotencyConflictError, RecordReviewResult, SRSStore

__all__ = [
    "DEFAULT_ADAPTIVE_SCHEDULER",
    "FSRSAdapter", "FSRSConfig", "FSRSReviewResult", "FSRS_SCHEDULER_VERSION",
    "AnkiClassicCard", "AnkiClassicConfig", "AnkiClassicScheduler",
    "Card", "ReviewLog", "review", "due_cards", "catalog_spaced_repetition_check",
    "DEFAULT_INTERVALS", "LeitnerCard", "review_leitner", "due_leitner_cards",
    "SRSStore", "RecordReviewResult", "IdempotencyConflictError",
]
