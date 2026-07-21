import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'ai-models-integration'))
from tiers import Tier, TierConfig, get_tier_config, get_upgrade_path, list_tiers, TIER_CATALOGUE

BOT_FEATURES = {
    Tier.FREE.value: [
        "1 property at a time",
        "basic ARV estimate",
        "simple flip score (0-100)",
        "purchase price + renovation cost summary",
    ],
    Tier.PRO.value: [
        "5 properties simultaneously",
        "detailed renovation cost breakdown by category",
        "holding cost calculation",
        "financing cost modeling",
        "profit margin & ROI analysis",
        "comparable sales lookup",
        "flip score with breakdown",
    ],
    Tier.ENTERPRISE.value: [
        "unlimited properties",
        "contractor bidding simulator",
        "market timing analysis",
        "neighborhood trend overlay",
        "risk-adjusted ROI projections",
        "bulk portfolio flip analysis",
        "API access",
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
