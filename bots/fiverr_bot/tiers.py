"""
Tier configuration for the Fiverr Automation Bot.

Tiers:
  - FREE:       5 gig listings, basic order tracking, manual delivery.
                Service fee: 20% per transaction.
  - PRO ($49):  50 gig listings, auto order management, analytics, inbox
                automation, freelancer/client matching, job postings,
                proposal submissions, Stripe payments, milestones.
                Service fee: 10% per transaction.
  - ENTERPRISE ($199): Unlimited gigs, AI-optimized pricing, white-label,
                CRM export, admin dashboard, featured gig placement.
                Service fee: 5% per transaction.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class Tier(Enum):
    FREE = "free"
    PRO = "pro"
    ENTERPRISE = "enterprise"


@dataclass
class TierConfig:
    name: str
    tier: Tier
    price_usd_monthly: float
    max_gigs: Optional[int]
    max_orders_per_month: Optional[int]
    features: list
    support_level: str
    service_fee_pct: float  # percentage charged per completed transaction

    def has_feature(self, feature: str) -> bool:
        return feature in self.features

    def is_unlimited_gigs(self) -> bool:
        return self.max_gigs is None


FEATURE_GIG_LISTING = "gig_listing"
FEATURE_ORDER_TRACKING = "order_tracking"
FEATURE_INBOX_AUTOMATION = "inbox_automation"
FEATURE_REVIEW_COLLECTION = "review_collection"
FEATURE_ANALYTICS = "analytics"
FEATURE_PRICING_OPTIMIZER = "pricing_optimizer"
FEATURE_CRM_EXPORT = "crm_export"
FEATURE_AI_PRICING = "ai_pricing"
FEATURE_WHITE_LABEL = "white_label"
FEATURE_BULK_MESSAGING = "bulk_messaging"
# New features
FEATURE_FREELANCER_MATCHING = "freelancer_matching"
FEATURE_JOB_POSTINGS = "job_postings"
FEATURE_PROPOSALS = "proposals"
FEATURE_STRIPE_PAYMENTS = "stripe_payments"
FEATURE_MILESTONES = "milestones"
FEATURE_ADMIN_DASHBOARD = "admin_dashboard"
FEATURE_FEATURED_GIGS = "featured_gigs"

FREE_FEATURES = [
    FEATURE_GIG_LISTING,
    FEATURE_ORDER_TRACKING,
]

PRO_FEATURES = FREE_FEATURES + [
    FEATURE_INBOX_AUTOMATION,
    FEATURE_REVIEW_COLLECTION,
    FEATURE_ANALYTICS,
    FEATURE_PRICING_OPTIMIZER,
    FEATURE_BULK_MESSAGING,
    FEATURE_FREELANCER_MATCHING,
    FEATURE_JOB_POSTINGS,
    FEATURE_PROPOSALS,
    FEATURE_STRIPE_PAYMENTS,
    FEATURE_MILESTONES,
]

ENTERPRISE_FEATURES = PRO_FEATURES + [
    FEATURE_CRM_EXPORT,
    FEATURE_AI_PRICING,
    FEATURE_WHITE_LABEL,
    FEATURE_ADMIN_DASHBOARD,
    FEATURE_FEATURED_GIGS,
]

TIER_CATALOGUE = {
    Tier.FREE.value: TierConfig(
        name="Free",
        tier=Tier.FREE,
        price_usd_monthly=0.0,
        max_gigs=5,
        max_orders_per_month=20,
        features=FREE_FEATURES,
        support_level="Community",
        service_fee_pct=20.0,
    ),
    Tier.PRO.value: TierConfig(
        name="Pro",
        tier=Tier.PRO,
        price_usd_monthly=49.0,
        max_gigs=50,
        max_orders_per_month=500,
        features=PRO_FEATURES,
        support_level="Email (24 h SLA)",
        service_fee_pct=10.0,
    ),
    Tier.ENTERPRISE.value: TierConfig(
        name="Enterprise",
        tier=Tier.ENTERPRISE,
        price_usd_monthly=199.0,
        max_gigs=None,
        max_orders_per_month=None,
        features=ENTERPRISE_FEATURES,
        support_level="Dedicated 24/7",
        service_fee_pct=5.0,
    ),
}


def get_tier_config(tier: Tier) -> TierConfig:
    return TIER_CATALOGUE[tier.value]


def list_tiers() -> list:
    return [TIER_CATALOGUE[t.value] for t in Tier]


def get_upgrade_path(current: Tier) -> Optional[TierConfig]:
    order = list(Tier)
    idx = order.index(current)
    if idx + 1 < len(order):
        return get_tier_config(order[idx + 1])
    return None
