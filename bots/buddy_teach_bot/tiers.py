"""
Tier configuration for the Buddy Teach Bot.

Tiers:
  - FREE:            Basic skill lessons, 1 broadcast target, item valuation.
  - PRO ($49):       Full lesson library, multi-device broadcast, AI training,
                     personality customization.
  - ENTERPRISE ($199): Unlimited broadcast targets, white-label, API access,
                        custom curriculum building, dedicated support.
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
    """Configuration for a Buddy Teach Bot subscription tier."""

    name: str
    tier: Tier
    price_usd_monthly: float
    max_broadcast_targets: Optional[int]
    max_skill_tracks: Optional[int]
    max_ai_training_sessions: Optional[int]
    features: list
    support_level: str

    def has_feature(self, feature: str) -> bool:
        return feature in self.features

    def is_unlimited_broadcast(self) -> bool:
        return self.max_broadcast_targets is None


# ---------------------------------------------------------------------------
# Feature flags
# ---------------------------------------------------------------------------

FEATURE_SKILL_TRAINING = "skill_training"
FEATURE_ITEM_DETECTION = "item_detection"
FEATURE_BROADCAST = "broadcast"
FEATURE_MULTI_BROADCAST = "multi_broadcast"
FEATURE_PERSONALITY = "personality"
FEATURE_AI_TRAINING = "ai_training"
FEATURE_CURRICULUM_BUILDER = "curriculum_builder"
FEATURE_AR_VR_OVERLAY = "ar_vr_overlay"
FEATURE_LIVE_FEEDBACK = "live_feedback"
FEATURE_WHITE_LABEL = "white_label"
FEATURE_API_ACCESS = "api_access"
FEATURE_DEDICATED_SUPPORT = "dedicated_support"

FREE_FEATURES: list = [
    FEATURE_SKILL_TRAINING,
    FEATURE_ITEM_DETECTION,
    FEATURE_BROADCAST,
    FEATURE_PERSONALITY,
]

PRO_FEATURES: list = FREE_FEATURES + [
    FEATURE_MULTI_BROADCAST,
    FEATURE_AI_TRAINING,
    FEATURE_AR_VR_OVERLAY,
    FEATURE_LIVE_FEEDBACK,
]

ENTERPRISE_FEATURES: list = PRO_FEATURES + [
    FEATURE_CURRICULUM_BUILDER,
    FEATURE_WHITE_LABEL,
    FEATURE_API_ACCESS,
    FEATURE_DEDICATED_SUPPORT,
]

TIER_CATALOGUE: dict = {
    Tier.FREE.value: TierConfig(
        name="Free",
        tier=Tier.FREE,
        price_usd_monthly=0.0,
        max_broadcast_targets=1,
        max_skill_tracks=3,
        max_ai_training_sessions=10,
        features=FREE_FEATURES,
        support_level="Community",
    ),
    Tier.PRO.value: TierConfig(
        name="Pro",
        tier=Tier.PRO,
        price_usd_monthly=49.0,
        max_broadcast_targets=10,
        max_skill_tracks=25,
        max_ai_training_sessions=500,
        features=PRO_FEATURES,
        support_level="Email (24 h SLA)",
    ),
    Tier.ENTERPRISE.value: TierConfig(
        name="Enterprise",
        tier=Tier.ENTERPRISE,
        price_usd_monthly=199.0,
        max_broadcast_targets=None,
        max_skill_tracks=None,
        max_ai_training_sessions=None,
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
