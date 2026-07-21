"""
Sales Bot — Outreach Email Bot

Reads leads from ``data/leads.txt`` (written by LeadScraperBot) and sends
personalised outreach emails via SMTP.

Credentials and SMTP settings are injected at construction time so the bot
can be used in tests without touching real mail infrastructure.

Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.
"""

from __future__ import annotations

import ast
import os
import smtplib
import sys
from email.mime.text import MIMEText

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from framework import GlobalAISourcesFlow  # noqa: F401  # GLOBAL AI SOURCES FLOW


# ---------------------------------------------------------------------------
# Errors
# ---------------------------------------------------------------------------

class OutreachBotError(Exception):
    """Raised when a non-recoverable outreach error occurs."""


# ---------------------------------------------------------------------------
# Bot
# ---------------------------------------------------------------------------

class OutreachBot:
    """Outreach Sales Bot — sends personalised emails to scraped leads.

    Parameters
    ----------
    sender_email:
        Sending address.  Defaults to ``"youremail@example.com"``.
    password:
        SMTP password.  Defaults to ``"yourpassword"``.
    smtp_host:
        SMTP server hostname.  Defaults to ``"smtp.example.com"``.
    smtp_port:
        SMTP server port.  Defaults to ``587``.
    data_dir:
        Directory containing ``leads.txt``.  Defaults to ``"data"``.
    """

    def __init__(
        self,
        sender_email: str = "youremail@example.com",
        password: str = "yourpassword",
        smtp_host: str = "smtp.example.com",
        smtp_port: int = 587,
        data_dir: str = "data",
    ) -> None:
        self.name = "Outreach Sales Bot"
        self.sender_email = sender_email
        self.password = password
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.data_dir = data_dir
        self._flow = GlobalAISourcesFlow(bot_name="OutreachBot")

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def run(self) -> str:
        """Read leads file, send outreach emails, return a status string."""
        leads_path = os.path.join(self.data_dir, "leads.txt")

        try:
            with open(leads_path, "r", encoding="utf-8") as fh:
                lines = [line.strip() for line in fh if line.strip()]

            leads = [ast.literal_eval(line) for line in lines]

            if not leads:
                return "❌ No leads to send outreach emails."

            for lead in leads:
                self.send_email(lead)

            return f"📬 Outreach emails sent to {len(leads)} leads."

        except FileNotFoundError:
            return "❌ No leads to send outreach emails."
        except Exception as exc:  # noqa: BLE001
            return f"❌ Sales bot failed: {exc}"

    def send_email(self, lead: dict) -> None:
        """Send a single outreach email to *lead*.

        Parameters
        ----------
        lead:
            A dict with at least a ``name`` key.  The recipient address is
            taken from the ``email`` key when present; otherwise the ``phone``
            key is used as a fallback (the problem-statement scraper stores
            only ``name`` and ``phone``, so callers that haven't yet enriched
            the lead with a real e-mail address should place the address in
            the ``phone`` field until enrichment is available).
        """
        recipient = lead.get("email") or lead.get("phone", "")

        msg = MIMEText(
            f"Hi {lead.get('name', 'there')},\n\n"
            "We'd love to connect with you about your business."
        )
        msg["Subject"] = "Business Opportunity"
        msg["From"] = self.sender_email
        msg["To"] = recipient

        try:
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.password)
                server.sendmail(self.sender_email, recipient, msg.as_string())

            print(f"✅ Email sent to {lead.get('name', 'unknown')}")

        except Exception as exc:  # noqa: BLE001
            print(f"❌ Failed to send to {lead.get('name', 'unknown')}: {exc}")


# ---------------------------------------------------------------------------
# Legacy alias expected by problem-statement code snippets
# ---------------------------------------------------------------------------

class Bot(OutreachBot):
    """Alias retained for backwards-compatibility with problem-statement usage."""
