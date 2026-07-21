"""
Tier configuration for the Multi-Source Lead Scraper Bot.

Tiers:
  - FREE:        50 leads/day, 2 sources, basic filtering.
  - PRO ($49):   5,000 leads/day, 10 sources, enrichment, CRM export.
  - ENTERPRISE ($199): Unlimited leads, all sources, AI scoring, white-label.
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
    max_leads_per_day: Optional[int]
    max_sources: Optional[int]
    features: list
    support_level: str

    def has_feature(self, feature: str) -> bool:
        return feature in self.features

    def is_unlimited_leads(self) -> bool:
        return self.max_leads_per_day is None


FEATURE_BASIC_SCRAPING = "basic_scraping"
FEATURE_MULTI_SOURCE = "multi_source"
FEATURE_LEAD_ENRICHMENT = "lead_enrichment"
FEATURE_AI_SCORING = "ai_scoring"
FEATURE_CRM_EXPORT = "crm_export"
FEATURE_DEDUPLICATION = "deduplication"
FEATURE_EMAIL_VALIDATION = "email_validation"
FEATURE_PHONE_VALIDATION = "phone_validation"
FEATURE_LINKEDIN_SCRAPER = "linkedin_scraper"
FEATURE_TWITTER_SCRAPER = "twitter_scraper"
FEATURE_REDDIT_SCRAPER = "reddit_scraper"
FEATURE_GOOGLE_SCRAPER = "google_scraper"
FEATURE_YELP_SCRAPER = "yelp_scraper"
FEATURE_INDUSTRY_FILTER = "industry_filter"
FEATURE_WHITE_LABEL = "white_label"
FEATURE_WEBHOOK_EXPORT = "webhook_export"

FREE_FEATURES = [
    FEATURE_BASIC_SCRAPING,
    FEATURE_DEDUPLICATION,
    FEATURE_EMAIL_VALIDATION,
    FEATURE_GOOGLE_SCRAPER,
]

PRO_FEATURES = FREE_FEATURES + [
    FEATURE_MULTI_SOURCE,
    FEATURE_LEAD_ENRICHMENT,
    FEATURE_CRM_EXPORT,
    FEATURE_PHONE_VALIDATION,
    FEATURE_LINKEDIN_SCRAPER,
    FEATURE_TWITTER_SCRAPER,
    FEATURE_REDDIT_SCRAPER,
    FEATURE_YELP_SCRAPER,
    FEATURE_INDUSTRY_FILTER,
    FEATURE_WEBHOOK_EXPORT,
]

ENTERPRISE_FEATURES = PRO_FEATURES + [
    FEATURE_AI_SCORING,
    FEATURE_WHITE_LABEL,
]

TIER_CATALOGUE = {
    Tier.FREE.value: TierConfig(
        name="Free",
        tier=Tier.FREE,
        price_usd_monthly=0.0,
        max_leads_per_day=50,
        max_sources=2,
        features=FREE_FEATURES,
        support_level="Community",
    ),
    Tier.PRO.value: TierConfig(
        name="Pro",
        tier=Tier.PRO,
        price_usd_monthly=49.0,
        max_leads_per_day=5_000,
        max_sources=10,
        features=PRO_FEATURES,
        support_level="Email (24 h SLA)",
    ),
    Tier.ENTERPRISE.value: TierConfig(
        name="Enterprise",
        tier=Tier.ENTERPRISE,
        price_usd_monthly=199.0,
        max_leads_per_day=None,
        max_sources=None,
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
