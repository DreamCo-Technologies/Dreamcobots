"""
OutreachBot — contacts leads via email with an extendable SMTP-based module.

Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.
See framework/global_ai_sources_flow.py for the full pipeline specification.
"""

from __future__ import annotations

import os
import sys
from email.mime.text import MIMEText
from typing import Dict, List

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from framework import GlobalAISourcesFlow  # noqa: F401  (GLOBAL AI SOURCES FLOW)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _build_message(lead: Dict) -> str:
    """Return a personalized outreach e-mail body for *lead*."""
    name = lead.get("name", "Business Owner")
    business = lead.get("business", "your business")
    return (
        f"Hey {name},\n\n"
        f"I noticed your {business} could benefit from automation.\n"
        f"I help businesses increase revenue using AI systems.\n\n"
        f"Want me to show you how?\n\n"
        f"— DreamCo"
    )


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def outreach(lead: Dict) -> bool:
    """
    Contact a single lead via e-mail.

    In production, replace the print statement with a real SMTP / SendGrid
    / Mailgun call.  The MIMEText object is constructed here so that the
    SMTP integration is a one-line swap.

    Parameters
    ----------
    lead : dict
        Lead record with at minimum ``name``, ``email``, and ``business``.

    Returns
    -------
    bool
        ``True`` when the message was sent (or queued) successfully.
    """
    to_email = lead.get("email", "")
    name = lead.get("name", "Business Owner")
    business = lead.get("business", "your business")

    subject = f"{name}, quick idea for your {business}"
    body = _build_message(lead)

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = "outreach@dreamco.ai"
    msg["To"] = to_email

    # Replace with real SMTP credentials for production:
    # with smtplib.SMTP("smtp.gmail.com", 587) as server:
    #     server.starttls()
    #     server.login(EMAIL_USER, EMAIL_PASS)
    #     server.send_message(msg)

    print(f"📨 Sent to {to_email}")
    return True


def run(leads: List[Dict]) -> int:
    """Send outreach messages to every lead in *leads*. Returns sent count."""
    sent = 0
    for lead in leads:
        if outreach(lead):
            sent += 1
    return sent


if __name__ == "__main__":
    from bots.LeadGenBot.main import get_leads

    run(get_leads())
