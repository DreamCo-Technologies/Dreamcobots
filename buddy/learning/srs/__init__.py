"""Shared, division-independent spaced-repetition engine for Buddy.

FSRS is the default adaptive scheduler. Leitner supports beginner/classroom
mode, SM-2 remains available for legacy decks, and Anki Classic-style scheduling
is exposed as an explicitly versioned compatibility profile.
"""
from __future__ import annotations

DEFAULT_ADAPTIVE_SCHEDULER = "fsrs"

from .anki_classic import AnkiClassicCard, AnkiClassicConfig, AnkiClassicScheduler
from .leitner import DEFAULT_INTERVALS, LeitnerCard, due_leitner_cards, review_leitner
from .sm2 import Card, ReviewLog, review, due_cards, catalog_spaced_repetition_check
from .store import IdempotencyConflictError, RecordReviewResult, SRSStore

_FSRS_EXPORTS = {"FSRSAdapter", "FSRSConfig", "FSRSReviewResult", "FSRS_SCHEDULER_VERSION", "BuddySRSService"}


def __getattr__(name: str):
    if name in _FSRS_EXPORTS:
        if name == "BuddySRSService":
            from .service import BuddySRSService
            return BuddySRSService
        from importlib import import_module
        fsrs_module = import_module(f"{__name__}.fsrs")
        return getattr(fsrs_module, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = [
    "DEFAULT_ADAPTIVE_SCHEDULER",
    "FSRSAdapter", "FSRSConfig", "FSRSReviewResult", "FSRS_SCHEDULER_VERSION", "BuddySRSService",
    "AnkiClassicCard", "AnkiClassicConfig", "AnkiClassicScheduler",
    "Card", "ReviewLog", "review", "due_cards", "catalog_spaced_repetition_check",
    "DEFAULT_INTERVALS", "LeitnerCard", "review_leitner", "due_leitner_cards",
    "SRSStore", "RecordReviewResult", "IdempotencyConflictError",
]
