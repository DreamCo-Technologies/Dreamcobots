"""
Tier configuration for the Dreamcobots CRM Automation Bot.
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
CRM_AUTOMATION_FEATURES: dict[str, list[str]] = {
    Tier.FREE.value: ["100 contacts", "basic pipeline", "email templates"],
    Tier.PRO.value: ["10,000 contacts", "advanced pipeline", "automated sequences", "integrations"],
    Tier.ENTERPRISE.value: ["unlimited contacts", "AI insights", "custom CRM integration", "team collaboration", "reporting"],
}


def get_crm_automation_tier_info(tier: Tier) -> dict:
    """Return bot-specific tier information as a dict."""
    cfg = get_tier_config(tier)
    return {
        "tier": tier.value,
        "name": cfg.name,
        "price_usd_monthly": cfg.price_usd_monthly,
        "requests_per_month": cfg.requests_per_month,
        "platform_features": cfg.features,
        "bot_features": CRM_AUTOMATION_FEATURES[tier.value],
        "support_level": cfg.support_level,
    }
