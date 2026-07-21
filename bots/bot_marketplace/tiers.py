"""
Tier configuration for the DreamCo Bot Marketplace.

Tiers:
  - FREE ($0/month):        Browse marketplace, buy up to 3 bots, 1 listing, basic search.
  - PRO ($49/month):        Buy unlimited bots, 10 listings, monetize bots, upsell skills,
                            detailed analytics, 15% platform fee.
  - ENTERPRISE ($199/month): Unlimited listings, custom storefronts, Fortune 500 integrations,
                             white-label marketplace, API access, 10% platform fee,
                             dedicated support.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class Tier(Enum):
    FREE = "free"
    PRO = "pro"
    ENTERPRISE = "enterprise"


# ---------------------------------------------------------------------------
# Feature flags
# ---------------------------------------------------------------------------

FEATURE_BROWSE = "browse"
FEATURE_BUY_BOTS = "buy_bots"
FEATURE_SELL_BOTS = "sell_bots"
FEATURE_MONETIZE = "monetize"
FEATURE_UPSELL = "upsell"
FEATURE_ANALYTICS = "analytics"
FEATURE_CUSTOM_STOREFRONT = "custom_storefront"
FEATURE_FORTUNE500_INTEGRATION = "fortune500_integration"
FEATURE_WHITE_LABEL = "white_label"
FEATURE_API_ACCESS = "api_access"
FEATURE_DEDICATED_SUPPORT = "dedicated_support"

FREE_FEATURES: list = [
    FEATURE_BROWSE,
    FEATURE_BUY_BOTS,
    FEATURE_SELL_BOTS,
]

PRO_FEATURES: list = FREE_FEATURES + [
    FEATURE_MONETIZE,
    FEATURE_UPSELL,
    FEATURE_ANALYTICS,
]

ENTERPRISE_FEATURES: list = PRO_FEATURES + [
    FEATURE_CUSTOM_STOREFRONT,
    FEATURE_FORTUNE500_INTEGRATION,
    FEATURE_WHITE_LABEL,
    FEATURE_API_ACCESS,
    FEATURE_DEDICATED_SUPPORT,
]


@dataclass
class TierConfig:
    """Configuration for a DreamCo Bot Marketplace subscription tier."""

    name: str
    tier: Tier
    price_usd_monthly: float
    max_listings: Optional[int]
    max_purchases: Optional[int]
    platform_fee_pct: float
    features: list
    support_level: str

    def has_feature(self, feature: str) -> bool:
        return feature in self.features

    def is_unlimited_listings(self) -> bool:
        return self.max_listings is None

    def is_unlimited_purchases(self) -> bool:
        return self.max_purchases is None


TIER_CATALOGUE: dict = {
    Tier.FREE.value: TierConfig(
        name="Free",
        tier=Tier.FREE,
        price_usd_monthly=0.0,
        max_listings=1,
        max_purchases=3,
        platform_fee_pct=0.20,
        features=FREE_FEATURES,
        support_level="Community",
    ),
    Tier.PRO.value: TierConfig(
        name="Pro",
        tier=Tier.PRO,
        price_usd_monthly=49.0,
        max_listings=10,
        max_purchases=None,
        platform_fee_pct=0.15,
        features=PRO_FEATURES,
        support_level="Email (48 h SLA)",
    ),
    Tier.ENTERPRISE.value: TierConfig(
        name="Enterprise",
        tier=Tier.ENTERPRISE,
        price_usd_monthly=199.0,
        max_listings=None,
        max_purchases=None,
        platform_fee_pct=0.10,
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
