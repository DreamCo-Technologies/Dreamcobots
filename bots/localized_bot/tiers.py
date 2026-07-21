"""
Tier configuration for the DreamCo Localized Bot.

Tiers:
  - FREE ($0/month):        3 regions, basic translation, community leaderboard view.
  - PRO ($49/month):        25 regions, full translations, industry adaption, vote on bots,
                            regional challenges.
  - ENTERPRISE ($199/month): All regions, custom locale support, private regional bots,
                             API access, analytics, white-label.
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
    """Configuration for a DreamCo Localized Bot subscription tier."""

    name: str
    tier: Tier
    price_usd_monthly: float
    max_regions: Optional[int]
    features: list
    support_level: str

    def has_feature(self, feature: str) -> bool:
        return feature in self.features

    def is_unlimited_regions(self) -> bool:
        return self.max_regions is None


# ---------------------------------------------------------------------------
# Feature flags
# ---------------------------------------------------------------------------

FEATURE_BASIC_TRANSLATION = "basic_translation"
FEATURE_FULL_TRANSLATION = "full_translation"
FEATURE_INDUSTRY_ADAPTION = "industry_adaption"
FEATURE_REGIONAL_CHALLENGES = "regional_challenges"
FEATURE_GLOBAL_LEADERBOARD_VOTE = "global_leaderboard_vote"
FEATURE_CUSTOM_LOCALE = "custom_locale"
FEATURE_PRIVATE_REGIONAL_BOTS = "private_regional_bots"
FEATURE_API_ACCESS = "api_access"
FEATURE_ANALYTICS = "analytics"
FEATURE_WHITE_LABEL = "white_label"

FREE_FEATURES: list = [
    FEATURE_BASIC_TRANSLATION,
]

PRO_FEATURES: list = FREE_FEATURES + [
    FEATURE_FULL_TRANSLATION,
    FEATURE_INDUSTRY_ADAPTION,
    FEATURE_GLOBAL_LEADERBOARD_VOTE,
    FEATURE_REGIONAL_CHALLENGES,
]

ENTERPRISE_FEATURES: list = PRO_FEATURES + [
    FEATURE_CUSTOM_LOCALE,
    FEATURE_PRIVATE_REGIONAL_BOTS,
    FEATURE_API_ACCESS,
    FEATURE_ANALYTICS,
    FEATURE_WHITE_LABEL,
]

TIER_CATALOGUE: dict = {
    Tier.FREE.value: TierConfig(
        name="Free",
        tier=Tier.FREE,
        price_usd_monthly=0.0,
        max_regions=3,
        features=FREE_FEATURES,
        support_level="Community",
    ),
    Tier.PRO.value: TierConfig(
        name="Pro",
        tier=Tier.PRO,
        price_usd_monthly=49.0,
        max_regions=25,
        features=PRO_FEATURES,
        support_level="Email (48 h SLA)",
    ),
    Tier.ENTERPRISE.value: TierConfig(
        name="Enterprise",
        tier=Tier.ENTERPRISE,
        price_usd_monthly=199.0,
        max_regions=None,
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
