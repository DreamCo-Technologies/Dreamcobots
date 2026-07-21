"""
Tier definitions and access control for the Professional Music Editing Bot.

Tiers:
  - FREE:       Basic editing, MP3 export, 2 tracks max, 3 projects/month.
  - PRO:        Multi-track (16 tracks), AI composition, noise reduction, WAV/AIFF export, 30/month.
  - ENTERPRISE: Unlimited tracks, AI mastering, DAW compatibility, real-time collaboration, unlimited.
"""

from __future__ import annotations

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "ai-models-integration"))

from tiers import Tier, TierConfig, get_tier_config, get_upgrade_path, list_tiers, TIER_CATALOGUE  # noqa: F401


# Feature flags as string constants
FEATURE_BASIC_EDITING = "basic_editing"
FEATURE_MP3_EXPORT = "mp3_export"
FEATURE_MULTI_TRACK_EDITING = "multi_track_editing"
FEATURE_AI_COMPOSITION = "ai_composition"
FEATURE_NOISE_REDUCTION = "noise_reduction"
FEATURE_WAV_AIFF_EXPORT = "wav_aiff_export"
FEATURE_UNLIMITED_TRACKS = "unlimited_tracks"
FEATURE_AI_MASTERING = "ai_mastering"
FEATURE_DAW_COMPATIBILITY = "daw_compatibility"
FEATURE_REAL_TIME_COLLABORATION = "real_time_collaboration"
FEATURE_COMMERCIAL_RIGHTS = "commercial_rights"

FREE_FEATURES = [
    FEATURE_BASIC_EDITING,
    FEATURE_MP3_EXPORT,
]

PRO_FEATURES = FREE_FEATURES + [
    FEATURE_MULTI_TRACK_EDITING,
    FEATURE_AI_COMPOSITION,
    FEATURE_NOISE_REDUCTION,
    FEATURE_WAV_AIFF_EXPORT,
]

ENTERPRISE_FEATURES = PRO_FEATURES + [
    FEATURE_UNLIMITED_TRACKS,
    FEATURE_AI_MASTERING,
    FEATURE_DAW_COMPATIBILITY,
    FEATURE_REAL_TIME_COLLABORATION,
    FEATURE_COMMERCIAL_RIGHTS,
]

BOT_FEATURES = {
    Tier.FREE.value: FREE_FEATURES,
    Tier.PRO.value: PRO_FEATURES,
    Tier.ENTERPRISE.value: ENTERPRISE_FEATURES,
}

# Monthly project limits
MONTHLY_LIMITS = {
    Tier.FREE.value: 3,
    Tier.PRO.value: 30,
    Tier.ENTERPRISE.value: None,  # unlimited
}

# Alias for backwards compatibility
DAILY_LIMITS = MONTHLY_LIMITS

TRACK_LIMITS = {
    Tier.FREE.value: 2,
    Tier.PRO.value: 16,
    Tier.ENTERPRISE.value: None,  # unlimited
}


def get_bot_tier_info(tier: Tier) -> dict:
    """Return a dict describing the Professional Music Editing Bot's features for the given tier."""
    config = get_tier_config(tier)
    return {
        "tier": tier.value,
        "name": config.name,
        "price_usd_monthly": config.price_usd_monthly,
        "features": BOT_FEATURES[tier.value],
        "monthly_limit": MONTHLY_LIMITS[tier.value],
        "track_limit": TRACK_LIMITS[tier.value],
        "support_level": config.support_level,
        "commercial_rights": FEATURE_COMMERCIAL_RIGHTS in BOT_FEATURES[tier.value],
    }
