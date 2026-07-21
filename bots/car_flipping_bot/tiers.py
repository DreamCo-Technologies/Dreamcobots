import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'ai-models-integration'))
from tiers import Tier, TierConfig, get_tier_config, get_upgrade_path, list_tiers, TIER_CATALOGUE

BOT_FEATURES = {
    Tier.FREE.value: ["1 make at a time", "5 results max", "basic valuation", "flip potential score"],
    Tier.PRO.value: ["any make", "20 results", "detailed vehicle history", "flip profit calculator", "repair cost estimate"],
    Tier.ENTERPRISE.value: ["all makes/models", "50 results", "market price prediction", "auction access data", "bulk analysis", "API access"],
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
