"""
Tier configuration for the Wealth System Bot.

Tiers:
  - FREE:              Basic wealth hubs (3 max), treasury management,
                       community governance read-only, basic analytics.
  - PRO ($49):         Unlimited hubs, advanced features, dividend engine,
                       KYC/AML compliance, asset allocation, DreamCoin,
                       income/asset bots, referral system, Stripe billing.
  - ENTERPRISE ($199): All pro features + trading bots, white-label,
                       full analytics, priority support.
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
    max_hubs: Optional[int]
    max_members_per_hub: Optional[int]
    features: list
    support_level: str

    def has_feature(self, feature: str) -> bool:
        return feature in self.features

    def is_unlimited_hubs(self) -> bool:
        return self.max_hubs is None


# ---------------------------------------------------------------------------
# Feature flags
# ---------------------------------------------------------------------------

FEATURE_WEALTH_HUBS = "wealth_hubs"
FEATURE_TREASURY_MANAGEMENT = "treasury_management"
FEATURE_GOVERNANCE_VOTING = "governance_voting"
FEATURE_DIVIDEND_ENGINE = "dividend_engine"
FEATURE_ASSET_ALLOCATION = "asset_allocation"
FEATURE_DREAMCOIN = "dreamcoin"
FEATURE_KYC_COMPLIANCE = "kyc_compliance"
FEATURE_AML_COMPLIANCE = "aml_compliance"
FEATURE_GLOBAL_REGISTRY = "global_registry"
FEATURE_MULTI_LANGUAGE = "multi_language"
FEATURE_MULTI_CURRENCY = "multi_currency"
FEATURE_INCOME_BOTS = "income_bots"
FEATURE_ASSET_BOTS = "asset_bots"
FEATURE_TRADING_BOTS = "trading_bots"
FEATURE_ANALYTICS = "analytics"
FEATURE_WHITE_LABEL = "white_label"
FEATURE_STRIPE_BILLING = "stripe_billing"
FEATURE_REFERRAL_SYSTEM = "referral_system"
FEATURE_MARKETPLACE = "marketplace"

FREE_FEATURES = [
    FEATURE_WEALTH_HUBS,
    FEATURE_TREASURY_MANAGEMENT,
    FEATURE_GLOBAL_REGISTRY,
    FEATURE_MULTI_LANGUAGE,
    FEATURE_MULTI_CURRENCY,
]

PRO_FEATURES = FREE_FEATURES + [
    FEATURE_GOVERNANCE_VOTING,
    FEATURE_DIVIDEND_ENGINE,
    FEATURE_ASSET_ALLOCATION,
    FEATURE_DREAMCOIN,
    FEATURE_KYC_COMPLIANCE,
    FEATURE_AML_COMPLIANCE,
    FEATURE_INCOME_BOTS,
    FEATURE_ASSET_BOTS,
    FEATURE_REFERRAL_SYSTEM,
    FEATURE_STRIPE_BILLING,
    FEATURE_MARKETPLACE,
]

ENTERPRISE_FEATURES = PRO_FEATURES + [
    FEATURE_TRADING_BOTS,
    FEATURE_ANALYTICS,
    FEATURE_WHITE_LABEL,
]

TIER_CATALOGUE = {
    Tier.FREE.value: TierConfig(
        name="Free",
        tier=Tier.FREE,
        price_usd_monthly=0.0,
        max_hubs=3,
        max_members_per_hub=10,
        features=FREE_FEATURES,
        support_level="Community",
    ),
    Tier.PRO.value: TierConfig(
        name="Pro",
        tier=Tier.PRO,
        price_usd_monthly=49.0,
        max_hubs=None,
        max_members_per_hub=100,
        features=PRO_FEATURES,
        support_level="Email (24 h SLA)",
    ),
    Tier.ENTERPRISE.value: TierConfig(
        name="Enterprise",
        tier=Tier.ENTERPRISE,
        price_usd_monthly=199.0,
        max_hubs=None,
        max_members_per_hub=None,
        features=ENTERPRISE_FEATURES,
        support_level="Dedicated 24/7",
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
