import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "ai-models-integration"))
from tiers import Tier, TierConfig, get_tier_config, get_upgrade_path, list_tiers, TIER_CATALOGUE  # noqa: E402

BOT_FEATURES = {
    Tier.FREE.value: [
        "lead_capture",
        "buy_listings",
        "rent_listings",
        "stripe_payment",
        "interaction_log",
    ],
    Tier.PRO.value: [
        "lead_capture",
        "buy_listings",
        "rent_listings",
        "off_market_deals",
        "stripe_payment",
        "paypal_payment",
        "lead_scoring",
        "crm_export",
        "interaction_log",
        "revenue_analytics",
    ],
    Tier.ENTERPRISE.value: [
        "lead_capture",
        "buy_listings",
        "rent_listings",
        "off_market_deals",
        "stripe_payment",
        "paypal_payment",
        "lead_scoring",
        "crm_export",
        "interaction_log",
        "revenue_analytics",
        "auto_followup",
        "multi_market",
        "api_access",
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
