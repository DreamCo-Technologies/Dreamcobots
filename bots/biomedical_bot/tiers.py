"""Tier definitions for the Biomedical Bot."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'ai-models-integration'))
from tiers import Tier, TierConfig, get_tier_config, get_upgrade_path, list_tiers, TIER_CATALOGUE

BOT_FEATURES = {
    Tier.FREE.value: [
        "1 patient monitored",
        "3 health metrics (heart rate, steps, sleep)",
        "basic heart rate monitoring",
        "step tracking",
        "daily health summary",
    ],
    Tier.PRO.value: [
        "20 patients monitored",
        "all health metrics",
        "continuous glucose monitoring",
        "blood pressure tracking",
        "SpO2 and respiratory rate",
        "anomaly detection and alerts",
        "7-day trend analysis",
        "basic disease marker screening",
        "personalized health reports",
    ],
    Tier.ENTERPRISE.value: [
        "unlimited patients",
        "all PRO features",
        "nanotech-assisted disease detection",
        "genomic / DNA sequence analysis",
        "ML-powered health predictions",
        "precision medicine engine",
        "personalized drug efficacy scoring",
        "full treatment plan generation",
        "bulk data export",
        "API access",
        "dedicated medical dashboard",
    ],
}


def get_bot_tier_info(tier: Tier) -> dict:
    cfg = get_tier_config(tier)
    return {
        "tier": tier.value,
        "name": cfg.name,
        "price_usd_monthly": cfg.price_usd_monthly,
        "requests_per_month": cfg.requests_per_month,
        "features": BOT_FEATURES[tier.value],
        "support_level": cfg.support_level,
    }
