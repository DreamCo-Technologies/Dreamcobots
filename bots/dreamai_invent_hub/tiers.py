"""
Tier configuration for the DreamAIInvent Hub.

Tiers:
  - FREE ($0):         Browse marketplace, basic matchmaking, 3 toolkit sessions/month.
  - PRO ($49):         Full matchmaking, unlimited toolkit, forums, licensing templates.
  - ENTERPRISE ($199): White-label, API access, dedicated IP & patent advisor, IoT lab.
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
    """Configuration for a DreamAIInvent Hub subscription tier."""

    name: str
    tier: Tier
    price_usd_monthly: float
    max_matches_per_month: Optional[int]
    max_toolkit_sessions_per_month: Optional[int]
    max_marketplace_listings: Optional[int]
    features: list
    support_level: str

    def has_feature(self, feature: str) -> bool:
        return feature in self.features

    def is_unlimited_matches(self) -> bool:
        return self.max_matches_per_month is None


# ---------------------------------------------------------------------------
# Feature flags
# ---------------------------------------------------------------------------

FEATURE_MARKETPLACE_BROWSE = "marketplace_browse"
FEATURE_BASIC_MATCHMAKING = "basic_matchmaking"
FEATURE_ADVANCED_MATCHMAKING = "advanced_matchmaking"
FEATURE_LICENSING_TEMPLATES = "licensing_templates"
FEATURE_REVENUE_SHARING = "revenue_sharing"
FEATURE_IOT_MATCHMAKING = "iot_matchmaking"
FEATURE_INVENTOR_TOOLKIT = "inventor_toolkit"
FEATURE_DESIGN_BOT = "design_bot"
FEATURE_FINANCIAL_PROJECTION = "financial_projection"
FEATURE_MANUFACTURING_SIMULATOR = "manufacturing_simulator"
FEATURE_PATENT_SUPPORT = "patent_support"
FEATURE_FORUMS = "forums"
FEATURE_PROTOTYPING_LAB = "prototyping_lab"
FEATURE_MARKETPLACE_LISTING = "marketplace_listing"
FEATURE_ELECTRONICS_DIRECTORY = "electronics_directory"
FEATURE_API_ACCESS = "api_access"
FEATURE_WHITE_LABEL = "white_label"
FEATURE_DEDICATED_SUPPORT = "dedicated_support"
FEATURE_IOT_LAB = "iot_lab"
FEATURE_PARTNERSHIP_ANALYTICS = "partnership_analytics"

FREE_FEATURES: list = [
    FEATURE_MARKETPLACE_BROWSE,
    FEATURE_BASIC_MATCHMAKING,
    FEATURE_INVENTOR_TOOLKIT,
    FEATURE_DESIGN_BOT,
    FEATURE_ELECTRONICS_DIRECTORY,
]

PRO_FEATURES: list = FREE_FEATURES + [
    FEATURE_ADVANCED_MATCHMAKING,
    FEATURE_LICENSING_TEMPLATES,
    FEATURE_REVENUE_SHARING,
    FEATURE_IOT_MATCHMAKING,
    FEATURE_FINANCIAL_PROJECTION,
    FEATURE_MANUFACTURING_SIMULATOR,
    FEATURE_PATENT_SUPPORT,
    FEATURE_FORUMS,
    FEATURE_PROTOTYPING_LAB,
    FEATURE_MARKETPLACE_LISTING,
    FEATURE_PARTNERSHIP_ANALYTICS,
]

ENTERPRISE_FEATURES: list = PRO_FEATURES + [
    FEATURE_API_ACCESS,
    FEATURE_WHITE_LABEL,
    FEATURE_DEDICATED_SUPPORT,
    FEATURE_IOT_LAB,
]

TIER_CATALOGUE: dict = {
    Tier.FREE.value: TierConfig(
        name="Free",
        tier=Tier.FREE,
        price_usd_monthly=0.0,
        max_matches_per_month=5,
        max_toolkit_sessions_per_month=3,
        max_marketplace_listings=0,
        features=FREE_FEATURES,
        support_level="Community",
    ),
    Tier.PRO.value: TierConfig(
        name="Pro",
        tier=Tier.PRO,
        price_usd_monthly=49.0,
        max_matches_per_month=100,
        max_toolkit_sessions_per_month=None,
        max_marketplace_listings=20,
        features=PRO_FEATURES,
        support_level="Email (24 h SLA)",
    ),
    Tier.ENTERPRISE.value: TierConfig(
        name="Enterprise",
        tier=Tier.ENTERPRISE,
        price_usd_monthly=199.0,
        max_matches_per_month=None,
        max_toolkit_sessions_per_month=None,
        max_marketplace_listings=None,
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
