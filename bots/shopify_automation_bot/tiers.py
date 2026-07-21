"""
Tier configuration for the Dreamcobots Shopify Automation Bot.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'ai-models-integration'))

from tiers import (
    Tier,
    TierConfig,
    get_tier_config,
    get_upgrade_path,
    list_tiers,
    TIER_CATALOGUE,
)

# Bot-specific features per tier
SHOPIFY_AUTOMATION_FEATURES: dict[str, list[str]] = {
    Tier.FREE.value: ["1 store", "basic automation", "100 orders/month"],
    Tier.PRO.value: ["3 stores", "advanced automation", "10,000 orders/month", "inventory sync"],
    Tier.ENTERPRISE.value: ["unlimited stores", "custom workflows", "priority support", "API access", "bulk operations"],
}


def get_shopify_automation_tier_info(tier: Tier) -> dict:
    """Return bot-specific tier information as a dict."""
    cfg = get_tier_config(tier)
    return {
        "tier": tier.value,
        "name": cfg.name,
        "price_usd_monthly": cfg.price_usd_monthly,
        "requests_per_month": cfg.requests_per_month,
        "platform_features": cfg.features,
        "bot_features": SHOPIFY_AUTOMATION_FEATURES[tier.value],
        "support_level": cfg.support_level,
    }
