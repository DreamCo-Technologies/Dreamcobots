"""
Tier configuration for the LegalMoneyBot.

Tiers:
  - FREE:          Basic claim discovery (public databases), 3 eligibility
                   questionnaire responses/month, basic settlement tips.
  - PRO ($49):     All free features + PACER/FTC dataset scanning, full
                   eligibility scoring, settlement maximizer AI, lawyer
                   matching, auto-filing assistance, referral tracking,
                   email notifications.
  - ENTERPRISE ($149): All pro features + bulk claim processing, dedicated
                   legal team routing, white-label, advanced analytics,
                   API access, priority support.
"""

from __future__ import annotations

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "ai-models-integration"))
from tiers import Tier, TierConfig, get_tier_config, get_upgrade_path, list_tiers  # noqa: F401

# ---------------------------------------------------------------------------
# Feature flags
# ---------------------------------------------------------------------------

FEATURE_CLAIM_FINDER = "claim_finder"
FEATURE_FTC_SCAN = "ftc_scan"
FEATURE_PACER_SCAN = "pacer_scan"
FEATURE_ELIGIBILITY_SCORING = "eligibility_scoring"
FEATURE_SMART_QUESTIONNAIRE = "smart_questionnaire"
FEATURE_SETTLEMENT_MAXIMIZER = "settlement_maximizer"
FEATURE_LAWYER_MATCHING = "lawyer_matching"
FEATURE_AUTO_FILING = "auto_filing"
FEATURE_REFERRAL_TRACKING = "referral_tracking"
FEATURE_NOTIFICATIONS = "notifications"
FEATURE_BULK_PROCESSING = "bulk_processing"
FEATURE_ANALYTICS = "analytics"
FEATURE_WHITE_LABEL = "white_label"
FEATURE_API_ACCESS = "api_access"

BOT_FEATURES = {
    Tier.FREE.value: [
        "basic claim discovery",
        "3 eligibility checks/month",
        "basic settlement guidance",
    ],
    Tier.PRO.value: [
        "PACER court record scanning",
        "FTC complaint dataset scanning",
        "unlimited eligibility scoring",
        "smart questionnaire",
        "settlement maximizer AI",
        "lawyer matching (contingency-based)",
        "auto-filing assistance",
        "referral tracking",
        "email notifications",
    ],
    Tier.ENTERPRISE.value: [
        "bulk claim processing",
        "dedicated legal team routing",
        "advanced analytics dashboard",
        "white-label deployment",
        "full API access",
        "priority 24/7 support",
    ],
}


def get_bot_tier_info(tier: Tier) -> dict:
    """Return a dict describing the tier features and pricing."""
    cfg = get_tier_config(tier)
    return {
        "tier": tier.value,
        "name": cfg.name,
        "price_usd_monthly": cfg.price_usd_monthly,
        "requests_per_month": cfg.requests_per_month,
        "features": BOT_FEATURES[tier.value],
        "support_level": cfg.support_level,
    }
