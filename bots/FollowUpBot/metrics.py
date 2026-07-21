"""FollowUpBot metrics — tracks follow-up activity."""
# Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.

from __future__ import annotations


def track(follow_ups_sent: int = 0) -> dict:
    """Return a metrics snapshot for this bot run."""
    return {
        "bot": "FollowUpBot",
        "follow_ups_sent": follow_ups_sent,
    }
