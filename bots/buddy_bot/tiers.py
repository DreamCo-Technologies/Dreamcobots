"""
Tier configuration for the Buddy Bot — DreamCo's most human-like AI companion.

Tiers:
  - FREE ($0/mo):        Core conversational AI, basic emotion detection, 5 memory
                         profiles, single persona, text-only interaction.
  - PRO ($49/mo):        Full emotion suite, 100 memory profiles, voice synthesis,
                         multilingual (50+ languages), all persona modes, AR avatar.
  - ENTERPRISE ($199/mo): Unlimited memory, voice cloning (consent-gated), GAN image
                          mimicry, holographic projection API, full VR presence, white-
                          label, dedicated support.
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
    """Configuration for a Buddy Bot subscription tier.

    Attributes
    ----------
    name : str
        Human-readable tier name.
    tier : Tier
        Enum value.
    price_usd_monthly : float
        Monthly subscription price in USD.
    max_memory_profiles : int | None
        Maximum user profiles stored.  None = unlimited.
    max_languages : int
        Number of supported language translations.
    max_personas : int | None
        Maximum simultaneous persona modes.  None = unlimited.
    features : list[str]
        Feature flags enabled on this tier.
    support_level : str
        Support offering description.
    """

    name: str
    tier: Tier
    price_usd_monthly: float
    max_memory_profiles: Optional[int]
    max_languages: int
    max_personas: Optional[int]
    features: list
    support_level: str

    def has_feature(self, feature: str) -> bool:
        """Return True if *feature* is available on this tier."""
        return feature in self.features

    def is_unlimited_memory(self) -> bool:
        """Return True if memory profiles are unlimited."""
        return self.max_memory_profiles is None


# ---------------------------------------------------------------------------
# Feature flags
# ---------------------------------------------------------------------------

FEATURE_CONVERSATIONAL_AI = "conversational_ai"
FEATURE_EMOTION_DETECTION = "emotion_detection"
FEATURE_BASIC_MEMORY = "basic_memory"
FEATURE_MULTILINGUAL = "multilingual"
FEATURE_HUMOR_ENGINE = "humor_engine"
FEATURE_EMPATHY_ENGINE = "empathy_engine"
FEATURE_VOICE_SYNTHESIS = "voice_synthesis"
FEATURE_AVATAR_2D = "avatar_2d"
FEATURE_AVATAR_3D = "avatar_3d"
FEATURE_MICRO_EXPRESSIONS = "micro_expressions"
FEATURE_AR_VR_PRESENCE = "ar_vr_presence"
FEATURE_ADVANCED_MEMORY = "advanced_memory"
FEATURE_MILESTONE_TRACKER = "milestone_tracker"
FEATURE_CONFLICT_RESOLUTION = "conflict_resolution"
FEATURE_MOOD_SYNC = "mood_sync"
FEATURE_PERSONALITY_MODES = "personality_modes"
FEATURE_CREATIVITY_ENGINE = "creativity_engine"
FEATURE_GAMIFIED_PRODUCTIVITY = "gamified_productivity"
FEATURE_VOICE_CLONING = "voice_cloning"
FEATURE_GAN_IMAGE_MIMICRY = "gan_image_mimicry"
FEATURE_HOLOGRAPHIC_PROJECTION = "holographic_projection"
FEATURE_REAL_TIME_TRANSLATION = "real_time_translation"
FEATURE_WELLNESS_TRACKER = "wellness_tracker"
FEATURE_SOCIAL_MEDIA_MANAGER = "social_media_manager"
FEATURE_WHITE_LABEL = "white_label"
FEATURE_API_ACCESS = "api_access"
FEATURE_DEDICATED_SUPPORT = "dedicated_support"

# ---------------------------------------------------------------------------
# Autonomous SaaS feature flags
# ---------------------------------------------------------------------------

FEATURE_LEAD_FINDER = "lead_finder"
FEATURE_OFFER_GENERATOR = "offer_generator"
FEATURE_CONVERSION_ENGINE = "conversion_engine"
FEATURE_FULFILLMENT_ENGINE = "fulfillment_engine"
FEATURE_RETENTION_ENGINE = "retention_engine"

FREE_FEATURES: list = [
    FEATURE_CONVERSATIONAL_AI,
    FEATURE_EMOTION_DETECTION,
    FEATURE_BASIC_MEMORY,
    FEATURE_EMPATHY_ENGINE,
    FEATURE_HUMOR_ENGINE,
    FEATURE_AVATAR_2D,
]

PRO_FEATURES: list = FREE_FEATURES + [
    FEATURE_MULTILINGUAL,
    FEATURE_VOICE_SYNTHESIS,
    FEATURE_AVATAR_3D,
    FEATURE_MICRO_EXPRESSIONS,
    FEATURE_AR_VR_PRESENCE,
    FEATURE_ADVANCED_MEMORY,
    FEATURE_MILESTONE_TRACKER,
    FEATURE_CONFLICT_RESOLUTION,
    FEATURE_MOOD_SYNC,
    FEATURE_PERSONALITY_MODES,
    FEATURE_CREATIVITY_ENGINE,
    FEATURE_GAMIFIED_PRODUCTIVITY,
    FEATURE_REAL_TIME_TRANSLATION,
    FEATURE_WELLNESS_TRACKER,
    FEATURE_LEAD_FINDER,
    FEATURE_OFFER_GENERATOR,
    FEATURE_CONVERSION_ENGINE,
    FEATURE_FULFILLMENT_ENGINE,
    FEATURE_RETENTION_ENGINE,
]

ENTERPRISE_FEATURES: list = PRO_FEATURES + [
    FEATURE_VOICE_CLONING,
    FEATURE_GAN_IMAGE_MIMICRY,
    FEATURE_HOLOGRAPHIC_PROJECTION,
    FEATURE_SOCIAL_MEDIA_MANAGER,
    FEATURE_WHITE_LABEL,
    FEATURE_API_ACCESS,
    FEATURE_DEDICATED_SUPPORT,
]

TIER_CATALOGUE: dict = {
    Tier.FREE.value: TierConfig(
        name="Free",
        tier=Tier.FREE,
        price_usd_monthly=0.0,
        max_memory_profiles=5,
        max_languages=5,
        max_personas=1,
        features=FREE_FEATURES,
        support_level="Community",
    ),
    Tier.PRO.value: TierConfig(
        name="Pro",
        tier=Tier.PRO,
        price_usd_monthly=49.0,
        max_memory_profiles=100,
        max_languages=50,
        max_personas=10,
        features=PRO_FEATURES,
        support_level="Email (24 h SLA)",
    ),
    Tier.ENTERPRISE.value: TierConfig(
        name="Enterprise",
        tier=Tier.ENTERPRISE,
        price_usd_monthly=199.0,
        max_memory_profiles=None,
        max_languages=100,
        max_personas=None,
        features=ENTERPRISE_FEATURES,
        support_level="Dedicated 24/7",
    ),
}


def get_tier_config(tier: Tier) -> TierConfig:
    """Return the TierConfig for *tier*."""
    return TIER_CATALOGUE[tier.value]


def list_tiers() -> list:
    """Return all TierConfig objects in tier order."""
    return [TIER_CATALOGUE[t.value] for t in Tier]


def get_upgrade_path(current: Tier) -> Optional[TierConfig]:
    """Return the next tier's config, or None if already at the top."""
    order = list(Tier)
    idx = order.index(current)
    if idx + 1 < len(order):
        return get_tier_config(order[idx + 1])
    return None
