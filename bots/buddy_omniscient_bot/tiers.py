"""
Tier configuration for the Buddy Omniscient Bot.

Tiers:
  - FREE ($0):        AR/VR demos, 5 viral challenges, community skill browsing,
                      basic knowledge queries.
  - PRO ($49):        Full AR/VR engine, unlimited viral challenges, Buddy Badges,
                      community skill uploads, expert collaboration, social content
                      creation tools, Reality Show participation.
  - ENTERPRISE ($199): White-label, API access, unlimited knowledge domains,
                       dedicated expert partnerships, advanced analytics, charity
                       ambassador program, DreamYourBusiness full suite.
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
    """Configuration for a Buddy Omniscient subscription tier."""

    name: str
    tier: Tier
    price_usd_monthly: float
    max_ar_sessions: Optional[int]
    max_viral_challenges: Optional[int]
    max_skill_uploads: Optional[int]
    max_knowledge_domains: Optional[int]
    features: list
    support_level: str

    def has_feature(self, feature: str) -> bool:
        return feature in self.features

    def is_unlimited_knowledge(self) -> bool:
        return self.max_knowledge_domains is None


# ---------------------------------------------------------------------------
# Feature flags
# ---------------------------------------------------------------------------

FEATURE_AR_VR = "ar_vr_engine"
FEATURE_HOLOGRAPHIC = "holographic_projection"
FEATURE_VIRAL_CHALLENGES = "viral_challenges"
FEATURE_BUDDY_BADGES = "buddy_badges"
FEATURE_SKILL_DATABASE = "skill_database"
FEATURE_SKILL_UPLOAD = "skill_upload"
FEATURE_KNOWLEDGE_ENGINE = "knowledge_engine"
FEATURE_OMNISCIENT_MODE = "omniscient_mode"
FEATURE_SOCIAL_CREATORS = "social_creators"
FEATURE_REALITY_SHOW = "reality_show"
FEATURE_CHARITY_AMBASSADOR = "charity_ambassador"
FEATURE_DREAM_BUSINESS = "dream_your_business"
FEATURE_EXPERT_COLLABORATION = "expert_collaboration"
FEATURE_DYNAMIC_LEARNING = "dynamic_learning"
FEATURE_WHITE_LABEL = "white_label"
FEATURE_API_ACCESS = "api_access"
FEATURE_ADVANCED_ANALYTICS = "advanced_analytics"
FEATURE_DEDICATED_SUPPORT = "dedicated_support"

FREE_FEATURES: list = [
    FEATURE_AR_VR,
    FEATURE_VIRAL_CHALLENGES,
    FEATURE_SKILL_DATABASE,
    FEATURE_KNOWLEDGE_ENGINE,
    FEATURE_DYNAMIC_LEARNING,
]

PRO_FEATURES: list = FREE_FEATURES + [
    FEATURE_HOLOGRAPHIC,
    FEATURE_BUDDY_BADGES,
    FEATURE_SKILL_UPLOAD,
    FEATURE_OMNISCIENT_MODE,
    FEATURE_SOCIAL_CREATORS,
    FEATURE_REALITY_SHOW,
    FEATURE_CHARITY_AMBASSADOR,
    FEATURE_DREAM_BUSINESS,
    FEATURE_EXPERT_COLLABORATION,
]

ENTERPRISE_FEATURES: list = PRO_FEATURES + [
    FEATURE_WHITE_LABEL,
    FEATURE_API_ACCESS,
    FEATURE_ADVANCED_ANALYTICS,
    FEATURE_DEDICATED_SUPPORT,
]

TIER_CATALOGUE: dict = {
    Tier.FREE.value: TierConfig(
        name="Free",
        tier=Tier.FREE,
        price_usd_monthly=0.0,
        max_ar_sessions=5,
        max_viral_challenges=5,
        max_skill_uploads=0,
        max_knowledge_domains=10,
        features=FREE_FEATURES,
        support_level="Community",
    ),
    Tier.PRO.value: TierConfig(
        name="Pro",
        tier=Tier.PRO,
        price_usd_monthly=49.0,
        max_ar_sessions=100,
        max_viral_challenges=None,
        max_skill_uploads=50,
        max_knowledge_domains=500,
        features=PRO_FEATURES,
        support_level="Email (24 h SLA)",
    ),
    Tier.ENTERPRISE.value: TierConfig(
        name="Enterprise",
        tier=Tier.ENTERPRISE,
        price_usd_monthly=199.0,
        max_ar_sessions=None,
        max_viral_challenges=None,
        max_skill_uploads=None,
        max_knowledge_domains=None,
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
