"""
Outreach Bot — Conducts email outreach with placeholders for SMTP configuration.

Requires GitHub Secrets: EMAIL_USER, EMAIL_PASS

Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.
See framework/global_ai_sources_flow.py for the full pipeline specification.
"""

from __future__ import annotations

import os
import smtplib
import sys
from email.mime.text import MIMEText

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from framework import GlobalAISourcesFlow  # noqa: F401  (GLOBAL AI SOURCES FLOW)


def send_message(lead: dict) -> bool:
    """Send an outreach message to a lead.

    Uses SMTP if EMAIL_USER and EMAIL_PASS environment variables are set
    (populated from GitHub Secrets in CI). Falls back to a console print
    when the secrets are not configured.

    Parameters
    ----------
    lead : dict
        Lead record with at least 'name' and 'email' keys.

    Returns
    -------
    bool
        True on success, False on failure.
    """
    sender = os.getenv("EMAIL_USER")
    password = os.getenv("EMAIL_PASS")

    body = f"""
Hey {lead['name']},

We help businesses increase revenue using AI automation.

Want more customers without more work?
"""

    if sender and password:
        try:
            msg = MIMEText(body)
            msg["Subject"] = "Quick question"
            msg["From"] = sender
            msg["To"] = lead["email"]

            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                server.login(sender, password)
                server.send_message(msg)
        except Exception as exc:
            print(f"Failed to send email to {lead['email']}: {exc}")
            return False

    print(f"Sending to {lead['email']}")
    return True


def run() -> dict:
    """GLOBAL AI SOURCES FLOW framework entry point."""
    return {
        "status": "success",
        "leads": 0,
        "leads_generated": 0,
        "revenue": 0,
    }
