"""
Tier configuration for the Government Contract & Grant Bot.
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
)

__all__ = ["Tier", "TierConfig", "get_tier_config", "get_upgrade_path", "list_tiers", "GOVBOT_FEATURES", "get_govbot_tier_info"]

GOVBOT_FEATURES: dict[str, list[str]] = {
    Tier.FREE.value: [
        "Contract search (basic)",
        "Grant eligibility check",
        "5 searches/day",
    ],
    Tier.PRO.value: [
        "Advanced contract search",
        "Grant application drafting",
        "SAM.gov integration",
        "100 searches/day",
    ],
    Tier.ENTERPRISE.value: [
        "Priority contract alerts",
        "Custom grant matching",
        "Compliance tracking",
        "Unlimited searches",
        "Dedicated contract specialist",
    ],
}


def get_govbot_tier_info(tier: Tier) -> dict:
    """Return government-bot-specific tier information as a dict."""
    cfg = get_tier_config(tier)
    return {
        "tier": tier.value,
        "name": cfg.name,
        "price_usd_monthly": cfg.price_usd_monthly,
        "requests_per_month": cfg.requests_per_month,
        "support_level": cfg.support_level,
        "govbot_features": GOVBOT_FEATURES[tier.value],
    }
