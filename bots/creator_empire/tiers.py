"""
Tier configuration for the CreatorEmpire bot.

Reuses the platform-wide FREE / PRO / ENTERPRISE tiers and layers
creator-economy-specific feature flags on top.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'ai-models-integration'))

from tiers import (   # re-export for convenience
    Tier,
    TierConfig,
    get_tier_config,
    get_upgrade_path,
    list_tiers,
    TIER_CATALOGUE,
)

# ---------------------------------------------------------------------------
# Creator roles supported by the onboarding engine
# ---------------------------------------------------------------------------

CREATOR_ROLES = [
    "streamer",
    "rapper",
    "athlete",
    "artist",
    "content_creator",
    "podcaster",
    "comedian",
    "fitness_coach",
    "gamer",
    "dancer",
]

# ---------------------------------------------------------------------------
# Creator-economy feature flags per tier
# ---------------------------------------------------------------------------

FEATURE_BASIC_PROFILE = "basic_profile"
FEATURE_ROLE_ONBOARDING = "role_onboarding"
FEATURE_BRANDING_KIT = "branding_kit"
FEATURE_STREAM_SETUP = "stream_setup"
FEATURE_EVENT_PLANNER = "event_planner"
FEATURE_MONETIZATION_BASIC = "monetization_basic"
FEATURE_MONETIZATION_ADVANCED = "monetization_advanced"
FEATURE_SPONSORSHIP_TOOLS = "sponsorship_tools"
FEATURE_ANALYTICS_DASHBOARD = "analytics_dashboard"
FEATURE_CONTRACT_TEMPLATES = "contract_templates"
FEATURE_SOCIAL_AUTOMATION = "social_automation"
FEATURE_AI_BRANDING = "ai_branding"
FEATURE_COMMUNITY_TOOLS = "community_tools"
FEATURE_FINANCIAL_INFRA = "financial_infra"
FEATURE_WHITE_LABEL = "white_label"
FEATURE_CUSTOM_INTEGRATIONS = "custom_integrations"

FREE_CREATOR_FEATURES = [
    FEATURE_BASIC_PROFILE,
    FEATURE_ROLE_ONBOARDING,
    FEATURE_MONETIZATION_BASIC,
]

PRO_CREATOR_FEATURES = FREE_CREATOR_FEATURES + [
    FEATURE_BRANDING_KIT,
    FEATURE_STREAM_SETUP,
    FEATURE_EVENT_PLANNER,
    FEATURE_MONETIZATION_ADVANCED,
    FEATURE_ANALYTICS_DASHBOARD,
    FEATURE_CONTRACT_TEMPLATES,
    FEATURE_COMMUNITY_TOOLS,
]

ENTERPRISE_CREATOR_FEATURES = PRO_CREATOR_FEATURES + [
    FEATURE_SPONSORSHIP_TOOLS,
    FEATURE_SOCIAL_AUTOMATION,
    FEATURE_AI_BRANDING,
    FEATURE_FINANCIAL_INFRA,
    FEATURE_WHITE_LABEL,
    FEATURE_CUSTOM_INTEGRATIONS,
]

CREATOR_FEATURES_BY_TIER: dict[str, list[str]] = {
    Tier.FREE.value: FREE_CREATOR_FEATURES,
    Tier.PRO.value: PRO_CREATOR_FEATURES,
    Tier.ENTERPRISE.value: ENTERPRISE_CREATOR_FEATURES,
}

# ---------------------------------------------------------------------------
# Monetization models available per tier
# ---------------------------------------------------------------------------

MONETIZATION_MODELS_BY_TIER: dict[str, list[str]] = {
    Tier.FREE.value: ["tip_jar", "subscription_basic"],
    Tier.PRO.value: ["tip_jar", "subscription_basic", "subscription_premium",
                     "pay_per_view", "merchandise", "direct_service_fee"],
    Tier.ENTERPRISE.value: ["tip_jar", "subscription_basic", "subscription_premium",
                            "pay_per_view", "merchandise", "direct_service_fee",
                            "brand_deal", "licensing", "revenue_share", "nft"],
}


def get_creator_tier_info(tier: Tier) -> dict:
    """Return CreatorEmpire-specific tier information as a dict."""
    cfg = get_tier_config(tier)
    return {
        "tier": tier.value,
        "name": cfg.name,
        "price_usd_monthly": cfg.price_usd_monthly,
        "requests_per_month": cfg.requests_per_month,
        "platform_features": cfg.features,
        "creator_features": CREATOR_FEATURES_BY_TIER[tier.value],
        "monetization_models": MONETIZATION_MODELS_BY_TIER[tier.value],
        "support_level": cfg.support_level,
    }
