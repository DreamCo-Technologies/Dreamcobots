"""
Follow-Up Bot — automates follow-up outreach to leads, since most money
happens on follow-up, not first contact.

Reads leads from data/leads.json and sends targeted follow-up messages.

Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.
See framework/global_ai_sources_flow.py for the full pipeline specification.
"""

from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from framework import GlobalAISourcesFlow  # noqa: F401  (GLOBAL AI SOURCES FLOW)

from datetime import datetime, timezone
from typing import Optional


_DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data")
_DEFAULT_LEADS_PATH = os.path.join(_DATA_DIR, "leads.json")

FOLLOWUP_TEMPLATE = (
    "Hey {name}, just following up!\n\n"
    "We still have people in your area looking for your service. "
    "Are you ready to start receiving customers?\n\n"
    "Reply YES and I'll set it up right away."
)

MAX_FOLLOWUPS_PER_RUN: int = 3


class FollowUpBot:
    """
    Automates follow-up messages to leads that haven't responded.

    Parameters
    ----------
    leads_path : str, optional
        Path to the leads JSON file.
    max_followups : int
        Maximum follow-ups per run (default: 3).
    template : str, optional
        Custom follow-up message template.
    """

    def __init__(
        self,
        leads_path: Optional[str] = None,
        max_followups: int = MAX_FOLLOWUPS_PER_RUN,
        template: Optional[str] = None,
    ) -> None:
        self.name = "Follow-Up Bot"
        self._leads_path = leads_path or _DEFAULT_LEADS_PATH
        self.max_followups = max_followups
        self.template = template or FOLLOWUP_TEMPLATE
        self._followup_log: list[dict] = []

    def _load_leads(self) -> list[dict]:
        """Load leads from the leads data file."""
        try:
            with open(self._leads_path, encoding="utf-8") as f:
                content = f.read().strip()
                if not content:
                    return []
                if content.startswith("["):
                    data = json.loads(content)
                    return data if isinstance(data, list) else []
                # JSONL format
                leads = []
                for line in content.splitlines():
                    line = line.strip()
                    if line:
                        try:
                            leads.append(json.loads(line))
                        except json.JSONDecodeError:
                            pass
                return leads
        except (FileNotFoundError, json.JSONDecodeError, OSError):
            return []

    def build_followup_message(self, lead: dict) -> str:
        """Build a personalized follow-up message."""
        name = lead.get("name", "there")
        return self.template.format(name=name)

    def send_followup(self, lead: dict) -> dict:
        """Send a follow-up to a single lead."""
        message = self.build_followup_message(lead)
        record = {
            "lead_name": lead.get("name", "unknown"),
            "phone": lead.get("phone", "unknown"),
            "message": message,
            "status": "followup_sent",
            "sent_at": datetime.now(timezone.utc).isoformat(),
        }
        self._followup_log.append(record)
        return record

    def run(self) -> str:
        """
        Load leads and send follow-ups to the first max_followups leads.

        Returns
        -------
        str
            Summary of follow-ups sent.
        """
        leads = self._load_leads()
        if not leads:
            return "No leads found for follow-up."

        target_leads = leads[: self.max_followups]
        for lead in target_leads:
            self.send_followup(lead)
            print(f"🔁 Following up with {lead.get('name', 'unknown')}")

        return f"📈 Follow-ups sent: {len(target_leads)}"

    def get_followup_log(self) -> list[dict]:
        """Return all follow-up records."""
        return list(self._followup_log)

    def get_followup_count(self) -> int:
        """Return total follow-ups sent."""
        return len(self._followup_log)
