"""
Tier configuration for the DreamCo API Kit Bot.

Tiers:
  - FREE ($0/month):        1 API kit, 1 sandbox, 100 API calls/day, community support.
  - PRO ($49/month):        10 API kits, 5 sandboxes, 10,000 API calls/day, secret key
                            management, one-click deploy (3/month), analytics.
  - ENTERPRISE ($199/month): Unlimited kits/sandboxes/API calls, advanced sandbox isolation,
                              auto key expiration, one-click deploy unlimited, white-label,
                              Fortune 500 integrations, dedicated support.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class Tier(Enum):
    FREE = "free"
    PRO = "pro"
    ENTERPRISE = "enterprise"


# ---------------------------------------------------------------------------
# Feature flags
# ---------------------------------------------------------------------------

FEATURE_API_KIT_BASIC = "api_kit_basic"
FEATURE_SANDBOX_BASIC = "sandbox_basic"
FEATURE_SECRET_KEY_MANAGEMENT = "secret_key_management"
FEATURE_ONE_CLICK_DEPLOY = "one_click_deploy"
FEATURE_ANALYTICS = "analytics"
FEATURE_ADVANCED_SANDBOX = "advanced_sandbox"
FEATURE_AUTO_KEY_EXPIRATION = "auto_key_expiration"
FEATURE_WHITE_LABEL = "white_label"
FEATURE_FORTUNE500_INTEGRATIONS = "fortune500_integrations"
FEATURE_DEDICATED_SUPPORT = "dedicated_support"

FREE_FEATURES: list = [
    FEATURE_API_KIT_BASIC,
    FEATURE_SANDBOX_BASIC,
]

PRO_FEATURES: list = FREE_FEATURES + [
    FEATURE_SECRET_KEY_MANAGEMENT,
    FEATURE_ONE_CLICK_DEPLOY,
    FEATURE_ANALYTICS,
]

ENTERPRISE_FEATURES: list = PRO_FEATURES + [
    FEATURE_ADVANCED_SANDBOX,
    FEATURE_AUTO_KEY_EXPIRATION,
    FEATURE_WHITE_LABEL,
    FEATURE_FORTUNE500_INTEGRATIONS,
    FEATURE_DEDICATED_SUPPORT,
]


@dataclass
class TierConfig:
    """Configuration for a DreamCo API Kit Bot subscription tier."""

    name: str
    tier: Tier
    price_usd_monthly: float
    max_api_kits: Optional[int]
    max_sandboxes: Optional[int]
    max_api_calls_per_day: Optional[int]
    max_deployments_per_month: Optional[int]
    features: list
    support_level: str

    def has_feature(self, feature: str) -> bool:
        return feature in self.features

    def is_unlimited_kits(self) -> bool:
        return self.max_api_kits is None

    def is_unlimited_sandboxes(self) -> bool:
        return self.max_sandboxes is None

    def is_unlimited_api_calls(self) -> bool:
        return self.max_api_calls_per_day is None


TIER_CATALOGUE: dict = {
    Tier.FREE.value: TierConfig(
        name="Free",
        tier=Tier.FREE,
        price_usd_monthly=0.0,
        max_api_kits=1,
        max_sandboxes=1,
        max_api_calls_per_day=100,
        max_deployments_per_month=0,
        features=FREE_FEATURES,
        support_level="Community",
    ),
    Tier.PRO.value: TierConfig(
        name="Pro",
        tier=Tier.PRO,
        price_usd_monthly=49.0,
        max_api_kits=10,
        max_sandboxes=5,
        max_api_calls_per_day=10_000,
        max_deployments_per_month=3,
        features=PRO_FEATURES,
        support_level="Email (48 h SLA)",
    ),
    Tier.ENTERPRISE.value: TierConfig(
        name="Enterprise",
        tier=Tier.ENTERPRISE,
        price_usd_monthly=199.0,
        max_api_kits=None,
        max_sandboxes=None,
        max_api_calls_per_day=None,
        max_deployments_per_month=None,
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
