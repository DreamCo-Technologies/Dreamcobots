"""
Sales Pipeline — connects bots to create a seamless lead-to-revenue pipeline.

Integrates lead generation, enrichment, outreach, nurturing, and deal closing.

Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.
See framework/global_ai_sources_flow.py for the full pipeline specification.
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from framework import GlobalAISourcesFlow  # noqa: F401  (GLOBAL AI SOURCES FLOW)

from bots.LeadGenBot.main import get_leads
from bots.EnrichmentBot.main import enrich
from bots.OutreachBot.main import outreach
from bots.FollowUpBot.main import follow_up
from bots.CloserBot.main import attempt_close


# ---------------------------------------------------------------------------
# Pipeline
# ---------------------------------------------------------------------------


def run_pipeline() -> dict:
    """
    Execute the end-to-end sales pipeline.

    Steps
    -----
    1. Generate leads.
    2. Enrich each lead with a score and context.
    3. Send an outreach message to each lead.
    4. Follow up with every lead.
    5. Attempt to close qualified leads.

    Returns
    -------
    dict
        Summary with keys ``leads_total``, ``closed``, and ``nurtured``.
    """
    leads = get_leads()

    closed = 0
    nurtured = 0

    for lead in leads:
        lead = enrich(lead)
        outreach(lead)
        follow_up(lead)

        if attempt_close(lead):
            print(f"✅ DEAL CLOSED: {lead['name']}")
            closed += 1
        else:
            nurtured += 1

    return {
        "leads_total": len(leads),
        "closed": closed,
        "nurtured": nurtured,
    }


if __name__ == "__main__":
    result = run_pipeline()
    print(
        f"Pipeline complete — {result['leads_total']} leads, "
        f"{result['closed']} closed, {result['nurtured']} nurtured."
    )
