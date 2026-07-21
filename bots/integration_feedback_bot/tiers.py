"""
Tier configuration for the Integration Feedback Bot.

Tiers:
  - FREE ($0/mo):        Track up to 10 integrations, basic status logging.
  - PRO ($49/mo):        Unlimited tracking, Slack notifications, CSV export,
                          retry/auto-heal suggestions.
  - ENTERPRISE ($199/mo): All PRO features + webhook delivery, email alerts,
                            advanced analytics, dedicated support.
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
    """Configuration for an Integration Feedback Bot subscription tier."""

    name: str
    tier: Tier
    price_usd_monthly: float
    max_integrations: Optional[int]
    features: list
    support_level: str

    def has_feature(self, feature: str) -> bool:
        return feature in self.features

    def is_unlimited(self) -> bool:
        return self.max_integrations is None


# ---------------------------------------------------------------------------
# Feature flags
# ---------------------------------------------------------------------------

FEATURE_BASIC_TRACKING = "basic_tracking"
FEATURE_SLACK_NOTIFY = "slack_notify"
FEATURE_EXPORT_CSV = "export_csv"
FEATURE_AUTO_HEAL = "auto_heal"
FEATURE_WEBHOOK = "webhook"
FEATURE_EMAIL_ALERTS = "email_alerts"
FEATURE_ANALYTICS = "analytics"
FEATURE_DEDICATED_SUPPORT = "dedicated_support"

FREE_FEATURES: list = [
    FEATURE_BASIC_TRACKING,
]

PRO_FEATURES: list = FREE_FEATURES + [
    FEATURE_SLACK_NOTIFY,
    FEATURE_EXPORT_CSV,
    FEATURE_AUTO_HEAL,
    FEATURE_ANALYTICS,
]

ENTERPRISE_FEATURES: list = PRO_FEATURES + [
    FEATURE_WEBHOOK,
    FEATURE_EMAIL_ALERTS,
    FEATURE_DEDICATED_SUPPORT,
]

TIER_CATALOGUE: dict = {
    Tier.FREE.value: TierConfig(
        name="Free",
        tier=Tier.FREE,
        price_usd_monthly=0.0,
        max_integrations=10,
        features=FREE_FEATURES,
        support_level="Community",
    ),
    Tier.PRO.value: TierConfig(
        name="Pro",
        tier=Tier.PRO,
        price_usd_monthly=49.0,
        max_integrations=None,
        features=PRO_FEATURES,
        support_level="Email (24 h SLA)",
    ),
    Tier.ENTERPRISE.value: TierConfig(
        name="Enterprise",
        tier=Tier.ENTERPRISE,
        price_usd_monthly=199.0,
        max_integrations=None,
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
