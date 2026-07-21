"""
Tier configuration for the DreamCo SaaS Packages Bot.

Tiers:
  - FREE ($0/month):        1 SaaS package, basic templates, 1 user.
  - PRO ($49/month):        5 SaaS packages, advanced templates, 10 users,
                            CRM/E-commerce modules, usage analytics.
  - ENTERPRISE ($199/month): Unlimited packages, all industry modules,
                              unlimited users, custom SaaS builder,
                              Fortune 500 integrations, white-label,
                              API access, dedicated support.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class Tier(Enum):
    FREE = "free"
    PRO = "pro"
    ENTERPRISE = "enterprise"


@dataclass
class TierConfig:
    """Configuration for a DreamCo SaaS Packages Bot subscription tier."""

    name: str
    tier: Tier
    price_usd_monthly: float
    max_packages: Optional[int]
    max_users: Optional[int]
    features: list
    support_level: str

    def has_feature(self, feature: str) -> bool:
        return feature in self.features

    def is_unlimited_packages(self) -> bool:
        return self.max_packages is None

    def is_unlimited_users(self) -> bool:
        return self.max_users is None


# ---------------------------------------------------------------------------
# Feature flags
# ---------------------------------------------------------------------------

FEATURE_BASIC_PACKAGES = "basic_packages"
FEATURE_ADVANCED_TEMPLATES = "advanced_templates"
FEATURE_USAGE_ANALYTICS = "usage_analytics"
FEATURE_ECOMMERCE_MODULE = "ecommerce_module"
FEATURE_CRM_MODULE = "crm_module"
FEATURE_HR_MODULE = "hr_module"
FEATURE_CUSTOM_BUILDER = "custom_builder"
FEATURE_FORTUNE500_INTEGRATIONS = "fortune500_integrations"
FEATURE_WHITE_LABEL = "white_label"
FEATURE_API_ACCESS = "api_access"
FEATURE_DEDICATED_SUPPORT = "dedicated_support"

FREE_FEATURES: list = [
    FEATURE_BASIC_PACKAGES,
]

PRO_FEATURES: list = FREE_FEATURES + [
    FEATURE_ADVANCED_TEMPLATES,
    FEATURE_USAGE_ANALYTICS,
    FEATURE_ECOMMERCE_MODULE,
    FEATURE_CRM_MODULE,
]

ENTERPRISE_FEATURES: list = PRO_FEATURES + [
    FEATURE_HR_MODULE,
    FEATURE_CUSTOM_BUILDER,
    FEATURE_FORTUNE500_INTEGRATIONS,
    FEATURE_WHITE_LABEL,
    FEATURE_API_ACCESS,
    FEATURE_DEDICATED_SUPPORT,
]

TIER_CATALOGUE: dict = {
    Tier.FREE.value: TierConfig(
        name="Free",
        tier=Tier.FREE,
        price_usd_monthly=0.0,
        max_packages=1,
        max_users=1,
        features=FREE_FEATURES,
        support_level="Community",
    ),
    Tier.PRO.value: TierConfig(
        name="Pro",
        tier=Tier.PRO,
        price_usd_monthly=49.0,
        max_packages=5,
        max_users=10,
        features=PRO_FEATURES,
        support_level="Email (48 h SLA)",
    ),
    Tier.ENTERPRISE.value: TierConfig(
        name="Enterprise",
        tier=Tier.ENTERPRISE,
        price_usd_monthly=199.0,
        max_packages=None,
        max_users=None,
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
