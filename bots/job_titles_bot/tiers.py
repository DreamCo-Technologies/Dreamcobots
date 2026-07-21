"""
Job Titles Bot — Tier Definitions

Tiers:
  FREE       — Browse 50 job titles, basic bot templates, read-only.
  PRO        — Full 1 000+ job titles, custom bot generation, item valuation.
  ENTERPRISE — Unlimited titles, AI-powered training, face/object recognition,
               autonomous cost justification, marketplace hiring, white-label.
"""

import sys
import os

# Re-use the shared Tier / TierConfig definitions from ai-models-integration
_AI_MODELS_DIR = os.path.join(os.path.dirname(__file__), "..", "ai-models-integration")
if _AI_MODELS_DIR not in sys.path:
    sys.path.insert(0, _AI_MODELS_DIR)

from tiers import Tier, TierConfig, get_tier_config, get_upgrade_path  # noqa: E402


# ---------------------------------------------------------------------------
# Bot-level feature catalogue
# ---------------------------------------------------------------------------

BOT_FEATURES: dict[str, list[str]] = {
    Tier.FREE.value: [
        "Browse 50 job titles",
        "3 industry categories",
        "Basic bot templates (read-only)",
        "Job description lookup",
        "Community support",
    ],
    Tier.PRO.value: [
        "Full 1,000+ job titles",
        "25+ industry categories",
        "Custom bot generation per job role",
        "Hire human or AI worker matching",
        "Item valuation (antiques, coins, currency)",
        "Autonomous cost justification",
        "Token-based or subscription billing",
        "Priority email support",
    ],
    Tier.ENTERPRISE.value: [
        "Unlimited job titles + custom additions",
        "All industry categories",
        "AI-powered workforce automation",
        "Face & object recognition training",
        "Buddy Bot propagation (universal upgrades)",
        "Robot contract sourcing",
        "White-label marketplace deployment",
        "Full API access",
        "Dedicated account manager",
    ],
}


def get_bot_tier_info(tier: Tier) -> dict:
    """Return a dict describing *tier* capabilities for the Job Titles Bot."""
    cfg = get_tier_config(tier)
    return {
        "tier": tier.value,
        "name": cfg.name,
        "price_usd_monthly": cfg.price_usd_monthly,
        "requests_per_month": cfg.requests_per_month,
        "features": BOT_FEATURES[tier.value],
        "support_level": cfg.support_level,
    }


__all__ = [
    "Tier",
    "TierConfig",
    "get_tier_config",
    "get_upgrade_path",
    "BOT_FEATURES",
    "get_bot_tier_info",
]
