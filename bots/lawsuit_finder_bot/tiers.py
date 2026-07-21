"""
Tier configuration specific to the Lawsuit Finder Bot.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'ai-models-integration'))

from tiers import Tier, get_tier_config

LF_EXTRA_FEATURES: dict[str, list[str]] = {
    Tier.FREE.value: [
        "Public court case search",
        "Federal/state statute lookup",
        "Jurisdiction information",
        "Basic case summary",
    ],
    Tier.PRO.value: [
        "Class action lawsuit finder",
        "Settlement amount tracker",
        "Attorney & law firm matcher",
        "Case timeline visualizer",
        "Document checklist generator",
        "Email case alerts",
    ],
    Tier.ENTERPRISE.value: [
        "Deep litigation trend analytics",
        "PACER & LexisNexis API integration",
        "Predictive case outcome scoring",
        "Mass tort aggregation pipeline",
        "White-label legal research portal",
        "Dedicated legal research AI analyst",
    ],
}

LF_TOOLS: dict[str, list[str]] = {
    Tier.FREE.value: [
        "case_search",
        "statute_lookup",
        "jurisdiction_info",
    ],
    Tier.PRO.value: [
        "case_search",
        "statute_lookup",
        "jurisdiction_info",
        "class_action_finder",
        "settlement_tracker",
        "attorney_matcher",
        "case_alerts",
    ],
    Tier.ENTERPRISE.value: [
        "case_search",
        "statute_lookup",
        "jurisdiction_info",
        "class_action_finder",
        "settlement_tracker",
        "attorney_matcher",
        "case_alerts",
        "litigation_analytics",
        "pacer_integration",
        "outcome_predictor",
        "mass_tort_aggregator",
    ],
}


def get_lf_tier_info(tier: Tier) -> dict:
    """Return Lawsuit Finder Bot tier information as a dict."""
    cfg = get_tier_config(tier)
    return {
        "tier": tier.value,
        "name": cfg.name,
        "price_usd_monthly": cfg.price_usd_monthly,
        "requests_per_month": cfg.requests_per_month,
        "platform_features": cfg.features,
        "lf_features": LF_EXTRA_FEATURES[tier.value],
        "tools": LF_TOOLS[tier.value],
        "support_level": cfg.support_level,
    }
