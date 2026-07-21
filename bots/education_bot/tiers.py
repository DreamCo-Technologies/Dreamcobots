"""Tier configuration for the Education Bot."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'ai-models-integration'))

from tiers import Tier, TierConfig, get_tier_config, get_upgrade_path, list_tiers

__all__ = ["Tier", "TierConfig", "get_tier_config", "get_upgrade_path", "list_tiers",
           "EDUCATION_FEATURES", "COURSE_LIMITS", "get_education_tier_info"]

EDUCATION_FEATURES: dict[str, list[str]] = {
    Tier.FREE.value: [
        "3 active courses",
        "Basic quiz generation",
        "Progress tracking",
    ],
    Tier.PRO.value: [
        "25 active courses",
        "Advanced assessments",
        "Certificate generation",
        "Student analytics",
        "Video lesson support",
    ],
    Tier.ENTERPRISE.value: [
        "Unlimited courses",
        "AI-powered tutoring",
        "Custom LMS integration",
        "Bulk enrollment",
        "Compliance reporting",
        "White-label branding",
    ],
}

COURSE_LIMITS: dict[str, int | None] = {
    Tier.FREE.value: 3,
    Tier.PRO.value: 25,
    Tier.ENTERPRISE.value: None,
}


def get_education_tier_info(tier: Tier) -> dict:
    """Return education-bot-specific tier information as a dict."""
    cfg = get_tier_config(tier)
    return {
        "tier": tier.value,
        "name": cfg.name,
        "price_usd_monthly": cfg.price_usd_monthly,
        "requests_per_month": cfg.requests_per_month,
        "support_level": cfg.support_level,
        "education_features": EDUCATION_FEATURES[tier.value],
        "course_limit": COURSE_LIMITS[tier.value],
    }
