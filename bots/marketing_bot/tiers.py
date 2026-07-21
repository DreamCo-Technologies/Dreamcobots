"""
Tier configuration specific to the Marketing Bot.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'ai-models-integration'))

from tiers import Tier, get_tier_config

MARKETING_EXTRA_FEATURES: dict[str, list[str]] = {
    Tier.FREE.value: [
        "Social media post drafts (5/day)",
        "Basic SEO keyword suggestions",
        "Email subject line generator",
        "Hashtag recommendations",
    ],
    Tier.PRO.value: [
        "Multi-channel campaign builder",
        "A/B test copy variants",
        "Content calendar (30-day)",
        "Analytics dashboard integration",
        "Email sequence automation",
        "Paid ads copy generator",
    ],
    Tier.ENTERPRISE.value: [
        "Full-funnel campaign orchestration",
        "Influencer matching & outreach",
        "Brand voice customization",
        "Multi-brand white-label deployment",
        "Advanced attribution reporting",
        "Dedicated marketing strategist AI",
    ],
}

MARKETING_CHANNELS: dict[str, list[str]] = {
    Tier.FREE.value: [
        "social_media",
        "email_marketing",
        "seo",
    ],
    Tier.PRO.value: [
        "social_media",
        "email_marketing",
        "seo",
        "paid_ads",
        "content_calendar",
        "ab_testing",
    ],
    Tier.ENTERPRISE.value: [
        "social_media",
        "email_marketing",
        "seo",
        "paid_ads",
        "content_calendar",
        "ab_testing",
        "influencer",
        "brand_voice",
        "attribution_reporting",
        "full_funnel_orchestration",
    ],
}


def get_marketing_tier_info(tier: Tier) -> dict:
    """Return Marketing Bot tier information as a dict."""
    cfg = get_tier_config(tier)
    return {
        "tier": tier.value,
        "name": cfg.name,
        "price_usd_monthly": cfg.price_usd_monthly,
        "requests_per_month": cfg.requests_per_month,
        "platform_features": cfg.features,
        "marketing_features": MARKETING_EXTRA_FEATURES[tier.value],
        "channels": MARKETING_CHANNELS[tier.value],
        "support_level": cfg.support_level,
    }
