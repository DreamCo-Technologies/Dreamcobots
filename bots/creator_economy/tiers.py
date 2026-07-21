"""
Tier configuration specific to the Creator Economy Bot.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'ai-models-integration'))

from tiers import Tier, get_tier_config

CE_EXTRA_FEATURES: dict[str, list[str]] = {
    Tier.FREE.value: [
        "Content idea generator (10/day)",
        "Hashtag & caption optimizer",
        "Social bio writer",
        "Platform growth tips",
    ],
    Tier.PRO.value: [
        "Brand sponsorship pitch deck",
        "Revenue dashboard (5 platforms)",
        "Merchandise store setup guide",
        "Fan membership tier designer",
        "Affiliate link tracker",
        "Cross-platform content repurposing",
    ],
    Tier.ENTERPRISE.value: [
        "Talent agency integration",
        "IP & copyright protection assistant",
        "Multi-platform deal negotiation support",
        "Long-form content production pipeline",
        "Community management automation",
        "Dedicated creator success manager",
    ],
}

CE_TOOLS: dict[str, list[str]] = {
    Tier.FREE.value: [
        "content_ideas",
        "hashtag_generator",
        "bio_optimizer",
    ],
    Tier.PRO.value: [
        "content_ideas",
        "hashtag_generator",
        "bio_optimizer",
        "brand_pitch_generator",
        "revenue_dashboard",
        "merch_store_setup",
        "affiliate_tracker",
    ],
    Tier.ENTERPRISE.value: [
        "content_ideas",
        "hashtag_generator",
        "bio_optimizer",
        "brand_pitch_generator",
        "revenue_dashboard",
        "merch_store_setup",
        "affiliate_tracker",
        "ip_protection",
        "talent_agency_sync",
        "deal_negotiator",
        "community_manager",
    ],
}


def get_ce_tier_info(tier: Tier) -> dict:
    """Return Creator Economy Bot tier information as a dict."""
    cfg = get_tier_config(tier)
    return {
        "tier": tier.value,
        "name": cfg.name,
        "price_usd_monthly": cfg.price_usd_monthly,
        "requests_per_month": cfg.requests_per_month,
        "platform_features": cfg.features,
        "ce_features": CE_EXTRA_FEATURES[tier.value],
        "tools": CE_TOOLS[tier.value],
        "support_level": cfg.support_level,
    }
