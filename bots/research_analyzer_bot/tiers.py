"""
Tier definitions and access control for the Research Analyzer Bot.

Tiers:
  - FREE:       Basic search, summarization, 100-page limit, 20 queries/day.
  - PRO:        Semantic search, Q&A engine, 1000-page limit, 500 queries/day.
  - ENTERPRISE: Large corpus indexing, data synthesis, automation, unlimited.
"""

from __future__ import annotations

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "ai-models-integration"))

from tiers import Tier, TierConfig, get_tier_config, get_upgrade_path, list_tiers, TIER_CATALOGUE  # noqa: F401


# Feature flags as string constants
FEATURE_BASIC_SEARCH = "basic_search"
FEATURE_SUMMARIZATION = "summarization"
FEATURE_PAGE_LIMIT_100 = "page_limit_100"
FEATURE_SEMANTIC_SEARCH = "semantic_search"
FEATURE_QA_ENGINE = "qa_engine"
FEATURE_PAGE_LIMIT_1000 = "page_limit_1000"
FEATURE_LARGE_CORPUS_INDEXING = "large_corpus_indexing"
FEATURE_DATA_SYNTHESIS = "data_synthesis"
FEATURE_AUTOMATION = "automation"
FEATURE_COMMERCIAL_RIGHTS = "commercial_rights"

FREE_FEATURES = [
    FEATURE_BASIC_SEARCH,
    FEATURE_SUMMARIZATION,
    FEATURE_PAGE_LIMIT_100,
]

PRO_FEATURES = FREE_FEATURES + [
    FEATURE_SEMANTIC_SEARCH,
    FEATURE_QA_ENGINE,
    FEATURE_PAGE_LIMIT_1000,
]

ENTERPRISE_FEATURES = PRO_FEATURES + [
    FEATURE_LARGE_CORPUS_INDEXING,
    FEATURE_DATA_SYNTHESIS,
    FEATURE_AUTOMATION,
    FEATURE_COMMERCIAL_RIGHTS,
]

BOT_FEATURES = {
    Tier.FREE.value: FREE_FEATURES,
    Tier.PRO.value: PRO_FEATURES,
    Tier.ENTERPRISE.value: ENTERPRISE_FEATURES,
}

DAILY_LIMITS = {
    Tier.FREE.value: 20,
    Tier.PRO.value: 500,
    Tier.ENTERPRISE.value: None,  # unlimited
}


def get_bot_tier_info(tier: Tier) -> dict:
    """Return a dict describing the Research Analyzer Bot's features for the given tier."""
    config = get_tier_config(tier)
    return {
        "tier": tier.value,
        "name": config.name,
        "price_usd_monthly": config.price_usd_monthly,
        "features": BOT_FEATURES[tier.value],
        "daily_limit": DAILY_LIMITS[tier.value],
        "support_level": config.support_level,
        "commercial_rights": FEATURE_COMMERCIAL_RIGHTS in BOT_FEATURES[tier.value],
    }
