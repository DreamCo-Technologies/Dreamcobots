import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'ai-models-integration'))
from tiers import Tier, TierConfig, get_tier_config, get_upgrade_path, list_tiers, TIER_CATALOGUE

BOT_FEATURES = {
    Tier.FREE.value: [
        "1 payment provider (Stripe)",
        "up to 3 affiliate niches",
        "1 digital product listing",
        "basic revenue tracking",
        "daily revenue summary",
    ],
    Tier.PRO.value: [
        "Stripe + PayPal payment providers",
        "up to 10 affiliate niches",
        "up to 10 digital product listings",
        "real estate deal finder (up to 3 markets)",
        "advanced revenue tracking",
        "detailed analytics & reports",
        "email revenue alerts",
        "automated product promotion",
    ],
    Tier.ENTERPRISE.value: [
        "all payment providers",
        "unlimited affiliate niches",
        "unlimited digital product listings",
        "real estate deal pipeline (unlimited markets)",
        "AI-optimized pricing engine",
        "full revenue orchestration",
        "custom revenue dashboards",
        "white-label storefronts",
        "API access",
        "dedicated account manager",
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
