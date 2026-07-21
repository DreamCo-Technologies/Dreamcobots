import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'ai-models-integration'))
from tiers import Tier, TierConfig, get_tier_config, get_upgrade_path, list_tiers, TIER_CATALOGUE

BOT_FEATURES = {
    Tier.FREE.value: ["1 marketplace platform", "10 items max", "basic deal scoring", "manual refresh"],
    Tier.PRO.value: ["5 platforms", "100 items", "advanced deal scoring", "auto refresh", "price history", "profit calculator"],
    Tier.ENTERPRISE.value: ["all platforms", "unlimited items", "AI deal scoring", "real-time alerts", "arbitrage routing", "bulk analysis", "API access"],
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
