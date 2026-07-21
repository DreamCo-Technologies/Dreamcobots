"""
Tier configuration for the DreamCo Stripe Payment Bot.

Tiers:
  - STARTER:    Basic Stripe checkout, 500 payments/month, $29/mo.
  - GROWTH:     Subscriptions + webhooks, 10 000 payments/month, $99/mo.
  - ENTERPRISE: Unlimited, Connect platform, split payments, $299/mo.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class Tier(Enum):
    STARTER = "starter"
    GROWTH = "growth"
    ENTERPRISE = "enterprise"


# ---------------------------------------------------------------------------
# Feature flags
# ---------------------------------------------------------------------------

FEATURE_CHECKOUT = "checkout"
FEATURE_SUBSCRIPTIONS = "subscriptions"
FEATURE_WEBHOOKS = "webhooks"
FEATURE_REFUNDS = "refunds"
FEATURE_COUPONS = "coupons"
FEATURE_INVOICES = "invoices"
FEATURE_CONNECT = "connect"
FEATURE_SPLIT_PAYMENTS = "split_payments"
FEATURE_ANALYTICS = "analytics"
FEATURE_FRAUD_RADAR = "fraud_radar"
FEATURE_WHITE_LABEL = "white_label"
FEATURE_SLA = "sla_guarantee"

STARTER_FEATURES = [
    FEATURE_CHECKOUT,
    FEATURE_REFUNDS,
]

GROWTH_FEATURES = STARTER_FEATURES + [
    FEATURE_SUBSCRIPTIONS,
    FEATURE_WEBHOOKS,
    FEATURE_COUPONS,
    FEATURE_INVOICES,
    FEATURE_ANALYTICS,
]

ENTERPRISE_FEATURES = GROWTH_FEATURES + [
    FEATURE_CONNECT,
    FEATURE_SPLIT_PAYMENTS,
    FEATURE_FRAUD_RADAR,
    FEATURE_WHITE_LABEL,
    FEATURE_SLA,
]


@dataclass
class TierConfig:
    """Configuration for a Stripe Payment Bot subscription tier."""

    name: str
    tier: Tier
    price_usd_monthly: float
    payments_per_month: Optional[int]
    features: list = field(default_factory=list)
    support_level: str = "Community"
    platform_fee_pct: float = 2.9  # Stripe default

    def has_feature(self, feature: str) -> bool:
        return feature in self.features

    def is_unlimited(self) -> bool:
        return self.payments_per_month is None


TIER_CATALOGUE: dict[str, TierConfig] = {
    Tier.STARTER.value: TierConfig(
        name="Starter",
        tier=Tier.STARTER,
        price_usd_monthly=29.0,
        payments_per_month=500,
        features=STARTER_FEATURES,
        support_level="Community",
        platform_fee_pct=2.9,
    ),
    Tier.GROWTH.value: TierConfig(
        name="Growth",
        tier=Tier.GROWTH,
        price_usd_monthly=99.0,
        payments_per_month=10_000,
        features=GROWTH_FEATURES,
        support_level="Email (24 h SLA)",
        platform_fee_pct=2.5,
    ),
    Tier.ENTERPRISE.value: TierConfig(
        name="Enterprise",
        tier=Tier.ENTERPRISE,
        price_usd_monthly=299.0,
        payments_per_month=None,
        features=ENTERPRISE_FEATURES,
        support_level="Dedicated 24/7",
        platform_fee_pct=2.2,
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
