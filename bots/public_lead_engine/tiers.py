"""
Tier configuration for the Public Lead Engine Bot.

Tiers:
  - FREE:             50 businesses/day, Google Places search, basic filtering.
  - PRO ($39):        1,000 businesses/day, Yelp + Google, rating filter, ad scoring.
  - ENTERPRISE ($149): Unlimited, multi-API, AI opportunity scoring, full outreach.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class Tier(Enum):
    FREE = "free"
    PRO = "pro"
    ENTERPRISE = "enterprise"


@dataclass
class TierConfig:
    name: str
    tier: Tier
    price_usd_monthly: float
    max_searches_per_day: Optional[int]
    features: list
    support_level: str

    def has_feature(self, feature: str) -> bool:
        return feature in self.features

    def is_unlimited(self) -> bool:
        return self.max_searches_per_day is None


# Feature constants
FEATURE_GOOGLE_PLACES_SEARCH = "google_places_search"
FEATURE_YELP_SEARCH = "yelp_search"
FEATURE_RATING_FILTER = "rating_filter"
FEATURE_WEAK_MARKETING_FILTER = "weak_marketing_filter"
FEATURE_AD_SCORE = "ad_score"
FEATURE_SCRIPT_GENERATION = "script_generation"
FEATURE_OUTREACH_DRAFT = "outreach_draft"
FEATURE_CRM_EXPORT = "crm_export"
FEATURE_MULTI_API = "multi_api"
FEATURE_AI_OPPORTUNITY_SCORE = "ai_opportunity_score"
FEATURE_BULK_SEARCH = "bulk_search"
FEATURE_ANALYTICS = "analytics"
FEATURE_WHITE_LABEL = "white_label"

FREE_FEATURES = [
    FEATURE_GOOGLE_PLACES_SEARCH,
    FEATURE_RATING_FILTER,
]

PRO_FEATURES = FREE_FEATURES + [
    FEATURE_YELP_SEARCH,
    FEATURE_WEAK_MARKETING_FILTER,
    FEATURE_AD_SCORE,
    FEATURE_SCRIPT_GENERATION,
    FEATURE_OUTREACH_DRAFT,
    FEATURE_CRM_EXPORT,
]

ENTERPRISE_FEATURES = PRO_FEATURES + [
    FEATURE_MULTI_API,
    FEATURE_AI_OPPORTUNITY_SCORE,
    FEATURE_BULK_SEARCH,
    FEATURE_ANALYTICS,
    FEATURE_WHITE_LABEL,
]

TIER_CATALOGUE = {
    Tier.FREE.value: TierConfig(
        name="Free",
        tier=Tier.FREE,
        price_usd_monthly=0.0,
        max_searches_per_day=50,
        features=FREE_FEATURES,
        support_level="Community",
    ),
    Tier.PRO.value: TierConfig(
        name="Pro",
        tier=Tier.PRO,
        price_usd_monthly=39.0,
        max_searches_per_day=1_000,
        features=PRO_FEATURES,
        support_level="Email (24 h SLA)",
    ),
    Tier.ENTERPRISE.value: TierConfig(
        name="Enterprise",
        tier=Tier.ENTERPRISE,
        price_usd_monthly=149.0,
        max_searches_per_day=None,
        features=ENTERPRISE_FEATURES,
        support_level="Dedicated 24/7",
    ),
}


def get_tier_config(tier: Tier) -> TierConfig:
    return TIER_CATALOGUE[tier.value]


def list_tiers() -> list:
    return [TIER_CATALOGUE[t.value] for t in Tier]


def get_upgrade_path(current: Tier) -> Optional[TierConfig]:
    order = list(Tier)
    idx = order.index(current)
    if idx + 1 < len(order):
        return get_tier_config(order[idx + 1])
    return None
