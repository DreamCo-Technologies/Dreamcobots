"""
Tier configuration for the Dreamcobots Customer Support Bot.
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
CUSTOMER_SUPPORT_FEATURES: dict[str, list[str]] = {
    Tier.FREE.value: ["3 support categories", "basic FAQ responses", "email handoff"],
    Tier.PRO.value: ["15 support categories", "sentiment analysis", "priority routing", "CRM integration"],
    Tier.ENTERPRISE.value: ["unlimited categories", "custom AI training", "white-label", "SLA guarantees", "API webhooks"],
}


def get_customer_support_tier_info(tier: Tier) -> dict:
    """Return bot-specific tier information as a dict."""
    cfg = get_tier_config(tier)
    return {
        "tier": tier.value,
        "name": cfg.name,
        "price_usd_monthly": cfg.price_usd_monthly,
        "requests_per_month": cfg.requests_per_month,
        "platform_features": cfg.features,
        "bot_features": CUSTOMER_SUPPORT_FEATURES[tier.value],
        "support_level": cfg.support_level,
    }
