"""
Tier definitions and access control for the Voice Replicator Bot.

Tiers:
  - FREE:       Basic TTS, 5 languages, 10 requests/day.
  - PRO:        Advanced TTS, HD synthesis, all 25 languages, 200 requests/day.
  - ENTERPRISE: Voice cloning, real-time translation, natural tone adaptation, unlimited.
"""

from __future__ import annotations

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "ai-models-integration"))

from tiers import Tier, TierConfig, get_tier_config, get_upgrade_path, list_tiers, TIER_CATALOGUE  # noqa: F401


# Feature flags as string constants
FEATURE_BASIC_TTS = "basic_tts"
FEATURE_ADVANCED_TTS = "advanced_tts"
FEATURE_LANGUAGE_BASIC = "language_support_basic"
FEATURE_LANGUAGE_FULL = "language_support_full"
FEATURE_VOICE_SYNTHESIS_HD = "voice_synthesis_hd"
FEATURE_VOICE_CLONING = "voice_cloning"
FEATURE_REAL_TIME_TRANSLATION = "real_time_translation"
FEATURE_NATURAL_TONE_ADAPTATION = "natural_tone_adaptation"
FEATURE_COMMERCIAL_RIGHTS = "commercial_rights"

FREE_FEATURES = [
    FEATURE_BASIC_TTS,
    FEATURE_LANGUAGE_BASIC,
]

PRO_FEATURES = FREE_FEATURES + [
    FEATURE_ADVANCED_TTS,
    FEATURE_LANGUAGE_FULL,
    FEATURE_VOICE_SYNTHESIS_HD,
]

ENTERPRISE_FEATURES = PRO_FEATURES + [
    FEATURE_VOICE_CLONING,
    FEATURE_REAL_TIME_TRANSLATION,
    FEATURE_NATURAL_TONE_ADAPTATION,
    FEATURE_COMMERCIAL_RIGHTS,
]

BOT_FEATURES = {
    Tier.FREE.value: FREE_FEATURES,
    Tier.PRO.value: PRO_FEATURES,
    Tier.ENTERPRISE.value: ENTERPRISE_FEATURES,
}

DAILY_LIMITS = {
    Tier.FREE.value: 10,
    Tier.PRO.value: 200,
    Tier.ENTERPRISE.value: None,  # unlimited
}


def get_bot_tier_info(tier: Tier) -> dict:
    """Return a dict describing the Voice Replicator Bot's features for the given tier."""
    config = get_tier_config(tier)
    return {
        "tier": tier.value,
        "name": config.name,
        "price_usd_monthly": config.price_usd_monthly,
        "features": BOT_FEATURES[tier.value],
        "daily_limit": DAILY_LIMITS[tier.value],
        "support_level": config.support_level,
        "commercial_rights": FEATURE_COMMERCIAL_RIGHTS in BOT_FEATURES[tier.value],
    }
