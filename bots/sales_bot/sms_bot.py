"""
SMS Bot — sends irresistible, value-driven SMS outreach messages to leads.

Message template:
  "Hey [Business Name] — we found 5 people in your area looking for your
   service this week. We can send them directly to you. Want me to show you how?"

Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.
See framework/global_ai_sources_flow.py for the full pipeline specification.
"""

from __future__ import annotations

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from framework import GlobalAISourcesFlow  # noqa: F401  (GLOBAL AI SOURCES FLOW)

from datetime import datetime, timezone
from typing import Optional


# ---------------------------------------------------------------------------
# Default message template
# ---------------------------------------------------------------------------

DEFAULT_SMS_TEMPLATE = (
    "Hey {name},\n\n"
    "We found people in your area actively looking for your service this week.\n\n"
    "We can send them directly to you.\n\n"
    "Want me to send one over?"
)

IRRESISTIBLE_OFFER_TEMPLATE = (
    "Hey {name} — we found 5 people in your area looking for your service this week. "
    "We can send them directly to you. Want me to show you how?"
)


# ---------------------------------------------------------------------------
# SMS Bot
# ---------------------------------------------------------------------------

class SMSBot:
    """
    Sends value-driven SMS outreach messages to leads.

    Simulates Twilio SMS delivery (real Twilio integration requires credentials).

    Parameters
    ----------
    from_number : str
        Sender phone number.
    max_per_cycle : int
        Maximum messages per run cycle (safety limit).
    template : str, optional
        Custom message template (uses {name} placeholder).
    """

    def __init__(
        self,
        from_number: str = "+15550000001",
        max_per_cycle: int = 10,
        template: Optional[str] = None,
    ) -> None:
        self.name = "SMS Bot"
        self.from_number = from_number
        self.max_per_cycle = max_per_cycle
        self.template = template or DEFAULT_SMS_TEMPLATE
        self._messages_sent: list[dict] = []

    def build_message(self, lead: dict) -> str:
        """Build a personalized SMS message for a lead."""
        name = lead.get("name", "there")
        return self.template.format(name=name)

    def send_sms(self, lead: dict) -> dict:
        """
        Send (simulate) an SMS to a lead.

        Parameters
        ----------
        lead : dict
            Must contain 'name' and 'phone' keys.

        Returns
        -------
        dict
            Message record with status.
        """
        message_body = self.build_message(lead)
        record = {
            "to": lead.get("phone", "unknown"),
            "from": self.from_number,
            "body": message_body,
            "lead_name": lead.get("name", "unknown"),
            "status": "sent",
            "sent_at": datetime.now(timezone.utc).isoformat(),
        }
        self._messages_sent.append(record)
        return record

    def send_batch(self, leads: list[dict]) -> list[dict]:
        """
        Send SMS messages to a list of leads, capped at max_per_cycle.

        Parameters
        ----------
        leads : list[dict]
            List of lead dicts with 'name' and 'phone'.

        Returns
        -------
        list[dict]
            Records of all messages sent this batch.
        """
        batch = leads[: self.max_per_cycle]
        results = []
        for lead in batch:
            result = self.send_sms(lead)
            results.append(result)
        return results

    def get_messages_sent(self) -> list[dict]:
        """Return all sent message records."""
        return list(self._messages_sent)

    def get_send_count(self) -> int:
        """Return the total number of messages sent."""
        return len(self._messages_sent)

    def run(self) -> str:
        """GLOBAL AI SOURCES FLOW framework entry point."""
        return (
            f"📱 SMS Bot active. "
            f"Messages sent: {self.get_send_count()}. "
            f"Max per cycle: {self.max_per_cycle}."
        )
