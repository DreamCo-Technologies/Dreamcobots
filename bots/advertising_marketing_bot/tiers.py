"""
Tier configuration for the Advertising & Marketing Team Bot.

Tiers:
  - FREE:             Basic traffic generation, 100 leads/day, 1 campaign.
  - PRO ($49):        Advanced outreach, 5,000 leads/day, 10 campaigns, CRM export.
  - ENTERPRISE ($199): Unlimited leads, AI agents, full CRM, payment automation.
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
    max_campaigns: Optional[int]
    features: list
    support_level: str

    def has_feature(self, feature: str) -> bool:
        return feature in self.features

    def is_unlimited_leads(self) -> bool:
        return self.max_leads_per_day is None


FEATURE_TRAFFIC_GENERATION = "traffic_generation"
FEATURE_LEAD_SCRAPER = "lead_scraper"
FEATURE_LEAD_VALIDATOR = "lead_validator"
FEATURE_OUTREACH = "outreach"
FEATURE_FUNNEL = "funnel"
FEATURE_APPOINTMENT = "appointment"
FEATURE_CLOSE = "close"
FEATURE_PAYMENT = "payment"
FEATURE_CRM_INTEGRATION = "crm_integration"
FEATURE_AUTOMATION = "automation"
FEATURE_AI_AGENTS = "ai_agents"
FEATURE_ANALYTICS = "analytics"

FREE_FEATURES = [
    FEATURE_TRAFFIC_GENERATION,
    FEATURE_LEAD_SCRAPER,
    FEATURE_LEAD_VALIDATOR,
]

PRO_FEATURES = FREE_FEATURES + [
    FEATURE_OUTREACH,
    FEATURE_FUNNEL,
    FEATURE_APPOINTMENT,
    FEATURE_CLOSE,
    FEATURE_PAYMENT,
    FEATURE_CRM_INTEGRATION,
    FEATURE_ANALYTICS,
]

ENTERPRISE_FEATURES = PRO_FEATURES + [
    FEATURE_AUTOMATION,
    FEATURE_AI_AGENTS,
]

TIER_CATALOGUE = {
    Tier.FREE.value: TierConfig(
        name="Free",
        tier=Tier.FREE,
        price_usd_monthly=0.0,
        max_leads_per_day=100,
        max_campaigns=1,
        features=FREE_FEATURES,
        support_level="Community",
    ),
    Tier.PRO.value: TierConfig(
        name="Pro",
        tier=Tier.PRO,
        price_usd_monthly=49.0,
        max_leads_per_day=5_000,
        max_campaigns=10,
        features=PRO_FEATURES,
        support_level="Email (24 h SLA)",
    ),
    Tier.ENTERPRISE.value: TierConfig(
        name="Enterprise",
        tier=Tier.ENTERPRISE,
        price_usd_monthly=199.0,
        max_leads_per_day=None,
        max_campaigns=None,
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
