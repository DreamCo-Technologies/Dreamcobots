"""
Advertising & Marketing Team Bot — Main Module

An AI-powered advertising and marketing automation bot for the DreamCobots
ecosystem.  Executes a standardised sales pipeline through which every
DreamCo bot can run campaigns end-to-end.

Pipeline stages
---------------
Traffic → Lead Scraper → Validator → Outreach → Funnel → Appointment
       → Close → Payment → CRM → Automation → AI Agents

Features
--------
  • Traffic Generation  — drive targeted traffic via ads, SEO, and social
  • Lead Scraper        — collect qualified leads from multiple sources
  • Validator           — filter and enrich leads with quality scoring
  • Outreach            — automated personalised email / DM campaigns
  • Funnel              — nurture sequences and conversion tracking
  • Appointment         — calendar booking and confirmation automation
  • Close               — AI-assisted deal closing with objection handling
  • Payment             — payment link generation and collection
  • CRM Integration     — sync contacts, deals, and notes to CRM
  • Automation          — trigger-based workflow automation
  • AI Agents           — autonomous agents that run the full pipeline

Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.
See framework/global_ai_sources_flow.py for the full pipeline specification.

Usage
-----
    from bots.advertising_marketing_bot import AdvertisingMarketingBot, Tier

    bot = AdvertisingMarketingBot(tier=Tier.PRO)

    # Trigger the Advertising and Marketing Team Button
    result = bot.advertising_marketing_team(
        campaign_name="Q1 Growth Drive",
        target_audience="small business owners",
        budget_usd=500.0,
    )
    print(result["pipeline_complete"])  # True
"""

from __future__ import annotations

import sys
import os
import random
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Optional

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from framework import GlobalAISourcesFlow
from bots.advertising_marketing_bot.tiers import (
    Tier,
    TierConfig,
    get_tier_config,
    get_upgrade_path,
    FEATURE_TRAFFIC_GENERATION,
    FEATURE_LEAD_SCRAPER,
    FEATURE_LEAD_VALIDATOR,
    FEATURE_OUTREACH,
    FEATURE_FUNNEL,
    FEATURE_APPOINTMENT,
    FEATURE_CLOSE,
    FEATURE_PAYMENT,
    FEATURE_CRM_INTEGRATION,
    FEATURE_AUTOMATION,
    FEATURE_AI_AGENTS,
)


# ---------------------------------------------------------------------------
# Pipeline simulation constants
# ---------------------------------------------------------------------------

MIN_VISITORS_PER_DOLLAR: float = 5.0
MAX_VISITORS_PER_DOLLAR: float = 20.0
LEAD_VALIDATION_THRESHOLD: float = 0.5
OUTREACH_OPEN_RATE: float = 0.4
OUTREACH_REPLY_RATE: float = 0.6
APPOINTMENT_CONFIRMATION_RATE: float = 0.5
DEAL_CLOSE_RATE: float = 0.6
DEAL_MIN_VALUE_USD: float = 500.0
DEAL_MAX_VALUE_USD: float = 5000.0
PAYMENT_DEFAULT_RATE: float = 0.2


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------

class AdvertisingMarketingError(Exception):
    """Base exception for Advertising & Marketing Bot errors."""


class AdvertisingMarketingTierError(AdvertisingMarketingError):
    """Raised when a feature is unavailable on the current tier."""


# ---------------------------------------------------------------------------
# Pipeline stage data models
# ---------------------------------------------------------------------------

@dataclass
class TrafficResult:
    """Output from the Traffic Generation stage."""
    source: str
    visitors: int
    cost_usd: float
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


@dataclass
class Lead:
    """A qualified lead produced by the Lead Scraper stage."""
    lead_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    email: str = ""
    phone: str = ""
    source: str = ""
    score: float = 0.0
    status: str = "raw"
    campaign: str = ""
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


@dataclass
class OutreachResult:
    """Result of an outreach sequence."""
    lead_id: str
    channel: str
    message_sent: bool = True
    opened: bool = False
    replied: bool = False


@dataclass
class AppointmentResult:
    """Appointment booking result."""
    lead_id: str
    scheduled_at: str = ""
    confirmed: bool = False
    calendar_event_id: str = field(default_factory=lambda: str(uuid.uuid4()))


