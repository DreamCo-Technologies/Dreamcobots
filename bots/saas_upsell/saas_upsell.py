"""
SaaS Upsell + Subscription Revenue Framework

Manages subscriber onboarding (via tutorial bots), tier upgrades, and a
micro-business network that consolidates recurring revenue streams.

Features
--------
  - Subscriber registration and onboarding tutorial flow
  - Tier-based upsell recommendations (FREE → PRO → SCALE → ENTERPRISE)
  - Micro-business network: each member contributes a revenue share
  - Recurring-stream dashboard metrics (MRR, ARR, churn)

Revenue hook output:
    {
        "revenue": MRR + one-time upsell fees,
        "leads_generated": new subscribers this cycle,
        "conversion_rate": upsell acceptance rate,
        "action": description,
    }
"""

from __future__ import annotations

import sys
import os
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List, Optional

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from framework import GlobalAISourcesFlow  # noqa: F401


# ---------------------------------------------------------------------------
# Tier definitions
# ---------------------------------------------------------------------------


class SubscriptionTier(Enum):
    FREE = "FREE"
    PRO = "PRO"
    SCALE = "SCALE"
    ENTERPRISE = "ENTERPRISE"


TIER_MONTHLY_PRICE: Dict[str, float] = {
    "FREE": 0.0,
    "PRO": 29.0,
    "SCALE": 99.0,
    "ENTERPRISE": 499.0,
}

ONBOARDING_STEPS = [
    "Welcome & account setup",
    "Connect first data source",
    "Run first bot",
    "Review revenue dashboard",
    "Set scaling thresholds",
]


# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------


@dataclass
class Subscriber:
    subscriber_id: str
    email: str
    tier: SubscriptionTier = SubscriptionTier.FREE
    onboarding_step: int = 0
    onboarding_complete: bool = False
    upsell_offers_accepted: int = 0
    upsell_offers_declined: int = 0
    joined_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    upgraded_at: Optional[str] = None

    @property
    def monthly_revenue(self) -> float:
        return TIER_MONTHLY_PRICE.get(self.tier.value, 0.0)

    def to_dict(self) -> dict:
        return {
            "subscriber_id": self.subscriber_id,
            "email": self.email,
            "tier": self.tier.value,
            "monthly_revenue_usd": self.monthly_revenue,
            "onboarding_step": self.onboarding_step,
            "onboarding_complete": self.onboarding_complete,
            "upsell_offers_accepted": self.upsell_offers_accepted,
            "joined_at": self.joined_at,
            "upgraded_at": self.upgraded_at,
        }


@dataclass
class MicroBusiness:
    business_id: str
    name: str
    owner_email: str
    monthly_revenue: float
    revenue_share_pct: float = 0.10  # DreamCo takes 10%
    active: bool = True
    registered_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    @property
    def dreamco_share(self) -> float:
        return round(self.monthly_revenue * self.revenue_share_pct, 2)

    def to_dict(self) -> dict:
        return {
            "business_id": self.business_id,
            "name": self.name,
            "owner_email": self.owner_email,
            "monthly_revenue": self.monthly_revenue,
            "revenue_share_pct": self.revenue_share_pct,
            "dreamco_share": self.dreamco_share,
            "active": self.active,
            "registered_at": self.registered_at,
        }


# ---------------------------------------------------------------------------
# SaaSUpsell
# ---------------------------------------------------------------------------


