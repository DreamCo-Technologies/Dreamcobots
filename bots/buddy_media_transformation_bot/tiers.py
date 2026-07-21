"""
Tier definitions and access control for the Buddy Media Transformation Bot.

Tiers:
  - FREE:       Basic text-to-music, watermarked output, 3 creations/day.
  - PRO:        Advanced music, voice integration, video creation, 20 creations/day.
  - ENTERPRISE: User voice cloning, avatar creation, custom visual styles, commercial rights, unlimited.
"""

from __future__ import annotations

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "ai-models-integration"))

from tiers import Tier, TierConfig, get_tier_config, get_upgrade_path, list_tiers, TIER_CATALOGUE  # noqa: F401


# Feature flags as string constants
FEATURE_TEXT_TO_MUSIC_BASIC = "text_to_music_basic"
FEATURE_TEXT_TO_MUSIC_ADVANCED = "text_to_music_advanced"
FEATURE_VOICE_INTEGRATION = "voice_integration"
FEATURE_VIDEO_CREATION = "video_creation"
FEATURE_USER_VOICE_CLONING = "user_voice_cloning"
FEATURE_AVATAR_CREATION = "avatar_creation"
FEATURE_CUSTOM_VISUAL_STYLES = "custom_visual_styles"
FEATURE_WATERMARK = "watermark"
FEATURE_COMMERCIAL_RIGHTS = "commercial_rights"

FREE_FEATURES = [
    FEATURE_TEXT_TO_MUSIC_BASIC,
    FEATURE_WATERMARK,
]

PRO_FEATURES = [
    FEATURE_TEXT_TO_MUSIC_BASIC,
    FEATURE_TEXT_TO_MUSIC_ADVANCED,
    FEATURE_VOICE_INTEGRATION,
    FEATURE_VIDEO_CREATION,
]

ENTERPRISE_FEATURES = PRO_FEATURES + [
    FEATURE_USER_VOICE_CLONING,
    FEATURE_AVATAR_CREATION,
    FEATURE_CUSTOM_VISUAL_STYLES,
    FEATURE_COMMERCIAL_RIGHTS,
]

BOT_FEATURES = {
    Tier.FREE.value: FREE_FEATURES,
    Tier.PRO.value: PRO_FEATURES,
    Tier.ENTERPRISE.value: ENTERPRISE_FEATURES,
}

DAILY_LIMITS = {
    Tier.FREE.value: 3,
    Tier.PRO.value: 20,
    Tier.ENTERPRISE.value: None,  # unlimited
}


def get_bot_tier_info(tier: Tier) -> dict:
    """Return a dict describing the Buddy Media Transformation Bot's features for the given tier."""
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
