"""
Buddy Bot — Retention + Upsell Engine

Keeps revenue flowing by maximising client lifetime value:
  • Health scoring       — detects at-risk accounts before they churn
  • Check-in automation  — scheduled client success touchpoints
  • Upsell detection     — identifies the best upsell moment per client
  • Upsell offer builder — generates ready-to-send upgrade proposals
  • Revenue reporting    — monthly MRR, churn rate, LTV analytics
  • Referral triggers    — asks for referrals at peak satisfaction moments

Tier access
-----------
  FREE:       Basic health scoring, manual check-in reminders.
  PRO:        Automated check-ins, upsell detection, basic revenue reporting.
  ENTERPRISE: Full retention suite — referral engine, churn prediction,
              AI-personalised upsell campaigns, multi-client MRR dashboard.

GLOBAL AI SOURCES FLOW: this module participates in GlobalAISourcesFlow
via BuddyBot.
"""

from __future__ import annotations

import random
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Optional


def _slugify(name: str) -> str:
    """Convert *name* to a URL-safe slug."""
    slug = name.lower()
    slug = re.sub(r"[^a-z0-9\s-]", "", slug)
    slug = re.sub(r"[\s-]+", "-", slug).strip("-")
    return slug


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class HealthStatus(Enum):
    HEALTHY = "healthy"
    AT_RISK = "at_risk"
    CHURNING = "churning"
    INACTIVE = "inactive"
    CHAMPION = "champion"


class UpsellStage(Enum):
    NOT_READY = "not_ready"
    WARM = "warm"
    READY = "ready"
    OFFERED = "offered"
    ACCEPTED = "accepted"
    DECLINED = "declined"


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class ClientHealthRecord:
    """Tracks a retained client's health and engagement metrics."""

    client_id: str
    client_name: str
    plan_name: str
    monthly_value_usd: float
    months_active: int
    last_contact_days_ago: int
    results_delivered: int           # number of deliverables deployed
    satisfaction_score: float        # 0.0–10.0
    health_status: HealthStatus = HealthStatus.HEALTHY
    upsell_stage: UpsellStage = UpsellStage.NOT_READY
    lifetime_value_usd: float = 0.0
    referrals_generated: int = 0
    notes: list = field(default_factory=list)

    def compute_health(self) -> HealthStatus:
        """Recompute health status from current metrics."""
        if self.satisfaction_score >= 8.5 and self.months_active >= 3:
            self.health_status = HealthStatus.CHAMPION
        elif self.last_contact_days_ago > 30 or self.satisfaction_score < 4.0:
            self.health_status = HealthStatus.CHURNING
        elif self.last_contact_days_ago > 14 or self.satisfaction_score < 6.0:
            self.health_status = HealthStatus.AT_RISK
        elif self.results_delivered == 0:
            self.health_status = HealthStatus.INACTIVE
        else:
            self.health_status = HealthStatus.HEALTHY
        self.lifetime_value_usd = self.monthly_value_usd * self.months_active
        return self.health_status

    def to_dict(self) -> dict:
        return {
            "client_id": self.client_id,
            "client_name": self.client_name,
            "plan_name": self.plan_name,
            "monthly_value_usd": self.monthly_value_usd,
            "months_active": self.months_active,
            "last_contact_days_ago": self.last_contact_days_ago,
            "results_delivered": self.results_delivered,
            "satisfaction_score": self.satisfaction_score,
            "health_status": self.health_status.value,
            "upsell_stage": self.upsell_stage.value,
            "lifetime_value_usd": self.lifetime_value_usd,
            "referrals_generated": self.referrals_generated,
            "notes": self.notes,
        }


@dataclass
class CheckIn:
    """A scheduled client success check-in."""

    checkin_id: str
    client_name: str
    message: str
    channel: str
    scheduled_at: str
    completed: bool = False

    def to_dict(self) -> dict:
        return {
            "checkin_id": self.checkin_id,
            "client_name": self.client_name,
            "message": self.message,
            "channel": self.channel,
            "scheduled_at": self.scheduled_at,
            "completed": self.completed,
        }


@dataclass
class UpsellOffer:
    """A targeted upsell proposal for an existing client."""

    offer_id: str
    client_name: str
    current_plan: str
    proposed_plan: str
    upgrade_value_usd: float
    headline: str
    reason: str
    new_features: list
    incentive: Optional[str]

    def to_dict(self) -> dict:
        return {
            "offer_id": self.offer_id,
            "client_name": self.client_name,
            "current_plan": self.current_plan,
            "proposed_plan": self.proposed_plan,
            "upgrade_value_usd": self.upgrade_value_usd,
            "headline": self.headline,
            "reason": self.reason,
            "new_features": self.new_features,
            "incentive": self.incentive,
        }


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------

