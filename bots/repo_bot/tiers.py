"""
Tier definitions for the RepoActivityTracker bot.
"""
from __future__ import annotations

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "ai-models-integration"))

from tiers import Tier  # noqa: E402

FEATURE_BASIC_TRACKING = "basic_tracking"
FEATURE_ISSUE_SCANNING = "issue_scanning"
FEATURE_PR_SCANNING = "pr_scanning"
FEATURE_FULL_HISTORY = "full_history"
FEATURE_AI_CATEGORIZATION = "ai_categorization"
FEATURE_EXPORT = "export"
FEATURE_WEBHOOKS = "webhooks"

FREE_FEATURES = [
    FEATURE_BASIC_TRACKING,
    FEATURE_ISSUE_SCANNING,
]

PRO_FEATURES = FREE_FEATURES + [
    FEATURE_PR_SCANNING,
    FEATURE_FULL_HISTORY,
    FEATURE_EXPORT,
]

ENTERPRISE_FEATURES = PRO_FEATURES + [
    FEATURE_AI_CATEGORIZATION,
    FEATURE_WEBHOOKS,
]

BOT_FEATURES = {
    Tier.FREE.value: FREE_FEATURES,
    Tier.PRO.value: PRO_FEATURES,
    Tier.ENTERPRISE.value: ENTERPRISE_FEATURES,
}

_TIER_PRICES = {
    Tier.FREE.value: 0.0,
    Tier.PRO.value: 29.0,
    Tier.ENTERPRISE.value: 99.0,
}


def get_bot_tier_info(tier: Tier) -> dict:
    """Return tier metadata for the RepoActivityTracker bot."""
    return {
        "tier": tier.value,
        "price_usd_monthly": _TIER_PRICES[tier.value],
        "features": BOT_FEATURES[tier.value],
    }
