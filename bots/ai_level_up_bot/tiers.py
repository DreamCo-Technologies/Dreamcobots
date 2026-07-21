"""
Tier configuration for the DreamCo AI Level-Up Bot.

Tiers:
  - STARTER ($29/month):    AI basics, limited database access, 5 tokens/day.
  - PRO ($99/month):        Full database, all courses, 40 tokens/day, skill tree.
  - ENTERPRISE ($399/month): Unlimited access, API, agent generator, white-label.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class Tier(Enum):
    STARTER = "starter"
    PRO = "pro"
    ENTERPRISE = "enterprise"


@dataclass
class TierConfig:
    """Configuration for a DreamCo AI Level-Up Bot subscription tier."""

    name: str
    tier: Tier
    price_usd_monthly: float
    max_tokens_per_day: Optional[int]
    max_companies_accessible: Optional[int]
    max_course_levels: int
    features: list
    support_level: str

    def has_feature(self, feature: str) -> bool:
        return feature in self.features

    def is_unlimited_tokens(self) -> bool:
        return self.max_tokens_per_day is None

    def is_unlimited_companies(self) -> bool:
        return self.max_companies_accessible is None


# ---------------------------------------------------------------------------
# Feature flags
# ---------------------------------------------------------------------------

FEATURE_AI_COMPANIES_DATABASE = "ai_companies_database"
FEATURE_AI_COURSE_ENGINE = "ai_course_engine"
FEATURE_TOKEN_MARKETPLACE = "token_marketplace"
FEATURE_AI_SKILL_TREE = "ai_skill_tree"
FEATURE_AI_AGENTS_GENERATOR = "ai_agents_generator"
FEATURE_FULL_DATABASE = "full_database"
FEATURE_ADVANCED_COURSES = "advanced_courses"
FEATURE_SKILL_TREE_REWARDS = "skill_tree_rewards"
FEATURE_CUSTOM_AGENTS = "custom_agents"
FEATURE_API_ACCESS = "api_access"
FEATURE_WHITE_LABEL = "white_label"
FEATURE_DEDICATED_SUPPORT = "dedicated_support"

STARTER_FEATURES: list = [
    FEATURE_AI_COMPANIES_DATABASE,
    FEATURE_AI_COURSE_ENGINE,
    FEATURE_TOKEN_MARKETPLACE,
]

PRO_FEATURES: list = STARTER_FEATURES + [
    FEATURE_FULL_DATABASE,
    FEATURE_ADVANCED_COURSES,
    FEATURE_AI_SKILL_TREE,
    FEATURE_SKILL_TREE_REWARDS,
    FEATURE_CUSTOM_AGENTS,
]

ENTERPRISE_FEATURES: list = PRO_FEATURES + [
    FEATURE_AI_AGENTS_GENERATOR,
    FEATURE_API_ACCESS,
    FEATURE_WHITE_LABEL,
    FEATURE_DEDICATED_SUPPORT,
]

TIER_CATALOGUE: dict = {
    Tier.STARTER.value: TierConfig(
        name="Starter",
        tier=Tier.STARTER,
        price_usd_monthly=29.0,
        max_tokens_per_day=5,
        max_companies_accessible=25,
        max_course_levels=3,
        features=STARTER_FEATURES,
        support_level="Community",
    ),
    Tier.PRO.value: TierConfig(
        name="Pro",
        tier=Tier.PRO,
        price_usd_monthly=99.0,
        max_tokens_per_day=40,
        max_companies_accessible=None,
        max_course_levels=7,
        features=PRO_FEATURES,
        support_level="Email (48 h SLA)",
    ),
    Tier.ENTERPRISE.value: TierConfig(
        name="Enterprise",
        tier=Tier.ENTERPRISE,
        price_usd_monthly=399.0,
        max_tokens_per_day=None,
        max_companies_accessible=None,
        max_course_levels=10,
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
