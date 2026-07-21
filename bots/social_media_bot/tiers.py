"""
Tier configuration for the Dreamcobots Social Media Bot.
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
SOCIAL_MEDIA_FEATURES: dict[str, list[str]] = {
    Tier.FREE.value: ["1 account", "10 posts/month", "basic analytics"],
    Tier.PRO.value: ["5 accounts", "200 posts/month", "scheduling", "hashtag optimization", "engagement tracking"],
    Tier.ENTERPRISE.value: ["unlimited accounts", "unlimited posts", "AI content generation", "influencer analytics", "API access"],
}


def get_social_media_tier_info(tier: Tier) -> dict:
    """Return bot-specific tier information as a dict."""
    cfg = get_tier_config(tier)
    return {
        "tier": tier.value,
        "name": cfg.name,
        "price_usd_monthly": cfg.price_usd_monthly,
        "requests_per_month": cfg.requests_per_month,
        "platform_features": cfg.features,
        "bot_features": SOCIAL_MEDIA_FEATURES[tier.value],
        "support_level": cfg.support_level,
    }
