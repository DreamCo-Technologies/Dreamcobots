"""
Tier configuration for the DreamCo Influencer Bot.

Tiers:
  - FREE ($0/month):        Browse influencer catalog, 1 co-branded bot template, basic analytics.
  - PRO ($49/month):        10 co-branded bots, full influencer database, virality engine,
                            campaign manager, audience analytics.
  - ENTERPRISE ($199/month): Unlimited bots, celebrity partnerships, custom co-branding,
                             white-label bots, revenue sharing, API access, dedicated support.
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
    """Configuration for a DreamCo Influencer Bot subscription tier."""

    name: str
    tier: Tier
    price_usd_monthly: float
    max_cobranded_bots: Optional[int]
    features: list
    support_level: str

    def has_feature(self, feature: str) -> bool:
        return feature in self.features

    def is_unlimited_bots(self) -> bool:
        return self.max_cobranded_bots is None


# ---------------------------------------------------------------------------
# Feature flags
# ---------------------------------------------------------------------------

FEATURE_INFLUENCER_CATALOG = "influencer_catalog"
FEATURE_COBRAND_TEMPLATE = "cobrand_template"
FEATURE_BASIC_ANALYTICS = "basic_analytics"
FEATURE_FULL_DATABASE = "full_database"
FEATURE_VIRALITY_ENGINE = "virality_engine"
FEATURE_CAMPAIGN_MANAGER = "campaign_manager"
FEATURE_AUDIENCE_ANALYTICS = "audience_analytics"
FEATURE_CELEBRITY_PARTNERSHIPS = "celebrity_partnerships"
FEATURE_CUSTOM_COBRAND = "custom_cobrand"
FEATURE_WHITE_LABEL = "white_label"
FEATURE_REVENUE_SHARING = "revenue_sharing"
FEATURE_API_ACCESS = "api_access"
FEATURE_DEDICATED_SUPPORT = "dedicated_support"

FREE_FEATURES: list = [
    FEATURE_INFLUENCER_CATALOG,
    FEATURE_COBRAND_TEMPLATE,
    FEATURE_BASIC_ANALYTICS,
]

PRO_FEATURES: list = FREE_FEATURES + [
    FEATURE_FULL_DATABASE,
    FEATURE_VIRALITY_ENGINE,
    FEATURE_CAMPAIGN_MANAGER,
    FEATURE_AUDIENCE_ANALYTICS,
]

ENTERPRISE_FEATURES: list = PRO_FEATURES + [
    FEATURE_CELEBRITY_PARTNERSHIPS,
    FEATURE_CUSTOM_COBRAND,
    FEATURE_WHITE_LABEL,
    FEATURE_REVENUE_SHARING,
    FEATURE_API_ACCESS,
    FEATURE_DEDICATED_SUPPORT,
]

TIER_CATALOGUE: dict = {
    Tier.FREE.value: TierConfig(
        name="Free",
        tier=Tier.FREE,
        price_usd_monthly=0.0,
        max_cobranded_bots=1,
        features=FREE_FEATURES,
        support_level="Community",
    ),
    Tier.PRO.value: TierConfig(
        name="Pro",
        tier=Tier.PRO,
        price_usd_monthly=49.0,
        max_cobranded_bots=10,
        features=PRO_FEATURES,
        support_level="Email (48 h SLA)",
    ),
    Tier.ENTERPRISE.value: TierConfig(
        name="Enterprise",
        tier=Tier.ENTERPRISE,
        price_usd_monthly=199.0,
        max_cobranded_bots=None,
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
