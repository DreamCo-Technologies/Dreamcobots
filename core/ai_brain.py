"""
AI Brain — analyzes markets and determines bot types aligned with opportunities.

Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.
See framework/global_ai_sources_flow.py for the full pipeline specification.
"""

from __future__ import annotations

import os
import random
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from framework import GlobalAISourcesFlow  # noqa: F401  (GLOBAL AI SOURCES FLOW)

# ---------------------------------------------------------------------------
# Market data
# ---------------------------------------------------------------------------

MARKETS = [
    "real estate",
    "auto repair",
    "restaurants",
    "insurance",
    "trucking",
    "landscaping",
    "dental offices",
    "HVAC",
    "plumbing",
    "retail",
]

BOT_TYPE_MAP: dict[str, str] = {
    "real estate": "LeadGenBot_RealEstate",
    "auto repair": "LeadGenBot_Auto",
    "restaurants": "LeadGenBot_Restaurants",
    "insurance": "LeadGenBot_Insurance",
    "trucking": "LeadGenBot_Trucking",
    "landscaping": "LeadGenBot_Landscaping",
    "dental offices": "LeadGenBot_Dental",
    "HVAC": "LeadGenBot_HVAC",
    "plumbing": "LeadGenBot_Plumbing",
    "retail": "LeadGenBot_Retail",
}


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def find_opportunity() -> str:
    """Return a randomly selected market opportunity."""
    return random.choice(MARKETS)


def decide_bot_type(market: str) -> str:
    """Return the appropriate bot type name for the given market."""
    return BOT_TYPE_MAP.get(market, f"LeadGenBot_{market.replace(' ', '_').title()}")


def analyze_market(market: str | None = None) -> dict:
    """
    Analyze a market and return opportunity metadata.

    Parameters
    ----------
    market : str, optional
        Market to analyze.  A random market is selected when omitted.

    Returns
    -------
    dict
        Keys: ``market``, ``bot_type``, ``score``, ``recommendation``.
    """
    if market is None:
        market = find_opportunity()

    bot_type = decide_bot_type(market)
    score = random.randint(60, 100)

    recommendation = "build" if score >= 70 else "monitor"

    return {
        "market": market,
        "bot_type": bot_type,
        "score": score,
        "recommendation": recommendation,
    }


if __name__ == "__main__":
    result = analyze_market()
    print(f"🧠 AI chose market: {result['market']} (score: {result['score']})")
    print(f"   Bot type:       {result['bot_type']}")
    print(f"   Recommendation: {result['recommendation']}")
