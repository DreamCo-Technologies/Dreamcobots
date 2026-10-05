"""Dependency-free spaced-repetition engine (SM-2) for the DreamCo study-skills OS.

Status: local prototype. Not wired to Buddy or Pages yet.
"""
from .sm2 import Card, ReviewLog, review, due_cards, catalog_spaced_repetition_check

__all__ = ["Card", "ReviewLog", "review", "due_cards", "catalog_spaced_repetition_check"]
