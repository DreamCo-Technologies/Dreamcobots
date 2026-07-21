"""
Sales Bot — main deal-closing bot that orchestrates SMS outreach, follow-ups,
and conversion tracking to drive revenue.

Daily Execution Loop:
  1. Pull 50–100 leads
  2. Send 10–20 messages
  3. Follow up with warm leads
  4. Log responses
  5. Close 1–3 deals

Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.
See framework/global_ai_sources_flow.py for the full pipeline specification.
"""

from __future__ import annotations

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from framework import GlobalAISourcesFlow  # noqa: F401  (GLOBAL AI SOURCES FLOW)

from typing import Optional

from bots.sales_bot.tiers import (
    Tier,
    TierConfig,
    get_tier_config,
    get_upgrade_path,
    FEATURE_SMS_OUTREACH,
    FEATURE_FOLLOWUP_BOT,
    FEATURE_CONVERSION_TRACKING,
    FEATURE_VOICE_BOT,
    FEATURE_REVENUE_TRACKING,
)
from bots.sales_bot.sms_bot import SMSBot
from bots.sales_bot.followup_bot import FollowUpBot
from bots.sales_bot.conversion_tracker import ConversionTracker, LeadStatus


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------

class SalesBotError(Exception):
    """Base exception for Sales Bot errors."""


class SalesBotTierError(SalesBotError):
    """Raised when a feature is not available on the current tier."""


# ---------------------------------------------------------------------------
# Sales Bot
# ---------------------------------------------------------------------------

class SalesBot:
    """
    DreamCo Sales Bot — automates the full deal-closing pipeline.

    Parameters
    ----------
    tier : Tier
        Subscription tier controlling features and message limits.
    niche : str
        Business niche to focus on (e.g., "roofing", "real estate").
    leads_per_day : int
        Target leads to process per daily run.
    messages_per_cycle : int
        Maximum messages per run cycle.
    """

    def __init__(
        self,
        tier: Tier = Tier.FREE,
        niche: str = "general",
        leads_per_day: int = 50,
        messages_per_cycle: int = 10,
        leads_path: Optional[str] = None,
    ) -> None:
        self.tier = tier
        self.niche = niche
        self.leads_per_day = leads_per_day
        self.messages_per_cycle = messages_per_cycle
        self._config: TierConfig = get_tier_config(tier)
        self._sms_bot = SMSBot(max_per_cycle=messages_per_cycle)
        self._followup_bot = FollowUpBot(
            leads_path=leads_path,
            max_followups=3,
        )
        self._conversion_tracker = ConversionTracker()
        self._run_log: list[dict] = []

    # ------------------------------------------------------------------
    # Tier enforcement
    # ------------------------------------------------------------------

    def _require(self, feature: str) -> None:
        if not self._config.has_feature(feature):
            upgrade = get_upgrade_path(self.tier)
            hint = (
                f" Upgrade to {upgrade.name} (${upgrade.price_usd_monthly}/mo)."
                if upgrade
                else ""
            )
            raise SalesBotTierError(
                f"Feature '{feature}' requires {self._config.name} tier.{hint}"
            )

    # ------------------------------------------------------------------
    # Core pipeline
    # ------------------------------------------------------------------

    def run_daily_cycle(self, leads: Optional[list[dict]] = None) -> dict:
        """
        Execute the full daily revenue loop.

        Steps:
          1. Pull/accept leads
          2. Send outreach messages
          3. Run follow-ups
          4. Return metrics

        Parameters
        ----------
        leads : list[dict], optional
            Leads to process. Each dict should have 'name' and 'phone'.

        Returns
        -------
        dict
            Summary of the day's activity.
        """
        self._require(FEATURE_SMS_OUTREACH)

        if not leads:
            leads = []

        # Register leads with tracker
        for i, lead in enumerate(leads):
            lead_id = lead.get("id", f"lead_{i:04d}")
            self._conversion_tracker.add_lead(
                lead_id=lead_id,
                name=lead.get("name", f"Lead {i}"),
                phone=lead.get("phone", ""),
            )
            self._conversion_tracker.update_status(lead_id, LeadStatus.CONTACTED)

        # Send messages (capped at messages_per_cycle)
        messages_sent = []
        if leads:
            messages_sent = self._sms_bot.send_batch(leads)
            for _ in messages_sent:
                self._conversion_tracker.record_message_sent()

        # Follow-ups (PRO+)
        followup_result = "Skipped (upgrade to PRO for follow-ups)"
        if self._config.has_feature(FEATURE_FOLLOWUP_BOT):
            followup_result = self._followup_bot.run()

        # Conversion metrics (PRO+)
        metrics: dict = {}
        if self._config.has_feature(FEATURE_CONVERSION_TRACKING):
            metrics = self._conversion_tracker.get_metrics()

        run_summary = {
            "leads_processed": len(leads),
            "messages_sent": len(messages_sent),
            "followup_result": followup_result,
            "conversion_metrics": metrics,
            "niche": self.niche,
            "tier": self.tier.value,
        }
        self._run_log.append(run_summary)
        return run_summary

    def close_deal(self, lead_id: str) -> dict:
        """Mark a lead as closed and record revenue."""
        updated = self._conversion_tracker.update_status(lead_id, LeadStatus.CLOSED)
        if not updated:
            return {"error": f"Lead {lead_id} not found"}
        metrics = self._conversion_tracker.get_metrics()
        return {
            "lead_id": lead_id,
            "status": "closed",
            "total_revenue_usd": metrics["revenue_usd"],
            "deals_closed": metrics["deals_closed"],
        }

    def mark_interested(self, lead_id: str) -> dict:
        """Mark a lead as interested."""
        updated = self._conversion_tracker.update_status(lead_id, LeadStatus.INTERESTED)
        return {"lead_id": lead_id, "status": "interested"} if updated else {"error": "not found"}

    def mark_no_response(self, lead_id: str) -> dict:
        """Mark a lead as no_response."""
        updated = self._conversion_tracker.update_status(lead_id, LeadStatus.NO_RESPONSE)
        return {"lead_id": lead_id, "status": "no_response"} if updated else {"error": "not found"}

    # ------------------------------------------------------------------
    # Reporting
    # ------------------------------------------------------------------

    def get_revenue(self) -> float:
        """Return total revenue generated."""
        return self._conversion_tracker.get_metrics().get("revenue_usd", 0.0)

    def get_conversion_metrics(self) -> dict:
        """Return current conversion metrics."""
        return self._conversion_tracker.get_metrics()

    def get_run_log(self) -> list[dict]:
        """Return the history of daily run cycles."""
        return list(self._run_log)

    def get_offer_message(self, business_name: str) -> str:
        """Return the irresistible offer message for a business."""
        return (
            f"Hey {business_name} — we found 5 people in your area looking for "
            f"your service this week. We can send them directly to you. "
            f"Want me to show you how?"
        )

    def run(self) -> str:
        """GLOBAL AI SOURCES FLOW framework entry point."""
        result = self.run_daily_cycle()
        return (
            f"💰 Sales Bot running. Niche: {self.niche}. "
            f"Messages sent: {result['messages_sent']}. "
            f"Revenue: ${self.get_revenue():.2f}."
        )

    def process(self, payload: dict) -> dict:
        """GLOBAL AI SOURCES FLOW framework entry point."""
        leads = payload.get("leads", [])
        return self.run_daily_cycle(leads=leads)
