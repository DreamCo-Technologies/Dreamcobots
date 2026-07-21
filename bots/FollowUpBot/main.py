"""
FollowUpBot — conducts follow-ups to nurture leads.

Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.
See framework/global_ai_sources_flow.py for the full pipeline specification.
"""

from __future__ import annotations

import os
import sys
import time
from typing import Dict

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from framework import GlobalAISourcesFlow  # noqa: F401  (GLOBAL AI SOURCES FLOW)

# Follow-up message sequence (replace with dynamic AI-generated copy later)
_MESSAGES = [
    "Just circling back — this could increase your revenue fast.",
    "Quick reminder — I can show you real results.",
    "Last message — worth a quick look?",
]


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def follow_up(lead: Dict, delay: float = 0) -> list:
    """
    Send the follow-up sequence to *lead*.

    Parameters
    ----------
    lead : dict
        Lead record with at minimum ``email``.
    delay : float
        Seconds to sleep between messages (default 0 for tests/CI).

    Returns
    -------
    list
        The follow-up messages that were sent.
    """
    sent = []
    for msg in _MESSAGES:
        print(f"🔁 Follow-up to {lead.get('email', 'unknown')}: {msg}")
        if delay:
            time.sleep(delay)
        sent.append(msg)
    return sent


if __name__ == "__main__":
    from bots.LeadGenBot.main import get_leads

    for lead in get_leads():
        follow_up(lead)
