"""
Tier definitions and access control for the Creative Studio Bot.

Tiers:
  - FREE:       3 creations/day, basic tools, watermarked exports.
  - PRO:        50 creations/day, advanced AI tools, HD exports.
  - ENTERPRISE: Unlimited creations, commercial rights, white-label, API access.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "ai-models-integration"))

from tiers import Tier, TierConfig, get_tier_config, get_upgrade_path, list_tiers, TIER_CATALOGUE  # noqa: F401


# ---------------------------------------------------------------------------
# Feature flags
# ---------------------------------------------------------------------------

FEATURE_MUSIC_CREATION = "music_creation"
FEATURE_FILM_SCRIPTING = "film_scripting"
FEATURE_ART_GENERATION = "art_generation"
FEATURE_BASIC_3D_MODELING = "basic_3d_modeling"
FEATURE_CONTENT_CALENDAR = "content_calendar"
FEATURE_MEME_GENERATOR = "meme_generator"
FEATURE_ADVANCED_MUSIC = "advanced_music"
FEATURE_STORYBOARD = "storyboard"
FEATURE_ADVANCED_ART = "advanced_art"
FEATURE_ADVANCED_3D = "advanced_3d"
FEATURE_VIRAL_ANALYTICS = "viral_analytics"
FEATURE_INFLUENCER_ENGINE = "influencer_engine"
FEATURE_COMMERCIAL_RIGHTS = "commercial_rights"
FEATURE_WHITE_LABEL = "white_label"
FEATURE_API_ACCESS = "api_access"
FEATURE_DEDICATED_SUPPORT = "dedicated_support"
FEATURE_BULK_EXPORT = "bulk_export"
FEATURE_TEAM_COLLABORATION = "team_collaboration"

FREE_FEATURES = [
    FEATURE_MUSIC_CREATION,
    FEATURE_FILM_SCRIPTING,
    FEATURE_ART_GENERATION,
    FEATURE_BASIC_3D_MODELING,
    FEATURE_CONTENT_CALENDAR,
    FEATURE_MEME_GENERATOR,
]

PRO_FEATURES = FREE_FEATURES + [
    FEATURE_ADVANCED_MUSIC,
    FEATURE_STORYBOARD,
    FEATURE_ADVANCED_ART,
    FEATURE_ADVANCED_3D,
    FEATURE_VIRAL_ANALYTICS,
    FEATURE_INFLUENCER_ENGINE,
    FEATURE_BULK_EXPORT,
]

ENTERPRISE_FEATURES = PRO_FEATURES + [
    FEATURE_COMMERCIAL_RIGHTS,
    FEATURE_WHITE_LABEL,
    FEATURE_API_ACCESS,
    FEATURE_DEDICATED_SUPPORT,
    FEATURE_TEAM_COLLABORATION,
]

BOT_FEATURES = {
    Tier.FREE.value: FREE_FEATURES,
    Tier.PRO.value: PRO_FEATURES,
    Tier.ENTERPRISE.value: ENTERPRISE_FEATURES,
}

DAILY_CREATION_LIMITS = {
    Tier.FREE.value: 3,
    Tier.PRO.value: 50,
    Tier.ENTERPRISE.value: None,  # unlimited
}


def get_bot_tier_info(tier: Tier) -> dict:
    """Return a dict describing the Creative Studio Bot's features for the given tier."""
    config = get_tier_config(tier)
    return {
        "tier": tier.value,
        "name": config.name,
        "price_usd_monthly": config.price_usd_monthly,
        "features": BOT_FEATURES[tier.value],
        "daily_creation_limit": DAILY_CREATION_LIMITS[tier.value],
        "support_level": config.support_level,
        "commercial_rights": FEATURE_COMMERCIAL_RIGHTS in BOT_FEATURES[tier.value],
    }
