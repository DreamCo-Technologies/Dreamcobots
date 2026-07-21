"""
LeadGenBot — identifies and returns qualified prospects.

Replace the mock data with real API integrations (Google Maps, LinkedIn,
Apollo, etc.) for production use.

Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.
See framework/global_ai_sources_flow.py for the full pipeline specification.
"""

from __future__ import annotations

import os
import sys
from typing import List, Dict

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from framework import GlobalAISourcesFlow  # noqa: F401  (GLOBAL AI SOURCES FLOW)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def get_leads() -> List[Dict]:
    """
    Return a list of prospect leads.

    Each lead is a dict with at minimum the keys:
      - ``name``     : str  — business or contact name
      - ``email``    : str  — contact e-mail address
      - ``business`` : str  — business type / industry

    Replace the mock data below with real API integrations for production.
    Upgrade path: Google Maps scraping, LinkedIn, Craigslist, Apollo.
    """
    leads = [
        {"name": "John Doe", "email": "john@example.com", "business": "Auto Shop"},
        {"name": "Sarah Lee", "email": "sarah@example.com", "business": "Real Estate"},
        {"name": "Mike Chen", "email": "mike@example.com", "business": "Restaurant"},
        {"name": "Dana Park", "email": "dana@example.com", "business": "HVAC"},
    ]
    return leads


if __name__ == "__main__":
    leads = get_leads()
    print(f"✅ Generated {len(leads)} leads")
    for lead in leads:
        print(f"  • {lead['name']} <{lead['email']}> — {lead['business']}")