class RetentionEngineError(Exception):
    """Base exception for RetentionEngine errors."""


class RetentionEngineTierError(RetentionEngineError):
    """Raised when a feature is not available on the current tier."""


# ---------------------------------------------------------------------------
# Check-in message templates
# ---------------------------------------------------------------------------

_CHECKIN_MESSAGES = [
    "Hi {client}! Just checking in — how are the results landing so far? Let us know if there's anything we can optimise. 🚀",
    "Hey {client} team! Quick update: your campaign has been live for {days} days. Reply to see your latest metrics.",
    "{client} — you're at the {months}-month mark! We're pulling together your growth report. Anything specific you'd like us to focus on?",
    "Hi {client}! We noticed some exciting trends in your data. Got 10 minutes to review them together?",
    "{client} — your referral link is ready. Know any business owners who'd benefit from this system?",
]

# Upsell plan map: current plan → proposed upgrade
_UPSELL_MAP = {
    "starter": {
        "next_plan": "Business",
        "upgrade_features": [
            "AI lead generation (30–100 leads/month)",
            "Multi-platform ad campaigns",
            "Email marketing automation",
            "Monthly strategy call",
        ],
        "price_increase_usd": 70.0,
    },
    "business": {
        "next_plan": "Pro",
        "upgrade_features": [
            "Full AI workforce (5 specialised agents)",
            "SMS marketing",
            "Sales funnel builder",
            "CRM automation",
            "Weekly reporting dashboard",
        ],
        "price_increase_usd": 200.0,
    },
    "pro": {
        "next_plan": "Agency",
        "upgrade_features": [
            "Multi-client management (up to 10 clients)",
            "White-label reports",
            "AI voice agent for follow-ups",
            "Revenue-share option",
            "Dedicated account manager",
        ],
        "price_increase_usd": 700.0,
    },
    "agency": {
        "next_plan": "Enterprise",
        "upgrade_features": [
            "Unlimited clients",
            "Custom AI agent training",
            "API access",
            "Full SaaS platform licence",
            "Revenue optimizer bot",
        ],
        "price_increase_usd": 3000.0,
    },
}


# ---------------------------------------------------------------------------
# RetentionEngine
# ---------------------------------------------------------------------------

