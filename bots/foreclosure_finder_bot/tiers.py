import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'ai-models-integration'))
from tiers import Tier, TierConfig, get_tier_config, get_upgrade_path, list_tiers, TIER_CATALOGUE

BOT_FEATURES = {
    Tier.FREE.value: [
        "search in 1 county",
        "up to 5 results per search",
        "basic foreclosure info (address, status, price)",
        "estimated market discount",
    ],
    Tier.PRO.value: [
        "search in 5 counties",
        "up to 25 results per search",
        "lien status check",
        "auction calendar",
        "tax delinquency status",
        "HOA flag detection",
        "title risk summary",
    ],
    Tier.ENTERPRISE.value: [
        "unlimited county searches",
        "predictive foreclosure alerts",
        "bank REO pipeline access",
        "bulk auction bid analysis",
        "automated title risk scoring",
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
