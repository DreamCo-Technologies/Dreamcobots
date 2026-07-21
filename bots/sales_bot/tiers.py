"""
Tier configuration for the DreamCo Sales Bot.

Tiers:
  - FREE ($0):         Basic outreach (3 messages/day).
  - PRO ($99):         Full SMS + follow-up automation (20 messages/day).
  - ENTERPRISE ($299): Unlimited messages, voice bot, full conversion tracking.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class Tier(Enum):
    FREE = "free"
    PRO = "pro"
    ENTERPRISE = "enterprise"


FEATURE_SMS_OUTREACH = "sms_outreach"
FEATURE_FOLLOWUP_BOT = "followup_bot"
FEATURE_CONVERSION_TRACKING = "conversion_tracking"
FEATURE_VOICE_BOT = "voice_bot"
FEATURE_CRM_SYNC = "crm_sync"
FEATURE_REVENUE_TRACKING = "revenue_tracking"

FREE_FEATURES: list[str] = [FEATURE_SMS_OUTREACH]

PRO_FEATURES: list[str] = FREE_FEATURES + [
    FEATURE_FOLLOWUP_BOT,
    FEATURE_CONVERSION_TRACKING,
    FEATURE_REVENUE_TRACKING,
]

ENTERPRISE_FEATURES: list[str] = PRO_FEATURES + [
    FEATURE_VOICE_BOT,
    FEATURE_CRM_SYNC,
]


@dataclass
class TierConfig:
    name: str
    tier: Tier
    price_usd_monthly: float
    max_messages_per_day: Optional[int]
    features: list[str] = field(default_factory=list)
    support_level: str = "Community"

    def has_feature(self, feature: str) -> bool:
        return feature in self.features

    def is_unlimited(self) -> bool:
        return self.max_messages_per_day is None


TIER_CATALOGUE: dict[str, TierConfig] = {
    Tier.FREE.value: TierConfig(
        name="Free",
        tier=Tier.FREE,
        price_usd_monthly=0.0,
        max_messages_per_day=3,
        features=FREE_FEATURES,
        support_level="Community",
    ),
    Tier.PRO.value: TierConfig(
        name="Pro",
        tier=Tier.PRO,
        price_usd_monthly=99.0,
        max_messages_per_day=20,
        features=PRO_FEATURES,
        support_level="Email",
    ),
    Tier.ENTERPRISE.value: TierConfig(
        name="Enterprise",
        tier=Tier.ENTERPRISE,
        price_usd_monthly=299.0,
        max_messages_per_day=None,
        features=ENTERPRISE_FEATURES,
        support_level="Dedicated 24/7",
    ),
}


def get_tier_config(tier: Tier) -> TierConfig:
    return TIER_CATALOGUE[tier.value]


def list_tiers() -> list[TierConfig]:
    return [TIER_CATALOGUE[t.value] for t in Tier]


def get_upgrade_path(current: Tier) -> Optional[TierConfig]:
    order = list(Tier)
    idx = order.index(current)
    if idx + 1 < len(order):
        return get_tier_config(order[idx + 1])
    return None


BOT_FEATURES = {
    Tier.FREE.value: FREE_FEATURES,
    Tier.PRO.value: PRO_FEATURES,
    Tier.ENTERPRISE.value: ENTERPRISE_FEATURES,
}


def get_bot_tier_info(tier: Tier) -> dict:
    config = get_tier_config(tier)
    return {
        "tier": tier.value,
        "price_usd_monthly": config.price_usd_monthly,
        "features": BOT_FEATURES[tier.value],
    }
