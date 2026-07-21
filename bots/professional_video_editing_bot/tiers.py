"""
Tier definitions and access control for the Professional Video Editing Bot.

Tiers:
  - FREE:       Basic editing, 1080p MP4 export, 5 clips max, 3 projects/month.
  - PRO:        AI transitions, color grading, motion tracking, 4K export, 30/month.
  - ENTERPRISE: Render optimization, NLE compatibility, real-time collaboration, unlimited.
"""

from __future__ import annotations

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "ai-models-integration"))

from tiers import Tier, TierConfig, get_tier_config, get_upgrade_path, list_tiers, TIER_CATALOGUE  # noqa: F401


# Feature flags as string constants
FEATURE_BASIC_EDITING = "basic_editing"
FEATURE_MP4_1080P_EXPORT = "mp4_1080p_export"
FEATURE_AI_TRANSITIONS = "ai_transitions"
FEATURE_COLOR_GRADING = "color_grading"
FEATURE_MOTION_TRACKING = "motion_tracking"
FEATURE_EXPORT_4K = "export_4k"
FEATURE_RENDER_OPTIMIZATION = "render_optimization"
FEATURE_NLE_COMPATIBILITY = "nle_compatibility"
FEATURE_REAL_TIME_COLLABORATION = "real_time_collaboration"
FEATURE_COMMERCIAL_RIGHTS = "commercial_rights"

FREE_FEATURES = [
    FEATURE_BASIC_EDITING,
    FEATURE_MP4_1080P_EXPORT,
]

PRO_FEATURES = FREE_FEATURES + [
    FEATURE_AI_TRANSITIONS,
    FEATURE_COLOR_GRADING,
    FEATURE_MOTION_TRACKING,
    FEATURE_EXPORT_4K,
]

ENTERPRISE_FEATURES = PRO_FEATURES + [
    FEATURE_RENDER_OPTIMIZATION,
    FEATURE_NLE_COMPATIBILITY,
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

CLIP_LIMITS = {
    Tier.FREE.value: 5,
    Tier.PRO.value: None,
    Tier.ENTERPRISE.value: None,
}


def get_bot_tier_info(tier: Tier) -> dict:
    """Return a dict describing the Professional Video Editing Bot's features for the given tier."""
    config = get_tier_config(tier)
    return {
        "tier": tier.value,
        "name": config.name,
        "price_usd_monthly": config.price_usd_monthly,
        "features": BOT_FEATURES[tier.value],
        "monthly_limit": MONTHLY_LIMITS[tier.value],
        "clip_limit": CLIP_LIMITS[tier.value],
        "support_level": config.support_level,
        "commercial_rights": FEATURE_COMMERCIAL_RIGHTS in BOT_FEATURES[tier.value],
    }
