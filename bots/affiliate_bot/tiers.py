import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'ai-models-integration'))
from tiers import Tier, TierConfig, get_tier_config, get_upgrade_path, list_tiers, TIER_CATALOGUE

BOT_FEATURES = {
    Tier.FREE.value: ["up to 3 niches", "10 products max", "basic earnings estimate", "click tracking"],
    Tier.PRO.value: ["up to 10 niches", "50 products", "advanced earnings estimate", "click tracking", "detailed reports", "email alerts"],
    Tier.ENTERPRISE.value: ["unlimited niches", "unlimited products", "AI-optimized recommendations", "real-time analytics", "custom reports", "API access", "white-label"],
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
