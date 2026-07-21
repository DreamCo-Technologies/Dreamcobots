import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'ai-models-integration'))
from tiers import Tier, TierConfig, get_tier_config, get_upgrade_path, list_tiers, TIER_CATALOGUE

BOT_FEATURES = {
    Tier.FREE.value: ["1 US state search", "basic unclaimed funds lookup", "manual recovery steps"],
    Tier.PRO.value: ["all US states", "government benefits checker", "cashback finder", "recovery workflow", "email alerts"],
    Tier.ENTERPRISE.value: ["all states + international", "automated recovery pipeline", "portfolio of found money", "bulk family search", "API access", "white-label"],
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