class SaaSUpsell:
    """
    Manages subscriber onboarding, tier upsells, and micro-business network.

    Usage
    -----
    saas = SaaSUpsell()
    sub  = saas.register_subscriber("user@example.com")
    saas.advance_onboarding(sub.subscriber_id)
    saas.upsell(sub.subscriber_id)
    output = saas.get_revenue_output()
    """

    def __init__(self) -> None:
        self._subscribers: Dict[str, Subscriber] = {}
        self._micro_businesses: Dict[str, MicroBusiness] = {}
        self._upsell_count = 0
        self._upsell_accepted = 0

    # ------------------------------------------------------------------
    # Subscriber management
    # ------------------------------------------------------------------

    def register_subscriber(self, email: str) -> Subscriber:
        """Register a new subscriber and start onboarding."""
        subscriber_id = f"sub_{uuid.uuid4().hex[:8]}"
        subscriber = Subscriber(subscriber_id=subscriber_id, email=email)
        self._subscribers[subscriber_id] = subscriber
        return subscriber

    def advance_onboarding(self, subscriber_id: str) -> dict:
        """Advance the subscriber one step in the onboarding tutorial."""
        sub = self._get_subscriber(subscriber_id)
        if sub.onboarding_complete:
            return {"status": "already_complete", "step": sub.onboarding_step}

        sub.onboarding_step += 1
        if sub.onboarding_step >= len(ONBOARDING_STEPS):
            sub.onboarding_complete = True

        step_name = (
            ONBOARDING_STEPS[sub.onboarding_step - 1]
            if sub.onboarding_step <= len(ONBOARDING_STEPS)
            else "Onboarding complete"
        )
        return {
            "subscriber_id": subscriber_id,
            "step": sub.onboarding_step,
            "step_name": step_name,
            "onboarding_complete": sub.onboarding_complete,
        }

    def complete_onboarding(self, subscriber_id: str) -> dict:
        """Mark subscriber onboarding as complete immediately."""
        sub = self._get_subscriber(subscriber_id)
        sub.onboarding_step = len(ONBOARDING_STEPS)
        sub.onboarding_complete = True
        return {"subscriber_id": subscriber_id, "onboarding_complete": True}

    # ------------------------------------------------------------------
    # Tier upsells
    # ------------------------------------------------------------------

    def upsell(self, subscriber_id: str, accepted: bool = True) -> dict:
        """
        Offer and (if accepted) apply a tier upgrade to the subscriber.

        Returns the next recommended tier and whether the upgrade happened.
        """
        sub = self._get_subscriber(subscriber_id)
        tiers = [t.value for t in SubscriptionTier]
        current_idx = tiers.index(sub.tier.value)
        self._upsell_count += 1

        if current_idx >= len(tiers) - 1:
            return {"subscriber_id": subscriber_id, "status": "already_at_max_tier"}

        next_tier = tiers[current_idx + 1]

        if accepted:
            sub.tier = SubscriptionTier(next_tier)
            sub.upgraded_at = datetime.now(timezone.utc).isoformat()
            sub.upsell_offers_accepted += 1
            self._upsell_accepted += 1
            return {
                "subscriber_id": subscriber_id,
                "new_tier": next_tier,
                "monthly_revenue_usd": sub.monthly_revenue,
                "status": "upgraded",
            }
        else:
            sub.upsell_offers_declined += 1
            return {
                "subscriber_id": subscriber_id,
                "recommended_tier": next_tier,
                "status": "declined",
            }

    # ------------------------------------------------------------------
    # Micro-business network
    # ------------------------------------------------------------------

    def register_micro_business(
        self,
        name: str,
        owner_email: str,
        monthly_revenue: float,
        revenue_share_pct: float = 0.10,
    ) -> MicroBusiness:
        """Register a micro-business in the DreamCo revenue-share network."""
        business_id = f"biz_{uuid.uuid4().hex[:8]}"
        biz = MicroBusiness(
            business_id=business_id,
            name=name,
            owner_email=owner_email,
            monthly_revenue=monthly_revenue,
            revenue_share_pct=revenue_share_pct,
        )
        self._micro_businesses[business_id] = biz
        return biz

    def list_micro_businesses(self) -> List[dict]:
        return [b.to_dict() for b in self._micro_businesses.values() if b.active]

    # ------------------------------------------------------------------
    # Revenue output (standard DreamCo format)
    # ------------------------------------------------------------------

    def get_revenue_output(self) -> dict:
        mrr = sum(s.monthly_revenue for s in self._subscribers.values())
        network_share = sum(
            b.dreamco_share for b in self._micro_businesses.values() if b.active
        )
        total_revenue = round(mrr + network_share, 2)
        new_subs = len([s for s in self._subscribers.values() if s.tier != SubscriptionTier.FREE])
        conversion_rate = (
            round(self._upsell_accepted / self._upsell_count, 4)
            if self._upsell_count
            else 0.0
        )
        return {
            "revenue": total_revenue,
            "leads_generated": new_subs,
            "conversion_rate": conversion_rate,
            "action": f"SaaS subscriptions + micro-business network. MRR=${mrr:.2f}, "
                      f"network_share=${network_share:.2f}",
        }

    # ------------------------------------------------------------------
    # Dashboard metrics
    # ------------------------------------------------------------------

    def get_dashboard_metrics(self) -> dict:
        mrr = sum(s.monthly_revenue for s in self._subscribers.values())
        arr = round(mrr * 12, 2)
        active_subs = len(self._subscribers)
        paid_subs = len(
            [s for s in self._subscribers.values() if s.tier != SubscriptionTier.FREE]
        )
        network_share = round(
            sum(b.dreamco_share for b in self._micro_businesses.values() if b.active), 2
        )
        tier_breakdown = {}
        for tier in SubscriptionTier:
            tier_breakdown[tier.value] = sum(
                1 for s in self._subscribers.values() if s.tier == tier
            )
        return {
            "mrr_usd": round(mrr, 2),
            "arr_usd": arr,
            "total_subscribers": active_subs,
            "paid_subscribers": paid_subs,
            "tier_breakdown": tier_breakdown,
            "micro_business_network_share_usd": network_share,
            "upsell_conversion_rate": (
                round(self._upsell_accepted / self._upsell_count, 4)
                if self._upsell_count
                else 0.0
            ),
        }

    def list_subscribers(self) -> List[dict]:
        return [s.to_dict() for s in self._subscribers.values()]

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _get_subscriber(self, subscriber_id: str) -> Subscriber:
        if subscriber_id not in self._subscribers:
            raise KeyError(f"Subscriber '{subscriber_id}' not found.")
        return self._subscribers[subscriber_id]
