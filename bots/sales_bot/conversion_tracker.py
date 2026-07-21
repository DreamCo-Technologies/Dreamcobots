"""
Conversion Tracker — tracks lead statuses (interested, closed, no_response)
and real conversion metrics (replies, deals closed, revenue).

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
from enum import Enum
from typing import Optional


# ---------------------------------------------------------------------------
# Lead status
# ---------------------------------------------------------------------------

class LeadStatus(Enum):
    NEW = "new"
    CONTACTED = "contacted"
    INTERESTED = "interested"
    CLOSED = "closed"
    NO_RESPONSE = "no_response"
    LOST = "lost"


_DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data")


# ---------------------------------------------------------------------------
# Conversion Tracker
# ---------------------------------------------------------------------------

class ConversionTracker:
    """
    Tracks lead conversions and real metrics for the deal-closing pipeline.

    Metrics tracked:
    - Leads collected
    - Messages sent
    - Replies received
    - Deals closed
    - Revenue generated

    Parameters
    ----------
    data_dir : str, optional
        Directory for storing conversion data.
    revenue_per_deal : float
        Revenue amount per closed deal (default: $50.00).
    """

    def __init__(
        self,
        data_dir: Optional[str] = None,
        revenue_per_deal: float = 50.0,
    ) -> None:
        self.revenue_per_deal = revenue_per_deal
        self._data_dir = data_dir or _DATA_DIR
        self._leads: dict[str, dict] = {}
        self._messages_sent: int = 0
        self._revenue: float = 0.0
        self._conversion_log: list[dict] = []

    # ------------------------------------------------------------------
    # Lead management
    # ------------------------------------------------------------------

    def add_lead(self, lead_id: str, name: str, phone: str = "", **kwargs) -> dict:
        """Add a new lead with status 'new'."""
        lead = {
            "lead_id": lead_id,
            "name": name,
            "phone": phone,
            "status": LeadStatus.NEW.value,
            "added_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
            **kwargs,
        }
        self._leads[lead_id] = lead
        return lead

    def update_status(self, lead_id: str, status: LeadStatus) -> Optional[dict]:
        """Update a lead's status and log the conversion event."""
        if lead_id not in self._leads:
            return None
        self._leads[lead_id]["status"] = status.value
        self._leads[lead_id]["updated_at"] = datetime.now(timezone.utc).isoformat()

        event = {
            "lead_id": lead_id,
            "old_status": self._leads[lead_id].get("status"),
            "new_status": status.value,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        self._conversion_log.append(event)

        if status == LeadStatus.CLOSED:
            self._revenue += self.revenue_per_deal

        return self._leads[lead_id]

    def record_message_sent(self) -> int:
        """Record that a message was sent. Returns new total."""
        self._messages_sent += 1
        return self._messages_sent

    # ------------------------------------------------------------------
    # Metrics
    # ------------------------------------------------------------------

    def get_metrics(self) -> dict:
        """Return all real conversion metrics."""
        by_status: dict[str, int] = {}
        for lead in self._leads.values():
            s = lead["status"]
            by_status[s] = by_status.get(s, 0) + 1

        total = len(self._leads)
        closed = by_status.get(LeadStatus.CLOSED.value, 0)
        interested = by_status.get(LeadStatus.INTERESTED.value, 0)
        no_response = by_status.get(LeadStatus.NO_RESPONSE.value, 0)

        conversion_rate = round((closed / total * 100), 2) if total > 0 else 0.0
        reply_rate = round(
            ((closed + interested) / self._messages_sent * 100), 2
        ) if self._messages_sent > 0 else 0.0

        return {
            "leads_collected": total,
            "messages_sent": self._messages_sent,
            "replies": closed + interested,
            "interested": interested,
            "deals_closed": closed,
            "no_response": no_response,
            "revenue_usd": round(self._revenue, 2),
            "conversion_rate_pct": conversion_rate,
            "reply_rate_pct": reply_rate,
            "by_status": by_status,
        }

    def get_leads_by_status(self, status: LeadStatus) -> list[dict]:
        """Return all leads with the given status."""
        return [
            lead for lead in self._leads.values()
            if lead["status"] == status.value
        ]

    def get_conversion_log(self) -> list[dict]:
        """Return the full conversion event log."""
        return list(self._conversion_log)

    def get_all_leads(self) -> list[dict]:
        """Return all tracked leads."""
        return list(self._leads.values())
