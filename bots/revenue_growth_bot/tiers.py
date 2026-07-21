"""Tier configuration for the Revenue Growth Bot."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'ai-models-integration'))

from tiers import Tier, TierConfig, get_tier_config, get_upgrade_path, list_tiers

__all__ = ["Tier", "TierConfig", "get_tier_config", "get_upgrade_path", "list_tiers",
           "REVENUE_FEATURES", "PRODUCT_LIMITS", "get_revenue_tier_info"]

REVENUE_FEATURES: dict[str, list[str]] = {
    Tier.FREE.value: [
        "Basic sales analytics",
        "Revenue tracking",
        "3 product listings",
    ],
    Tier.PRO.value: [
        "Advanced analytics",
        "Pricing optimization",
        "50 product listings",
        "Conversion funnel analysis",
        "A/B testing (2 variants)",
    ],
    Tier.ENTERPRISE.value: [
        "Unlimited products",
        "AI pricing engine",
        "Competitor analysis",
        "Revenue forecasting",
        "Custom dashboards",
        "CRM integration",
    ],
}

PRODUCT_LIMITS: dict[str, int | None] = {
    Tier.FREE.value: 3,
    Tier.PRO.value: 50,
    Tier.ENTERPRISE.value: None,
}


def get_revenue_tier_info(tier: Tier) -> dict:
    """Return revenue-bot-specific tier information as a dict."""
    cfg = get_tier_config(tier)
    return {
        "tier": tier.value,
        "name": cfg.name,
        "price_usd_monthly": cfg.price_usd_monthly,
        "requests_per_month": cfg.requests_per_month,
        "support_level": cfg.support_level,
        "revenue_features": REVENUE_FEATURES[tier.value],
        "product_limit": PRODUCT_LIMITS[tier.value],
    }
