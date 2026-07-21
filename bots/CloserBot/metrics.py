"""CloserBot metrics — tracks closing activity."""
# Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.

from __future__ import annotations


def track(deals_closed: int = 0, nurtured: int = 0) -> dict:
    """Return a metrics snapshot for this bot run."""
    return {
        "bot": "CloserBot",
        "deals_closed": deals_closed,
        "nurtured": nurtured,
    }
