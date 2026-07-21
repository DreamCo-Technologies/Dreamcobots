"""
CloserBot — closes high-priority leads or flags them for further nurturing.

Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.
See framework/global_ai_sources_flow.py for the full pipeline specification.
"""

from __future__ import annotations

import os
import sys
from typing import Dict

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from framework import GlobalAISourcesFlow  # noqa: F401  (GLOBAL AI SOURCES FLOW)

# Minimum enrichment score required to attempt an immediate close
CLOSE_SCORE_THRESHOLD = 70


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def qualify_lead(lead: Dict) -> str:
    """
    Return a priority tier for *lead*.

    Parameters
    ----------
    lead : dict
        Lead record.  Uses ``score`` if present, otherwise heuristics on
        ``name`` / ``business``.

    Returns
    -------
    str
        ``"high"`` or ``"medium"``.
    """
    score = lead.get("score", 0)
    if score >= CLOSE_SCORE_THRESHOLD:
        return "high"
    # Heuristic fallback when no enrichment score is present
    name = lead.get("name", "") or ""
    business = lead.get("business", "") or ""
    if "Auto" in name or "Auto" in business:
        return "high"
    return "medium"


def attempt_close(lead: Dict) -> bool:
    """
    Attempt to close the deal for *lead*.

    High-priority leads are closed immediately; medium-priority leads are
    flagged for further nurturing.

    Parameters
    ----------
    lead : dict
        Enriched lead record.

    Returns
    -------
    bool
        ``True`` if the deal was closed, ``False`` if sent to nurture.
    """
    priority = qualify_lead(lead)

    if priority == "high":
        print(f"💰 Closing HIGH VALUE deal with {lead.get('name', 'unknown')}")
        return True

    print(f"📞 Nurturing {lead.get('name', 'unknown')}")
    return False


if __name__ == "__main__":
    from bots.LeadGenBot.main import get_leads

    for lead in get_leads():
        attempt_close(lead)
