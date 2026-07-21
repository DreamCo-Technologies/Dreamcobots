import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'ai-models-integration'))
from tiers import Tier, TierConfig, get_tier_config, get_upgrade_path, list_tiers, TIER_CATALOGUE

BOT_FEATURES = {
    Tier.FREE.value: [
        "1 zone monitored",
        "3 sensor readings per query",
        "basic traffic optimization",
        "basic energy monitoring",
        "community safety alerts",
    ],
    Tier.PRO.value: [
        "10 zones monitored",
        "unlimited sensor readings",
        "advanced traffic flow prediction",
        "energy demand forecasting",
        "incident resource deployment",
        "demographic analytics",
        "tax policy modeling",
    ],
    Tier.ENTERPRISE.value: [
        "unlimited zones",
        "full real-time analytics",
        "predictive city modeling",
        "population projection",
        "policy impact simulation",
        "bulk data export",
        "API access",
        "dedicated city dashboard",
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
