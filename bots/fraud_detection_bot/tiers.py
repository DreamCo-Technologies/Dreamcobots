"""
Tier configuration for the Dreamcobots Fraud Detection Bot.
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
FRAUD_DETECTION_FEATURES: dict[str, list[str]] = {
    Tier.FREE.value: ["100 transactions/month", "rule-based detection", "basic alerts"],
    Tier.PRO.value: ["50,000 transactions/month", "ML detection", "real-time alerts", "custom rules"],
    Tier.ENTERPRISE.value: ["unlimited transactions", "advanced ML models", "behavioral analytics", "compliance reports", "API integration"],
}


def get_fraud_detection_tier_info(tier: Tier) -> dict:
    """Return bot-specific tier information as a dict."""
    cfg = get_tier_config(tier)
    return {
        "tier": tier.value,
        "name": cfg.name,
        "price_usd_monthly": cfg.price_usd_monthly,
        "requests_per_month": cfg.requests_per_month,
        "platform_features": cfg.features,
        "bot_features": FRAUD_DETECTION_FEATURES[tier.value],
        "support_level": cfg.support_level,
    }
