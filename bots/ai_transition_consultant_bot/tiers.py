"""
Tier definitions and access control for the AI Transition Consultant Bot.

Tiers:
  - FREE:       Basic AI readiness assessment, 3 consultations/month.
  - PRO:        Full assessment, solution recommendations, training modules, 30/month.
  - ENTERPRISE: Workflow integration, dedicated support, white-label, unlimited.
"""

from __future__ import annotations

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "ai-models-integration"))

from tiers import Tier, TierConfig, get_tier_config, get_upgrade_path, list_tiers, TIER_CATALOGUE  # noqa: F401


# Feature flags as string constants
FEATURE_BASIC_ASSESSMENT = "basic_assessment"
FEATURE_FULL_ASSESSMENT = "full_assessment"
FEATURE_SOLUTION_RECOMMENDATIONS = "solution_recommendations"
FEATURE_TRAINING_MODULES = "training_modules"
FEATURE_WORKFLOW_INTEGRATION = "workflow_integration"
FEATURE_DEDICATED_SUPPORT = "dedicated_support"
FEATURE_WHITE_LABEL = "white_label"
FEATURE_COMMERCIAL_RIGHTS = "commercial_rights"

FREE_FEATURES = [
    FEATURE_BASIC_ASSESSMENT,
]

PRO_FEATURES = FREE_FEATURES + [
    FEATURE_FULL_ASSESSMENT,
    FEATURE_SOLUTION_RECOMMENDATIONS,
    FEATURE_TRAINING_MODULES,
]

ENTERPRISE_FEATURES = PRO_FEATURES + [
    FEATURE_WORKFLOW_INTEGRATION,
    FEATURE_DEDICATED_SUPPORT,
    FEATURE_WHITE_LABEL,
    FEATURE_COMMERCIAL_RIGHTS,
]

BOT_FEATURES = {
    Tier.FREE.value: FREE_FEATURES,
    Tier.PRO.value: PRO_FEATURES,
    Tier.ENTERPRISE.value: ENTERPRISE_FEATURES,
}

# Monthly consultation limits
MONTHLY_LIMITS = {
    Tier.FREE.value: 3,
    Tier.PRO.value: 30,
    Tier.ENTERPRISE.value: None,  # unlimited
}

# Alias for backwards compatibility
DAILY_LIMITS = MONTHLY_LIMITS


def get_bot_tier_info(tier: Tier) -> dict:
    """Return a dict describing the AI Transition Consultant Bot's features for the given tier."""
    config = get_tier_config(tier)
    return {
        "tier": tier.value,
        "name": config.name,
        "price_usd_monthly": config.price_usd_monthly,
        "features": BOT_FEATURES[tier.value],
        "monthly_limit": MONTHLY_LIMITS[tier.value],
        "support_level": config.support_level,
        "commercial_rights": FEATURE_COMMERCIAL_RIGHTS in BOT_FEATURES[tier.value],
    }
