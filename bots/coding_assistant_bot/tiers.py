"""
Tier configuration for the Dreamcobots Coding Assistant Bot.
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
CODING_ASSISTANT_FEATURES: dict[str, list[str]] = {
    Tier.FREE.value: ["3 languages", "basic completion", "bug detection"],
    Tier.PRO.value: ["20 languages", "advanced completion", "refactoring", "unit test generation", "code review"],
    Tier.ENTERPRISE.value: ["all languages", "custom model training", "team analytics", "IDE plugins", "priority support"],
}


def get_coding_assistant_tier_info(tier: Tier) -> dict:
    """Return bot-specific tier information as a dict."""
    cfg = get_tier_config(tier)
    return {
        "tier": tier.value,
        "name": cfg.name,
        "price_usd_monthly": cfg.price_usd_monthly,
        "requests_per_month": cfg.requests_per_month,
        "platform_features": cfg.features,
        "bot_features": CODING_ASSISTANT_FEATURES[tier.value],
        "support_level": cfg.support_level,
    }
