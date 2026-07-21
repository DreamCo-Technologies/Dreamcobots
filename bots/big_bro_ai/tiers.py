"""
Tier configuration for the Big Bro AI Bot.

Tiers:
  - FREE:       Core mentor access, basic memory, 1 bot via Bot Factory.
  - PRO:        Full mentor suite, extended memory, 10 bots, 20 AI models.
  - ENTERPRISE: Unlimited bots, franchise engine, catalog, all AI models,
                priority support, white-label.
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
    """Configuration for a Big Bro AI subscription tier.

    Attributes
    ----------
    name : str
        Human-readable tier name.
    tier : Tier
        Enum value identifying the tier.
    price_usd_monthly : float
        Monthly subscription price in USD.
    max_bots : int | None
        Maximum bots the user can create via Bot Factory.  None = unlimited.
    max_memory_profiles : int | None
        Maximum user memory profiles stored.  None = unlimited.
    max_ai_models : int
        Number of AI models accessible via the 20-model suite.
    features : list[str]
        Feature flags enabled on this tier.
    support_level : str
        Description of the support offering.
    """

    name: str
    tier: Tier
    price_usd_monthly: float
    max_bots: Optional[int]
    max_memory_profiles: Optional[int]
    max_ai_models: int
    features: list
    support_level: str

    def is_unlimited_bots(self) -> bool:
        """Return True if this tier has no bot-creation cap."""
        return self.max_bots is None

    def has_feature(self, feature: str) -> bool:
        """Return True if *feature* is enabled on this tier."""
        return feature in self.features


# ---------------------------------------------------------------------------
# Feature flags
# ---------------------------------------------------------------------------

FEATURE_CORE_MENTOR = "core_mentor"
FEATURE_MEMORY_SYSTEM = "memory_system"
FEATURE_PERSONALITY_ENGINE = "personality_engine"
FEATURE_ROAST_DEFENSE = "roast_defense"
FEATURE_BOT_FACTORY = "bot_factory"
FEATURE_CONTINUOUS_STUDY = "continuous_study"
FEATURE_MONEY_ENGINE = "money_engine"
FEATURE_PROSPECTUS = "prospectus"
FEATURE_COURSES_SYSTEM = "courses_system"
FEATURE_ROUTE_GPS = "route_gps"
FEATURE_SALES_MONETIZATION = "sales_monetization"
FEATURE_CATALOG = "catalog"
FEATURE_FRANCHISE_ENGINE = "franchise_engine"
FEATURE_MASTER_DASHBOARD = "master_dashboard"
FEATURE_TOP_20_AI_MODELS = "top_20_ai_models"
FEATURE_WHITE_LABEL = "white_label"
FEATURE_COMPOUND_INTEREST = "compound_interest"
FEATURE_DAY_TRADING = "day_trading"
FEATURE_BROKER_CONSULTANT = "broker_consultant"
FEATURE_RELATIONSHIP_MENTOR = "relationship_mentor"
FEATURE_COMMUNITY_LEADER = "community_leader"
FEATURE_DEDICATED_SUPPORT = "dedicated_support"

FREE_FEATURES: list[str] = [
    FEATURE_CORE_MENTOR,
    FEATURE_MEMORY_SYSTEM,
    FEATURE_PERSONALITY_ENGINE,
    FEATURE_ROAST_DEFENSE,
    FEATURE_BOT_FACTORY,
    FEATURE_MONEY_ENGINE,
]

PRO_FEATURES: list[str] = FREE_FEATURES + [
    FEATURE_CONTINUOUS_STUDY,
    FEATURE_PROSPECTUS,
    FEATURE_COURSES_SYSTEM,
    FEATURE_ROUTE_GPS,
    FEATURE_SALES_MONETIZATION,
    FEATURE_CATALOG,
    FEATURE_MASTER_DASHBOARD,
    FEATURE_TOP_20_AI_MODELS,
    FEATURE_COMPOUND_INTEREST,
    FEATURE_DAY_TRADING,
    FEATURE_RELATIONSHIP_MENTOR,
    FEATURE_COMMUNITY_LEADER,
]

ENTERPRISE_FEATURES: list[str] = PRO_FEATURES + [
    FEATURE_FRANCHISE_ENGINE,
    FEATURE_BROKER_CONSULTANT,
    FEATURE_WHITE_LABEL,
    FEATURE_DEDICATED_SUPPORT,
]

# ---------------------------------------------------------------------------
# Tier catalogue
# ---------------------------------------------------------------------------

TIER_CATALOGUE: dict[str, TierConfig] = {
    Tier.FREE.value: TierConfig(
        name="Free",
        tier=Tier.FREE,
        price_usd_monthly=0.0,
        max_bots=1,
        max_memory_profiles=10,
        max_ai_models=3,
        features=FREE_FEATURES,
        support_level="Community",
    ),
    Tier.PRO.value: TierConfig(
        name="Pro",
        tier=Tier.PRO,
        price_usd_monthly=49.0,
        max_bots=10,
        max_memory_profiles=500,
        max_ai_models=20,
        features=PRO_FEATURES,
        support_level="Email (24 h SLA)",
    ),
    Tier.ENTERPRISE.value: TierConfig(
        name="Enterprise",
        tier=Tier.ENTERPRISE,
        price_usd_monthly=199.0,
        max_bots=None,
        max_memory_profiles=None,
        max_ai_models=20,
        features=ENTERPRISE_FEATURES,
        support_level="Dedicated 24/7",
    ),
}


def get_tier_config(tier: Tier) -> TierConfig:
    """Return the TierConfig for the given Tier enum value."""
    return TIER_CATALOGUE[tier.value]


def list_tiers() -> list[TierConfig]:
    """Return all tier configs ordered from cheapest to most expensive."""
    return [TIER_CATALOGUE[t.value] for t in Tier]


def get_upgrade_path(current: Tier) -> Optional[TierConfig]:
    """Return the next higher tier, or None if already at the top."""
    order = list(Tier)
    idx = order.index(current)
    if idx + 1 < len(order):
        return get_tier_config(order[idx + 1])
    return None
