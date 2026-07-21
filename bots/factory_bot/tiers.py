"""Tier definitions for Factory Bot."""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'ai-models-integration'))
from tiers import Tier, TierConfig, get_tier_config, get_upgrade_path, list_tiers, TIER_CATALOGUE  # noqa: F401

BOT_FEATURES = {
    Tier.FREE.value: [
        "monitor 2 machines",
        "basic workflow analysis",
        "energy usage overview",
        "5 production orders scheduling",
        "basic sustainability score",
    ],
    Tier.PRO.value: [
        "monitor 20 machines",
        "predictive maintenance analytics",
        "advanced workflow optimization",
        "bottleneck analysis",
        "energy optimization recommendations",
        "carbon footprint calculation",
        "waste reduction planning",
        "50 production orders scheduling",
    ],
    Tier.ENTERPRISE.value: [
        "unlimited machine monitoring",
        "ML-powered failure prediction",
        "full production line optimization",
        "real-time sensor analytics",
        "comprehensive green reports",
        "facility-wide energy intelligence",
        "unlimited production scheduling",
        "custom maintenance models",
        "API access",
        "white-label reports",
    ],
}


def get_bot_tier_info(tier: Tier) -> dict:
    """Return tier metadata merged with bot-specific feature list."""
    cfg = get_tier_config(tier)
    return {
        "tier": tier.value,
        "name": cfg.name,
        "price_usd_monthly": cfg.price_usd_monthly,
        "requests_per_month": cfg.requests_per_month,
        "features": BOT_FEATURES[tier.value],
        "support_level": cfg.support_level,
    }
