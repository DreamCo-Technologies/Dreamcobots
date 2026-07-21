"""
Tier configuration for the DreamCo Bot Wars Bot.

Tiers:
  - FREE ($0/month):        Basic competitions (view only), 1 bot submission, community leaderboard.
  - PRO ($49/month):        Join all competitions, 10 bot submissions, category leaderboards,
                            drag-drop builder, score analytics.
  - ENTERPRISE ($199/month): Unlimited submissions, white-label competitions, host private
                             tournaments, custom categories, API access, dedicated support.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class Tier(Enum):
    FREE = "free"
    PRO = "pro"
    ENTERPRISE = "enterprise"


@dataclass
class TierConfig:
    """Configuration for a DreamCo Bot Wars Bot subscription tier."""

    name: str
    tier: Tier
    price_usd_monthly: float
    max_bot_submissions: Optional[int]
    features: list
    support_level: str

    def has_feature(self, feature: str) -> bool:
        return feature in self.features

    def is_unlimited_submissions(self) -> bool:
        return self.max_bot_submissions is None


# ---------------------------------------------------------------------------
# Feature flags
# ---------------------------------------------------------------------------

FEATURE_VIEW_COMPETITIONS = "view_competitions"
FEATURE_COMMUNITY_LEADERBOARD = "community_leaderboard"
FEATURE_JOIN_COMPETITIONS = "join_competitions"
FEATURE_CATEGORY_LEADERBOARDS = "category_leaderboards"
FEATURE_DRAG_DROP_BUILDER = "drag_drop_builder"
FEATURE_SCORE_ANALYTICS = "score_analytics"
FEATURE_WHITE_LABEL = "white_label"
FEATURE_HOST_PRIVATE_TOURNAMENTS = "host_private_tournaments"
FEATURE_CUSTOM_CATEGORIES = "custom_categories"
FEATURE_API_ACCESS = "api_access"
FEATURE_DEDICATED_SUPPORT = "dedicated_support"

FREE_FEATURES: list = [
    FEATURE_VIEW_COMPETITIONS,
    FEATURE_COMMUNITY_LEADERBOARD,
]

PRO_FEATURES: list = FREE_FEATURES + [
    FEATURE_JOIN_COMPETITIONS,
    FEATURE_CATEGORY_LEADERBOARDS,
    FEATURE_DRAG_DROP_BUILDER,
    FEATURE_SCORE_ANALYTICS,
]

ENTERPRISE_FEATURES: list = PRO_FEATURES + [
    FEATURE_WHITE_LABEL,
    FEATURE_HOST_PRIVATE_TOURNAMENTS,
    FEATURE_CUSTOM_CATEGORIES,
    FEATURE_API_ACCESS,
    FEATURE_DEDICATED_SUPPORT,
]

TIER_CATALOGUE: dict = {
    Tier.FREE.value: TierConfig(
        name="Free",
        tier=Tier.FREE,
        price_usd_monthly=0.0,
        max_bot_submissions=1,
        features=FREE_FEATURES,
        support_level="Community",
    ),
    Tier.PRO.value: TierConfig(
        name="Pro",
        tier=Tier.PRO,
        price_usd_monthly=49.0,
        max_bot_submissions=10,
        features=PRO_FEATURES,
        support_level="Email (48 h SLA)",
    ),
    Tier.ENTERPRISE.value: TierConfig(
        name="Enterprise",
        tier=Tier.ENTERPRISE,
        price_usd_monthly=199.0,
        max_bot_submissions=None,
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