@dataclass
class DealResult:
    """Deal close result."""
    lead_id: str
    closed: bool = False
    deal_value_usd: float = 0.0
    close_reason: str = ""


@dataclass
class PaymentResult:
    """Payment collection result."""
    lead_id: str
    amount_usd: float = 0.0
    payment_link: str = ""
    paid: bool = False
    transaction_id: str = field(default_factory=lambda: str(uuid.uuid4()))


@dataclass
class CRMRecord:
    """CRM contact / deal record."""
    lead_id: str
    crm_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    synced: bool = True
    synced_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


# ---------------------------------------------------------------------------
# Main Bot
# ---------------------------------------------------------------------------

class AdvertisingMarketingBot:
    """
    Advertising & Marketing Team Bot.

    Automates the full sales & marketing pipeline:
    Traffic → Lead Scraper → Validator → Outreach → Funnel →
    Appointment → Close → Payment → CRM → AI Agents.
    """

    def __init__(self, tier: Tier = Tier.FREE, bot_name: str = "AdvertisingMarketingBot") -> None:
        self.tier = tier
        self.tier_config: TierConfig = get_tier_config(tier)
        self.bot_name = bot_name
        self.flow = GlobalAISourcesFlow(bot_name=bot_name)
        self._leads: list[Lead] = []
        self._crm_records: list[CRMRecord] = []
        self._pipeline_runs: list[dict] = []

    # ------------------------------------------------------------------
    # Advertising and Marketing Team Button — main entry point
    # ------------------------------------------------------------------

    def advertising_marketing_team(
        self,
        campaign_name: str = "Default Campaign",
        target_audience: str = "general",
        budget_usd: float = 100.0,
        lead_count: int = 10,
    ) -> dict[str, Any]:
        """
        Trigger the full Advertising and Marketing Team pipeline.

        Executes all available stages in sequence:
        Traffic → Lead Scraper → Validator → Outreach → Funnel →
        Appointment → Close → Payment → CRM → Automation → AI Agents

        Parameters
        ----------
        campaign_name : str
            Human-readable name for this campaign run.
        target_audience : str
            Audience segment to target (e.g. "small business owners").
        budget_usd : float
            Total ad spend budget in USD.
        lead_count : int
            Number of leads to generate in this run.

        Returns
        -------
        dict
            A summary of the full pipeline execution.
        """
        result: dict[str, Any] = {
            "campaign_name": campaign_name,
            "target_audience": target_audience,
            "budget_usd": budget_usd,
            "tier": self.tier.value,
            "pipeline_complete": False,
            "stages": {},
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        # Stage 1 — Traffic Generation
        traffic = self._generate_traffic(target_audience, budget_usd)
        result["stages"]["traffic"] = {
            "visitors": traffic.visitors,
            "source": traffic.source,
            "cost_usd": traffic.cost_usd,
        }

        # Stage 2 — Lead Scraper
        leads = self._scrape_leads(campaign_name, lead_count)
        result["stages"]["lead_scraper"] = {"leads_collected": len(leads)}

        # Stage 3 — Validator
        valid_leads = self._validate_leads(leads)
        result["stages"]["validator"] = {
            "leads_validated": len(valid_leads),
            "leads_rejected": len(leads) - len(valid_leads),
        }

        if self.tier_config.has_feature(FEATURE_OUTREACH):
            # Stage 4 — Outreach
            outreach = self._run_outreach(valid_leads)
            result["stages"]["outreach"] = {
                "messages_sent": sum(1 for o in outreach if o.message_sent),
                "replies": sum(1 for o in outreach if o.replied),
            }

            # Stage 5 — Funnel
            funnel_result = self._run_funnel(valid_leads)
            result["stages"]["funnel"] = funnel_result

            # Stage 6 — Appointment
            appointments = self._book_appointments(valid_leads)
            result["stages"]["appointment"] = {
                "booked": sum(1 for a in appointments if a.confirmed),
                "total": len(appointments),
            }

            # Stage 7 — Close
            deals = self._close_deals(valid_leads)
            result["stages"]["close"] = {
                "closed": sum(1 for d in deals if d.closed),
                "total_value_usd": sum(d.deal_value_usd for d in deals if d.closed),
            }

            # Stage 8 — Payment
            payments = self._collect_payments(deals)
            result["stages"]["payment"] = {
                "collected": sum(1 for p in payments if p.paid),
                "total_collected_usd": sum(p.amount_usd for p in payments if p.paid),
            }

        if self.tier_config.has_feature(FEATURE_CRM_INTEGRATION):
            # Stage 9 — CRM
            crm_records = self._sync_crm(valid_leads)
            result["stages"]["crm"] = {"records_synced": len(crm_records)}

        if self.tier_config.has_feature(FEATURE_AUTOMATION):
            result["stages"]["automation"] = self._run_automation(campaign_name)

        if self.tier_config.has_feature(FEATURE_AI_AGENTS):
            result["stages"]["ai_agents"] = self._run_ai_agents(campaign_name)

        # Run GlobalAISourcesFlow pipeline
        flow_result = self.flow.run_pipeline(
            raw_data={"campaign": campaign_name, "leads": len(valid_leads)},
            learning_method="supervised",
        )
        result["flow_pipeline"] = {"pipeline_complete": flow_result.get("pipeline_complete", True)}
        result["pipeline_complete"] = True

        self._pipeline_runs.append(result)
        return result

    # ------------------------------------------------------------------
    # Stage implementations
    # ------------------------------------------------------------------

    def _generate_traffic(self, target_audience: str, budget_usd: float) -> TrafficResult:
        """Stage 1 — generate traffic via ads and organic channels."""
        visitors = max(1, int(budget_usd * random.uniform(MIN_VISITORS_PER_DOLLAR, MAX_VISITORS_PER_DOLLAR)))
        return TrafficResult(
            source="multi_channel",
            visitors=visitors,
            cost_usd=budget_usd,
        )

    def _scrape_leads(self, campaign: str, count: int) -> list[Lead]:
        """Stage 2 — scrape leads up to tier limit."""
        limit = self.tier_config.max_leads_per_day
        if limit is not None:
            count = min(count, limit)
        leads = []
        for i in range(count):
            lead = Lead(
                name=f"Lead {i + 1}",
                email=f"lead{i + 1}@example.com",
                phone=f"+1-555-{1000 + i:04d}",
                source="scraped",
                score=round(random.uniform(0.3, 1.0), 2),
                campaign=campaign,
            )
            leads.append(lead)
        self._leads.extend(leads)
        return leads

    def _validate_leads(self, leads: list[Lead]) -> list[Lead]:
        """Stage 3 — validate and score leads; keep those scoring ≥ threshold."""
        valid = []
        for lead in leads:
            if lead.score >= LEAD_VALIDATION_THRESHOLD:
                lead.status = "validated"
                valid.append(lead)
            else:
                lead.status = "rejected"
        return valid

    def _run_outreach(self, leads: list[Lead]) -> list[OutreachResult]:
        """Stage 4 — send personalised outreach messages."""
        results = []
        for lead in leads:
            opened = random.random() > OUTREACH_OPEN_RATE
            replied = opened and random.random() > OUTREACH_REPLY_RATE
            results.append(OutreachResult(
                lead_id=lead.lead_id,
                channel="email",
                message_sent=True,
                opened=opened,
                replied=replied,
            ))
        return results

    def _run_funnel(self, leads: list[Lead]) -> dict[str, Any]:
        """Stage 5 — run leads through conversion funnel."""
        return {
            "leads_in_funnel": len(leads),
            "conversion_rate": round(random.uniform(0.1, 0.4), 2),
        }

    def _book_appointments(self, leads: list[Lead]) -> list[AppointmentResult]:
        """Stage 6 — book appointments with interested leads."""
        results = []
        for lead in leads:
            confirmed = random.random() > APPOINTMENT_CONFIRMATION_RATE
            results.append(AppointmentResult(
                lead_id=lead.lead_id,
                scheduled_at=datetime.now(timezone.utc).isoformat(),
                confirmed=confirmed,
            ))
        return results

    def _close_deals(self, leads: list[Lead]) -> list[DealResult]:
        """Stage 7 — attempt to close deals with booked leads."""
        results = []
        for lead in leads:
            closed = random.random() > DEAL_CLOSE_RATE
            results.append(DealResult(
                lead_id=lead.lead_id,
                closed=closed,
                deal_value_usd=round(random.uniform(DEAL_MIN_VALUE_USD, DEAL_MAX_VALUE_USD), 2) if closed else 0.0,
                close_reason="signed" if closed else "no_response",
            ))
        return results

    def _collect_payments(self, deals: list[DealResult]) -> list[PaymentResult]:
        """Stage 8 — generate payment links and collect payments."""
        results = []
        for deal in deals:
            if deal.closed:
                paid = random.random() > PAYMENT_DEFAULT_RATE
                results.append(PaymentResult(
                    lead_id=deal.lead_id,
                    amount_usd=deal.deal_value_usd,
                    payment_link=f"https://pay.dreamcobots.com/{deal.lead_id}",
                    paid=paid,
                ))
        return results

    def _sync_crm(self, leads: list[Lead]) -> list[CRMRecord]:
        """Stage 9 — sync validated leads to CRM."""
        records = []
        for lead in leads:
            record = CRMRecord(lead_id=lead.lead_id)
            self._crm_records.append(record)
            records.append(record)
        return records

    def _run_automation(self, campaign_name: str) -> dict[str, Any]:
        """Stage 10 — trigger-based workflow automation."""
        return {
            "workflows_triggered": random.randint(1, 5),
            "campaign": campaign_name,
            "status": "active",
        }

    def _run_ai_agents(self, campaign_name: str) -> dict[str, Any]:
        """Stage 11 — autonomous AI agents run the full pipeline."""
        return {
            "agents_active": random.randint(1, 3),
            "campaign": campaign_name,
            "status": "running",
        }

    # ------------------------------------------------------------------
    # Utilities
    # ------------------------------------------------------------------

    def get_leads(self) -> list[Lead]:
        """Return all leads collected in this session."""
        return list(self._leads)

    def get_crm_records(self) -> list[CRMRecord]:
        """Return all CRM records synced in this session."""
        return list(self._crm_records)

    def get_pipeline_runs(self) -> list[dict]:
        """Return the history of pipeline run summaries."""
        return list(self._pipeline_runs)

    def get_tier_info(self) -> dict[str, Any]:
        """Return tier details for this bot instance."""
        return {
            "tier": self.tier.value,
            "name": self.tier_config.name,
            "price_usd_monthly": self.tier_config.price_usd_monthly,
            "max_leads_per_day": self.tier_config.max_leads_per_day,
            "max_campaigns": self.tier_config.max_campaigns,
            "features": self.tier_config.features,
        }

    def upgrade_tier(self) -> Optional[TierConfig]:
        """Return the next tier config, or None if already on ENTERPRISE."""
        return get_upgrade_path(self.tier)

    def chat(self, message: str) -> dict[str, Any]:
        """Simple chat interface to the Advertising & Marketing Bot."""
        message_lower = message.lower()
        if any(kw in message_lower for kw in ["campaign", "start", "run", "launch"]):
            return {
                "message": (
                    "Launching the Advertising and Marketing Team pipeline! "
                    "Use advertising_marketing_team() to start a campaign."
                ),
                "action": "suggest_pipeline",
            }
        if "lead" in message_lower:
            return {
                "message": f"You currently have {len(self._leads)} leads in your pipeline.",
                "action": "report_leads",
            }
        if "crm" in message_lower:
            return {
                "message": f"{len(self._crm_records)} records have been synced to your CRM.",
                "action": "report_crm",
            }
        if "upgrade" in message_lower:
            next_tier = self.upgrade_tier()
            if next_tier:
                return {
                    "message": f"Upgrade to {next_tier.name} for ${next_tier.price_usd_monthly}/mo to unlock more features.",
                    "action": "suggest_upgrade",
                }
            return {"message": "You're already on the ENTERPRISE tier!", "action": "already_max"}
        return {
            "message": (
                "I'm your Advertising & Marketing Team Bot. "
                "I can help with traffic generation, lead scraping, outreach, "
                "appointments, closing deals, and CRM integration."
            ),
            "action": "general_help",
        }
