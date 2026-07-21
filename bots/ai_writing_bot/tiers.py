"""
Tier configuration for the Dreamcobots AI Writing Bot.
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
AI_WRITING_FEATURES: dict[str, list[str]] = {
    Tier.FREE.value: ["5 templates", "1,000 words/month", "basic SEO"],
    Tier.PRO.value: ["50 templates", "50,000 words/month", "advanced SEO", "tone control", "plagiarism check"],
    Tier.ENTERPRISE.value: ["unlimited templates", "unlimited words", "brand voice training", "multi-language", "API access"],
}


def get_ai_writing_tier_info(tier: Tier) -> dict:
    """Return bot-specific tier information as a dict."""
    cfg = get_tier_config(tier)
    return {
        "tier": tier.value,
        "name": cfg.name,
        "price_usd_monthly": cfg.price_usd_monthly,
        "requests_per_month": cfg.requests_per_month,
        "platform_features": cfg.features,
        "bot_features": AI_WRITING_FEATURES[tier.value],
        "support_level": cfg.support_level,
    }
