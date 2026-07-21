"""
SaaS Bot — Tiers

Manages SaaS subscription tiers and associated Stripe price IDs.

Tiers:
  - BASIC:      $29/month — core SaaS features, monthly billing.
  - PROFESSIONAL: $99/month — advanced features, annual billing option.
  - ENTERPRISE: $299/month — unlimited, white-label, dedicated support.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class Tier(Enum):
    BASIC = "basic"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"


@dataclass
class TierConfig:
    """Configuration for a SaaS Bot subscription tier."""

    name: str
    tier: Tier
    price_usd_monthly: float
    stripe_monthly_price_id: str
    stripe_annual_price_id: str
    max_users: Optional[int]
    features: list
    support_level: str

    def is_unlimited_users(self) -> bool:
        return self.max_users is None

    def has_feature(self, feature: str) -> bool:
        return feature in self.features


# ---------------------------------------------------------------------------
# Feature flags
# ---------------------------------------------------------------------------

FEATURE_CORE_SAAS = "core_saas"
FEATURE_STRIPE_SUBSCRIPTIONS = "stripe_subscriptions"
FEATURE_SUBSCRIPTION_WEBHOOKS = "subscription_webhooks"
FEATURE_ANNUAL_BILLING = "annual_billing"
FEATURE_TRIAL_PERIOD = "trial_period"
FEATURE_USAGE_ANALYTICS = "usage_analytics"
FEATURE_MULTI_USER = "multi_user"
FEATURE_WHITE_LABEL = "white_label"
FEATURE_CUSTOM_DOMAIN = "custom_domain"
FEATURE_PRIORITY_SUPPORT = "priority_support"

BASIC_FEATURES = [
    FEATURE_CORE_SAAS,
    FEATURE_STRIPE_SUBSCRIPTIONS,
    FEATURE_TRIAL_PERIOD,
]

PROFESSIONAL_FEATURES = BASIC_FEATURES + [
    FEATURE_SUBSCRIPTION_WEBHOOKS,
    FEATURE_ANNUAL_BILLING,
    FEATURE_USAGE_ANALYTICS,
    FEATURE_MULTI_USER,
    FEATURE_PRIORITY_SUPPORT,
]

ENTERPRISE_FEATURES = PROFESSIONAL_FEATURES + [
    FEATURE_WHITE_LABEL,
    FEATURE_CUSTOM_DOMAIN,
]

# ---------------------------------------------------------------------------
# Tier catalogue
# ---------------------------------------------------------------------------

TIER_CATALOGUE: dict[str, TierConfig] = {
    Tier.BASIC.value: TierConfig(
        name="Basic",
        tier=Tier.BASIC,
        price_usd_monthly=29.0,
        # Replace with real Stripe Price IDs from Dashboard > Products > Prices
        stripe_monthly_price_id="price_basic_monthly_placeholder",
        stripe_annual_price_id="price_basic_annual_placeholder",
        max_users=5,
        features=BASIC_FEATURES,
        support_level="Community",
    ),
    Tier.PROFESSIONAL.value: TierConfig(
        name="Professional",
        tier=Tier.PROFESSIONAL,
        price_usd_monthly=99.0,
        # Replace with real Stripe Price IDs from Dashboard > Products > Prices
        stripe_monthly_price_id="price_professional_monthly_placeholder",
        stripe_annual_price_id="price_professional_annual_placeholder",
        max_users=25,
        features=PROFESSIONAL_FEATURES,
        support_level="Email (24 h SLA)",
    ),
    Tier.ENTERPRISE.value: TierConfig(
        name="Enterprise",
        tier=Tier.ENTERPRISE,
        price_usd_monthly=299.0,
        # Replace with real Stripe Price IDs from Dashboard > Products > Prices
        stripe_monthly_price_id="price_enterprise_monthly_placeholder",
        stripe_annual_price_id="price_enterprise_annual_placeholder",
        max_users=None,
        features=ENTERPRISE_FEATURES,
        support_level="Dedicated 24/7",
    ),
}


def get_tier_config(tier: Tier) -> TierConfig:
    return TIER_CATALOGUE[tier.value]


def list_tiers() -> list[TierConfig]:
    return [TIER_CATALOGUE[t.value] for t in Tier]


def get_upgrade_path(current: Tier) -> Optional[TierConfig]:
    order = list(Tier)
    idx = order.index(current)
    if idx + 1 < len(order):
        return get_tier_config(order[idx + 1])
    return None