class RetentionEngine:
    """Maximises client lifetime value through proactive retention and upsells.

    Parameters
    ----------
    can_auto_checkins : bool
        Whether automated check-in scheduling is enabled.
    can_upsell_detection : bool
        Whether AI upsell moment detection is available.
    can_referral_engine : bool
        Whether the referral trigger system is available.
    can_churn_prediction : bool
        Whether advanced churn prediction is available.
    can_mrr_dashboard : bool
        Whether the full MRR analytics dashboard is available.
    """

    def __init__(
        self,
        can_auto_checkins: bool = False,
        can_upsell_detection: bool = False,
        can_referral_engine: bool = False,
        can_churn_prediction: bool = False,
        can_mrr_dashboard: bool = False,
    ) -> None:
        self.can_auto_checkins = can_auto_checkins
        self.can_upsell_detection = can_upsell_detection
        self.can_referral_engine = can_referral_engine
        self.can_churn_prediction = can_churn_prediction
        self.can_mrr_dashboard = can_mrr_dashboard
        self._clients: dict[str, ClientHealthRecord] = {}
        self._checkins: list[CheckIn] = []
        self._upsell_offers: list[UpsellOffer] = []
        self._counter: int = 0

    # ------------------------------------------------------------------
    # Client management
    # ------------------------------------------------------------------

    def add_client(
        self,
        client_name: str,
        plan_name: str,
        monthly_value_usd: float,
        months_active: int = 1,
        satisfaction_score: float = 7.0,
        results_delivered: int = 0,
        last_contact_days_ago: int = 0,
    ) -> ClientHealthRecord:
        """Register a client in the retention system.

        Parameters
        ----------
        client_name : str
            Client business name.
        plan_name : str
            Current subscription plan.
        monthly_value_usd : float
            Monthly recurring revenue from this client.
        months_active : int
            How long they've been a client.
        satisfaction_score : float
            Current satisfaction (0–10).
        results_delivered : int
            Number of deliverables deployed.
        last_contact_days_ago : int
            Days since last touchpoint.

        Returns
        -------
        ClientHealthRecord
        """
        self._counter += 1
        record = ClientHealthRecord(
            client_id=f"client_{self._counter:04d}",
            client_name=client_name,
            plan_name=plan_name.lower(),
            monthly_value_usd=monthly_value_usd,
            months_active=months_active,
            last_contact_days_ago=last_contact_days_ago,
            results_delivered=results_delivered,
            satisfaction_score=satisfaction_score,
        )
        record.compute_health()
        self._clients[client_name] = record
        return record

    def score_health(self, client_name: str) -> ClientHealthRecord:
        """Recompute and return the health record for a client.

        Parameters
        ----------
        client_name : str
            Client to score.

        Returns
        -------
        ClientHealthRecord
        """
        if client_name not in self._clients:
            raise RetentionEngineError(f"Client not found: {client_name}")
        record = self._clients[client_name]
        record.compute_health()
        return record

    def get_at_risk_clients(self) -> list[ClientHealthRecord]:
        """Return all clients with AT_RISK or CHURNING health status."""
        return [
            r for r in self._clients.values()
            if r.health_status in (HealthStatus.AT_RISK, HealthStatus.CHURNING)
        ]

    # ------------------------------------------------------------------
    # Check-ins
    # ------------------------------------------------------------------

    def schedule_checkin(
        self,
        client_name: str,
        channel: str = "email",
        days_from_now: int = 7,
    ) -> CheckIn:
        """Schedule a client check-in.

        Parameters
        ----------
        client_name : str
            Target client.
        channel : str
            Communication channel (email, sms, phone).
        days_from_now : int
            Days until the check-in should be sent.

        Returns
        -------
        CheckIn
        """
        if not self.can_auto_checkins:
            raise RetentionEngineTierError(
                "Automated check-ins require PRO tier or above."
            )
        record = self._clients.get(client_name)
        months = record.months_active if record else 1
        rng = random.Random(hash(client_name) + self._counter)
        message = rng.choice(_CHECKIN_MESSAGES).format(
            client=client_name, days=days_from_now, months=months
        )
        self._counter += 1
        checkin = CheckIn(
            checkin_id=f"ci_{self._counter:04d}",
            client_name=client_name,
            message=message,
            channel=channel,
            scheduled_at=(
                datetime.now(timezone.utc).isoformat()
            ),
        )
        self._checkins.append(checkin)
        return checkin

    # ------------------------------------------------------------------
    # Upsell detection & offers
    # ------------------------------------------------------------------

    def detect_upsell_moment(self, client_name: str) -> UpsellStage:
        """Detect whether a client is ready for an upsell.

        Parameters
        ----------
        client_name : str
            Client to evaluate.

        Returns
        -------
        UpsellStage
        """
        if not self.can_upsell_detection:
            raise RetentionEngineTierError(
                "Upsell detection requires PRO tier or above."
            )
        if client_name not in self._clients:
            raise RetentionEngineError(f"Client not found: {client_name}")
        record = self._clients[client_name]
        if (
            record.satisfaction_score >= 8.0
            and record.months_active >= 2
            and record.results_delivered >= 3
        ):
            record.upsell_stage = UpsellStage.READY
        elif (
            record.satisfaction_score >= 6.5
            and record.months_active >= 1
        ):
            record.upsell_stage = UpsellStage.WARM
        else:
            record.upsell_stage = UpsellStage.NOT_READY
        return record.upsell_stage

    def build_upsell_offer(self, client_name: str) -> UpsellOffer:
        """Generate a personalised upsell offer for a client.

        Parameters
        ----------
        client_name : str
            Client to upsell.

        Returns
        -------
        UpsellOffer
        """
        if not self.can_upsell_detection:
            raise RetentionEngineTierError(
                "Upsell offers require PRO tier or above."
            )
        if client_name not in self._clients:
            raise RetentionEngineError(f"Client not found: {client_name}")

        record = self._clients[client_name]
        plan = record.plan_name.lower()
        upsell_info = _UPSELL_MAP.get(plan, _UPSELL_MAP["starter"])
        self._counter += 1

        offer = UpsellOffer(
            offer_id=f"upsell_{self._counter:04d}",
            client_name=client_name,
            current_plan=record.plan_name,
            proposed_plan=upsell_info["next_plan"],
            upgrade_value_usd=upsell_info["price_increase_usd"],
            headline=(
                f"{client_name}, you're ready for the next level — "
                f"unlock {upsell_info['next_plan']} and grow 2x faster"
            ),
            reason=(
                f"Based on your {record.months_active} months of results and "
                f"{record.satisfaction_score}/10 satisfaction score, "
                f"you're the perfect fit for our {upsell_info['next_plan']} plan."
            ),
            new_features=upsell_info["upgrade_features"],
            incentive=(
                "Upgrade this month and get your first month at 50% off."
                if record.months_active >= 3 else None
            ),
        )
        self._upsell_offers.append(offer)
        record.upsell_stage = UpsellStage.OFFERED
        return offer

    # ------------------------------------------------------------------
    # Referral triggers
    # ------------------------------------------------------------------

    def trigger_referral_ask(self, client_name: str) -> dict:
        """Ask a champion client for a referral.

        Parameters
        ----------
        client_name : str
            Client to ask.

        Returns
        -------
        dict
            Referral ask message and incentive.
        """
        if not self.can_referral_engine:
            raise RetentionEngineTierError(
                "Referral engine requires ENTERPRISE tier."
            )
        if client_name not in self._clients:
            raise RetentionEngineError(f"Client not found: {client_name}")

        record = self._clients[client_name]
        if record.health_status not in (HealthStatus.CHAMPION, HealthStatus.HEALTHY):
            return {
                "eligible": False,
                "reason": "Client not yet ready for referral ask.",
            }

        record.referrals_generated += 1
        return {
            "eligible": True,
            "client": client_name,
            "message": (
                f"Hey {client_name}! You've been amazing to work with. "
                f"If you know any other business owners who could use a growth system like yours, "
                f"we'd love to help them too — and you'll earn $200 credit for every referral who signs up."
            ),
            "referral_link": f"https://dreamco.ai/refer/{_slugify(client_name)}",
            "incentive": "$200 account credit per successful referral",
        }

    # ------------------------------------------------------------------
    # Revenue analytics
    # ------------------------------------------------------------------

    def revenue_report(self) -> dict:
        """Return an MRR and retention analytics report.

        Returns
        -------
        dict
            Report containing MRR, churn rate, LTV, and health breakdown.
        """
        if not self.can_mrr_dashboard:
            raise RetentionEngineTierError(
                "Full MRR dashboard requires ENTERPRISE tier."
            )
        clients = list(self._clients.values())
        total_clients = len(clients)
        if total_clients == 0:
            return {"mrr_usd": 0, "total_clients": 0, "message": "No clients yet."}

        mrr = sum(c.monthly_value_usd for c in clients)
        avg_ltv = sum(c.lifetime_value_usd for c in clients) / total_clients
        churning = sum(1 for c in clients if c.health_status == HealthStatus.CHURNING)
        champions = sum(1 for c in clients if c.health_status == HealthStatus.CHAMPION)
        churn_rate = round(churning / total_clients * 100, 1)

        return {
            "mrr_usd": round(mrr, 2),
            "total_clients": total_clients,
            "average_ltv_usd": round(avg_ltv, 2),
            "churn_rate_pct": churn_rate,
            "champions": champions,
            "at_risk": sum(1 for c in clients if c.health_status == HealthStatus.AT_RISK),
            "churning": churning,
            "total_referrals": sum(c.referrals_generated for c in clients),
            "health_breakdown": {
                status.value: sum(1 for c in clients if c.health_status == status)
                for status in HealthStatus
            },
        }

    def simple_revenue_summary(self) -> dict:
        """Return basic revenue summary available on all tiers.

        Returns
        -------
        dict
        """
        clients = list(self._clients.values())
        return {
            "total_clients": len(clients),
            "mrr_usd": round(sum(c.monthly_value_usd for c in clients), 2),
        }

    # ------------------------------------------------------------------
    # Accessors
    # ------------------------------------------------------------------

    def get_client(self, client_name: str) -> ClientHealthRecord:
        """Return the health record for a specific client."""
        if client_name not in self._clients:
            raise RetentionEngineError(f"Client not found: {client_name}")
        return self._clients[client_name]

    def get_all_clients(self) -> list[ClientHealthRecord]:
        """Return all client health records."""
        return list(self._clients.values())

    def to_dict(self) -> dict:
        """Return engine state as a serialisable dict."""
        clients = list(self._clients.values())
        return {
            "total_clients": len(clients),
            "mrr_usd": round(sum(c.monthly_value_usd for c in clients), 2),
            "checkins_scheduled": len(self._checkins),
            "upsell_offers_sent": len(self._upsell_offers),
            "can_auto_checkins": self.can_auto_checkins,
            "can_upsell_detection": self.can_upsell_detection,
            "can_referral_engine": self.can_referral_engine,
            "can_churn_prediction": self.can_churn_prediction,
            "can_mrr_dashboard": self.can_mrr_dashboard,
        }
