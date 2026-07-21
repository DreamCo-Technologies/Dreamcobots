"""Tier definitions for the Emotional AI Bot."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'ai-models-integration'))
from tiers import Tier, TierConfig, get_tier_config, get_upgrade_path, list_tiers, TIER_CATALOGUE  # noqa: F401

BOT_FEATURES = {
    Tier.FREE.value: [
        "basic emotion recognition (4 emotions)",
        "simple coping strategy suggestions",
        "daily affirmations (3 per day)",
        "basic mental wellness tips",
        "community support",
    ],
    Tier.PRO.value: [
        "full emotion recognition (8 emotions)",
        "personality tone adaptation",
        "personalized coping strategies",
        "mental health assessment (non-diagnostic)",
        "wellness plan creation",
        "productivity coaching sessions",
        "progress tracking",
        "daily affirmations (unlimited)",
        "email support",
    ],
    Tier.ENTERPRISE.value: [
        "full emotion recognition (8 emotions)",
        "emotional state history & analytics",
        "environmental shift analysis",
        "advanced personality calibration",
        "comprehensive mental health coaching",
        "custom wellness plans",
        "full productivity coaching suite",
        "emotional dashboard & reporting",
        "unlimited progress tracking",
        "API access",
        "dedicated 24/7 support",
    ],
}


def get_bot_tier_info(tier: Tier) -> dict:
    cfg = get_tier_config(tier)
    return {
        "tier": tier.value,
        "name": cfg.name,
        "price_usd_monthly": cfg.price_usd_monthly,
        "requests_per_month": cfg.requests_per_month,
        "features": BOT_FEATURES[tier.value],
        "support_level": cfg.support_level,
    }
