"""
Tier configuration for the Automation Bot.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'ai-models-integration'))

from tiers import Tier, TierConfig, get_tier_config, get_upgrade_path, list_tiers

__all__ = ["Tier", "TierConfig", "get_tier_config", "get_upgrade_path", "list_tiers",
           "AUTOMATION_FEATURES", "TASK_LIMITS", "get_automation_tier_info"]

AUTOMATION_FEATURES: dict[str, list[str]] = {
    Tier.FREE.value: [
        "5 scheduled tasks",
        "Basic triggers (time-based)",
        "Email notifications",
    ],
    Tier.PRO.value: [
        "100 scheduled tasks",
        "Advanced triggers (webhook, event-based)",
        "Multi-step workflows",
        "Slack/Teams notifications",
        "Retry logic",
    ],
    Tier.ENTERPRISE.value: [
        "Unlimited tasks",
        "Custom trigger types",
        "Parallel workflow execution",
        "Audit logging",
        "SLA monitoring",
        "Priority queue",
    ],
}

TASK_LIMITS: dict[str, int | None] = {
    Tier.FREE.value: 5,
    Tier.PRO.value: 100,
    Tier.ENTERPRISE.value: None,  # unlimited
}


def get_automation_tier_info(tier: Tier) -> dict:
    """Return automation-bot-specific tier information as a dict."""
    cfg = get_tier_config(tier)
    return {
        "tier": tier.value,
        "name": cfg.name,
        "price_usd_monthly": cfg.price_usd_monthly,
        "requests_per_month": cfg.requests_per_month,
        "support_level": cfg.support_level,
        "automation_features": AUTOMATION_FEATURES[tier.value],
        "task_limit": TASK_LIMITS[tier.value],
    }
