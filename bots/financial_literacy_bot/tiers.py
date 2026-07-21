"""
Tier configuration for the Financial Literacy Bot.

Tiers:
  - FREE:        Basic credit education, simple credit-score tips, 1 investment
                 calculator, community read-only access.
  - PRO ($29):   All free features + credit utilization alerts, OPM strategies,
                 multiple investment calculators, bank integration (mock/Plaid),
                 automated reminders, personalized education paths.
  - ENTERPRISE ($99): All pro features + full community platform (post/reply),
                 advanced analytics, white-label, priority support, Stripe billing
                 management.
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
    max_education_modules: Optional[int]
    max_investment_calculators: Optional[int]
    features: list
    support_level: str

    def has_feature(self, feature: str) -> bool:
        return feature in self.features

    def is_unlimited_modules(self) -> bool:
        return self.max_education_modules is None


# Feature flags
FEATURE_CREDIT_TIPS = "credit_tips"
FEATURE_CREDIT_ALERTS = "credit_alerts"
FEATURE_OPM_STRATEGIES = "opm_strategies"
FEATURE_INVESTMENT_CALCULATOR = "investment_calculator"
FEATURE_BANK_INTEGRATION = "bank_integration"
FEATURE_AUTOMATED_REMINDERS = "automated_reminders"
FEATURE_EDUCATION_PATHS = "education_paths"
FEATURE_COMMUNITY_READ = "community_read"
FEATURE_COMMUNITY_POST = "community_post"
FEATURE_ANALYTICS = "analytics"
FEATURE_WHITE_LABEL = "white_label"
FEATURE_STRIPE_BILLING = "stripe_billing"
FEATURE_PRODUCT_MATCHING = "product_matching"

FREE_FEATURES = [
    FEATURE_CREDIT_TIPS,
    FEATURE_INVESTMENT_CALCULATOR,
    FEATURE_COMMUNITY_READ,
]

PRO_FEATURES = FREE_FEATURES + [
    FEATURE_CREDIT_ALERTS,
    FEATURE_OPM_STRATEGIES,
    FEATURE_BANK_INTEGRATION,
    FEATURE_AUTOMATED_REMINDERS,
    FEATURE_EDUCATION_PATHS,
    FEATURE_PRODUCT_MATCHING,
]

ENTERPRISE_FEATURES = PRO_FEATURES + [
    FEATURE_COMMUNITY_POST,
    FEATURE_ANALYTICS,
    FEATURE_WHITE_LABEL,
    FEATURE_STRIPE_BILLING,
]

TIER_CATALOGUE = {
    Tier.FREE.value: TierConfig(
        name="Free",
        tier=Tier.FREE,
        price_usd_monthly=0.0,
        max_education_modules=3,
        max_investment_calculators=1,
        features=FREE_FEATURES,
        support_level="Community",
    ),
    Tier.PRO.value: TierConfig(
        name="Pro",
        tier=Tier.PRO,
        price_usd_monthly=29.0,
        max_education_modules=20,
        max_investment_calculators=10,
        features=PRO_FEATURES,
        support_level="Email (24 h SLA)",
    ),
    Tier.ENTERPRISE.value: TierConfig(
        name="Enterprise",
        tier=Tier.ENTERPRISE,
        price_usd_monthly=99.0,
        max_education_modules=None,
        max_investment_calculators=None,
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
