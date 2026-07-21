"""Tier configuration for the Health & Wellness Bot."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'ai-models-integration'))

from tiers import Tier, TierConfig, get_tier_config, get_upgrade_path, list_tiers

__all__ = ["Tier", "TierConfig", "get_tier_config", "get_upgrade_path", "list_tiers",
           "HEALTH_FEATURES", "get_health_tier_info"]

HEALTH_FEATURES: dict[str, list[str]] = {
    Tier.FREE.value: [
        "BMI calculation",
        "Basic calorie tracking",
        "Step counter",
    ],
    Tier.PRO.value: [
        "Macro nutrient tracking",
        "Workout plans",
        "Sleep tracking",
        "Heart rate zones",
        "Progress photos (5/month)",
    ],
    Tier.ENTERPRISE.value: [
        "AI health coach",
        "Integration with health devices",
        "Medical record summaries",
        "Personalized nutrition plans",
        "Telehealth scheduling",
    ],
}


def get_health_tier_info(tier: Tier) -> dict:
    """Return health-bot-specific tier information as a dict."""
    cfg = get_tier_config(tier)
    return {
        "tier": tier.value,
        "name": cfg.name,
        "price_usd_monthly": cfg.price_usd_monthly,
        "requests_per_month": cfg.requests_per_month,
        "support_level": cfg.support_level,
        "health_features": HEALTH_FEATURES[tier.value],
    }
