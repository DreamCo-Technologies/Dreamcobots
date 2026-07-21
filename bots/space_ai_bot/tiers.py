import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'ai-models-integration'))
from tiers import Tier, TierConfig, get_tier_config, get_upgrade_path, list_tiers, TIER_CATALOGUE

BOT_FEATURES = {
    Tier.FREE.value: [
        "simulate trajectories only",
        "track up to 2 satellites",
        "basic orbital position data",
        "public satellite database access",
        "community support",
    ],
    Tier.PRO.value: [
        "plan up to 5 missions",
        "track up to 20 satellites",
        "full trajectory simulation",
        "risk assessment reports",
        "environmental monitoring",
        "planet surface mapping (basic)",
        "anomaly detection",
        "email support",
    ],
    Tier.ENTERPRISE.value: [
        "unlimited mission planning",
        "unlimited satellite tracking",
        "custom satellite tracking",
        "full simulation suite",
        "advanced risk modeling",
        "real-time environmental analytics",
        "high-resolution surface mapping",
        "deep-space mission support",
        "bulk data export",
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
