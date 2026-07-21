"""Tier configuration for the Lifestyle Bot."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'ai-models-integration'))

from tiers import Tier, TierConfig, get_tier_config, get_upgrade_path, list_tiers

__all__ = ["Tier", "TierConfig", "get_tier_config", "get_upgrade_path", "list_tiers",
           "LIFESTYLE_FEATURES", "HABIT_LIMITS", "get_lifestyle_tier_info"]

LIFESTYLE_FEATURES: dict[str, list[str]] = {
    Tier.FREE.value: [
        "5 habit trackers",
        "Daily reminders",
        "Basic goal setting",
    ],
    Tier.PRO.value: [
        "Unlimited habits",
        "Habit analytics",
        "Goal milestone tracking",
        "Mood journaling",
        "Weekly reports",
    ],
    Tier.ENTERPRISE.value: [
        "AI coaching",
        "Team habit challenges",
        "Integration with wearables",
        "Custom wellness programs",
        "Advanced analytics",
    ],
}

HABIT_LIMITS: dict[str, int | None] = {
    Tier.FREE.value: 5,
    Tier.PRO.value: None,
    Tier.ENTERPRISE.value: None,
}


def get_lifestyle_tier_info(tier: Tier) -> dict:
    """Return lifestyle-bot-specific tier information as a dict."""
    cfg = get_tier_config(tier)
    return {
        "tier": tier.value,
        "name": cfg.name,
        "price_usd_monthly": cfg.price_usd_monthly,
        "requests_per_month": cfg.requests_per_month,
        "support_level": cfg.support_level,
        "lifestyle_features": LIFESTYLE_FEATURES[tier.value],
        "habit_limit": HABIT_LIMITS[tier.value],
    }
