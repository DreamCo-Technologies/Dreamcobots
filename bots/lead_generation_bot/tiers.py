"""
Tier configuration for the Dreamcobots Lead Generation Bot.
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
LEAD_GENERATION_FEATURES: dict[str, list[str]] = {
    Tier.FREE.value: ["50 leads/month", "basic scoring", "CSV export"],
    Tier.PRO.value: ["1,000 leads/month", "AI scoring", "CRM sync", "email sequences"],
    Tier.ENTERPRISE.value: ["unlimited leads", "predictive analytics", "A/B testing", "custom integrations"],
}


def get_lead_generation_tier_info(tier: Tier) -> dict:
    """Return bot-specific tier information as a dict."""
    cfg = get_tier_config(tier)
    return {
        "tier": tier.value,
        "name": cfg.name,
        "price_usd_monthly": cfg.price_usd_monthly,
        "requests_per_month": cfg.requests_per_month,
        "platform_features": cfg.features,
        "bot_features": LEAD_GENERATION_FEATURES[tier.value],
        "support_level": cfg.support_level,
    }
