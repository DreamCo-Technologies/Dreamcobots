"""
Tier definitions and access control for the Photo Editing Bot.

Tiers:
  - FREE:       Basic editing, background removal, filters, JPG/PNG export, 10 photos/day.
  - PRO:        Noise removal, batch editing, cartoon conversion, caricature, HD export, 100/day.
  - ENTERPRISE: Animation generation, cartoon frame generation, frame-by-frame AI, unlimited.
"""

from __future__ import annotations

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "ai-models-integration"))

from tiers import Tier, TierConfig, get_tier_config, get_upgrade_path, list_tiers, TIER_CATALOGUE  # noqa: F401


# Feature flags as string constants
FEATURE_BASIC_EDITING = "basic_editing"
FEATURE_BACKGROUND_REMOVAL = "background_removal"
FEATURE_FILTERS = "filters"
FEATURE_JPG_PNG_EXPORT = "jpg_png_export"
FEATURE_NOISE_REMOVAL = "noise_removal"
FEATURE_BATCH_EDITING = "batch_editing"
FEATURE_CARTOON_CONVERSION = "cartoon_conversion"
FEATURE_CARICATURE = "caricature"
FEATURE_HD_EXPORT = "hd_export"
FEATURE_ANIMATION_GENERATION = "animation_generation"
FEATURE_CARTOON_FRAME_GENERATION = "cartoon_frame_generation"
FEATURE_FRAME_BY_FRAME_AI = "frame_by_frame_ai"
FEATURE_COMMERCIAL_RIGHTS = "commercial_rights"
FEATURE_WHITE_LABEL = "white_label"

FREE_FEATURES = [
    FEATURE_BASIC_EDITING,
    FEATURE_BACKGROUND_REMOVAL,
    FEATURE_FILTERS,
    FEATURE_JPG_PNG_EXPORT,
]

PRO_FEATURES = FREE_FEATURES + [
    FEATURE_NOISE_REMOVAL,
    FEATURE_BATCH_EDITING,
    FEATURE_CARTOON_CONVERSION,
    FEATURE_CARICATURE,
    FEATURE_HD_EXPORT,
]

ENTERPRISE_FEATURES = PRO_FEATURES + [
    FEATURE_ANIMATION_GENERATION,
    FEATURE_CARTOON_FRAME_GENERATION,
    FEATURE_FRAME_BY_FRAME_AI,
    FEATURE_COMMERCIAL_RIGHTS,
    FEATURE_WHITE_LABEL,
]

BOT_FEATURES = {
    Tier.FREE.value: FREE_FEATURES,
    Tier.PRO.value: PRO_FEATURES,
    Tier.ENTERPRISE.value: ENTERPRISE_FEATURES,
}

DAILY_LIMITS = {
    Tier.FREE.value: 10,
    Tier.PRO.value: 100,
    Tier.ENTERPRISE.value: None,  # unlimited
}


def get_bot_tier_info(tier: Tier) -> dict:
    """Return a dict describing the Photo Editing Bot's features for the given tier."""
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
