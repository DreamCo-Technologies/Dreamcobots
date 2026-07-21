"""
3-Tier Pricing and Membership System for Dreamcobots platform.

Implements Free, Premium, and Elite tiers with flexible weekly, monthly,
and yearly billing cycles.
"""

import uuid
from dataclasses import dataclass, field
from datetime import date, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional


class MembershipTier(Enum):
    """Three-tier membership hierarchy."""
    FREE = "free"
    PREMIUM = "premium"
    ELITE = "elite"


class BillingCycle(Enum):
    """Supported billing cadences."""
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    YEARLY = "yearly"


# Base monthly prices (USD) per tier
_BASE_MONTHLY_PRICES: Dict[MembershipTier, float] = {
    MembershipTier.FREE: 0.00,
    MembershipTier.PREMIUM: 29.99,
    MembershipTier.ELITE: 99.99,
}

# Discount multipliers per billing cycle (applied to the monthly base)
_CYCLE_MULTIPLIERS: Dict[BillingCycle, float] = {
    BillingCycle.WEEKLY: 0.30,    # approx weekly fraction (monthly * 0.30)
    BillingCycle.MONTHLY: 1.00,
    BillingCycle.YEARLY: 10.00,   # two months free on annual plan
}

# Feature sets per tier
_TIER_FEATURES: Dict[MembershipTier, List[str]] = {
    MembershipTier.FREE: [
        "Basic bot services",
        "Free versions of top 100 AI tools/service APIs",
        "Community support",
    ],
    MembershipTier.PREMIUM: [
        "Advanced bot functionalities",
        "Premium versions of AI tools",
        "Priority email support",
        "Sandbox testing (standard)",
        "Bot marketplace access",
    ],
    MembershipTier.ELITE: [
        "Unlimited access to all bots and tools",
        "Enterprise-grade tools",
        "Priority certifications",
        "Niche custom applications",
        "Dedicated account manager",
        "Sandbox testing (military-grade)",
        "Bot marketplace – buy and sell",
        "White-label deployment",
    ],
}


@dataclass
class MembershipPlan:
    """
    Represents a concrete membership plan combining tier and billing cycle.

    Args:
        tier: The membership tier.
        billing_cycle: How often the member is billed.
    """
    tier: MembershipTier
    billing_cycle: BillingCycle

    @property
    def price(self) -> float:
        """Return the price for one billing period in USD."""
        base = _BASE_MONTHLY_PRICES[self.tier]
        return round(base * _CYCLE_MULTIPLIERS[self.billing_cycle], 2)

    @property
    def features(self) -> List[str]:
        """Return the feature list for this tier."""
        return list(_TIER_FEATURES[self.tier])

    @property
    def period_days(self) -> int:
        """Number of calendar days per billing period."""
        return {
            BillingCycle.WEEKLY: 7,
            BillingCycle.MONTHLY: 30,
            BillingCycle.YEARLY: 365,
        }[self.billing_cycle]

    def describe(self) -> str:
        """Return a human-readable plan description."""
        return (
            f"{self.tier.value.capitalize()} / {self.billing_cycle.value.capitalize()} "
            f"– ${self.price:.2f} per {self.billing_cycle.value}"
        )


@dataclass
class Subscription:
    """Active subscription record for a member."""
    member_id: str
    plan: MembershipPlan
    start_date: date = field(default_factory=date.today)
    subscription_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    active: bool = True

    @property
    def end_date(self) -> date:
        """Return the current period end date."""
        return self.start_date + timedelta(days=self.plan.period_days)

    def is_valid_on(self, check_date: Optional[date] = None) -> bool:
        """Return True if the subscription is active on *check_date* (default today)."""
        check_date = check_date or date.today()
        return self.active and self.start_date <= check_date <= self.end_date


class MembershipManager:
    """
    Manages member subscriptions across all tiers and billing cycles.

    Usage::

        manager = MembershipManager()
        sub = manager.subscribe("user-123", MembershipTier.PREMIUM, BillingCycle.MONTHLY)
        manager.has_feature("user-123", "Sandbox testing (standard)")  # True
    """

    def __init__(self) -> None:
        self._subscriptions: Dict[str, Subscription] = {}  # member_id → Subscription

    # ------------------------------------------------------------------
    # Subscription management
    # ------------------------------------------------------------------

    def subscribe(
        self,
        member_id: str,
        tier: MembershipTier,
        billing_cycle: BillingCycle,
    ) -> Subscription:
        """
        Create or replace the subscription for *member_id*.

        Args:
            member_id: Unique identifier for the member.
            tier: Desired membership tier.
            billing_cycle: Billing frequency.

        Returns:
            The new Subscription record.
        """
        plan = MembershipPlan(tier=tier, billing_cycle=billing_cycle)
        sub = Subscription(member_id=member_id, plan=plan)
        self._subscriptions[member_id] = sub
        return sub

    def cancel(self, member_id: str) -> bool:
        """Cancel the active subscription for *member_id*. Returns True if found."""
        sub = self._subscriptions.get(member_id)
        if sub and sub.active:
            sub.active = False
            return True
        return False

    def get_subscription(self, member_id: str) -> Optional[Subscription]:
        """Return the subscription for *member_id*, or None."""
        return self._subscriptions.get(member_id)

    def upgrade(self, member_id: str, new_tier: MembershipTier) -> Optional[Subscription]:
        """
        Upgrade a member to *new_tier* while retaining their billing cycle.

        Returns the updated Subscription, or None if no subscription exists.
        """
        existing = self._subscriptions.get(member_id)
        if not existing:
            return None
        return self.subscribe(member_id, new_tier, existing.plan.billing_cycle)

    # ------------------------------------------------------------------
    # Feature gating
    # ------------------------------------------------------------------

    def has_feature(self, member_id: str, feature: str) -> bool:
        """
        Return True if *member_id* has access to *feature* today.

        Args:
            member_id: Member to check.
            feature: Feature string (must match exactly one from _TIER_FEATURES).
        """
        sub = self._subscriptions.get(member_id)
        if not sub or not sub.is_valid_on():
            return False
        return feature in sub.plan.features

    # ------------------------------------------------------------------
    # Reporting
    # ------------------------------------------------------------------

    def list_plans(self) -> List[Dict[str, Any]]:
        """Return all available plan configurations as a list of dicts."""
        plans = []
        for tier in MembershipTier:
            for cycle in BillingCycle:
                plan = MembershipPlan(tier=tier, billing_cycle=cycle)
                plans.append({
                    "tier": tier.value,
                    "billing_cycle": cycle.value,
                    "price_usd": plan.price,
                    "features": plan.features,
                    "description": plan.describe(),
                })
        return plans

    def active_subscribers(self) -> List[Subscription]:
        """Return all currently active subscriptions."""
        today = date.today()
        return [s for s in self._subscriptions.values() if s.is_valid_on(today)]
