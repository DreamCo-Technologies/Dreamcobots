"""
Tier configuration for the DreamCo Stripe Key Rotation Bot.

Tiers:
  - STARTER:    Manual rotation trigger only, email notification.
  - GROWTH:     Scheduled rotation + Slack/email notifications.
  - ENTERPRISE: Fully autonomous rotation with audit trail and multi-channel alerts.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class Tier(Enum):
    STARTER = "starter"
    GROWTH = "growth"
    ENTERPRISE = "enterprise"


# ---------------------------------------------------------------------------
# Feature flags
# ---------------------------------------------------------------------------

FEATURE_MANUAL_ROTATION = "manual_rotation"
FEATURE_SCHEDULED_ROTATION = "scheduled_rotation"
FEATURE_GITHUB_SECRETS_UPDATE = "github_secrets_update"
FEATURE_EMAIL_NOTIFICATION = "email_notification"
FEATURE_SLACK_NOTIFICATION = "slack_notification"
FEATURE_AUDIT_TRAIL = "audit_trail"
FEATURE_KEY_VALIDATION = "key_validation"
FEATURE_OLD_KEY_DEACTIVATION = "old_key_deactivation"
FEATURE_PAYMENT_WORKFLOW_TEST = "payment_workflow_test"
FEATURE_MULTI_ENV_ROTATION = "multi_env_rotation"

STARTER_FEATURES = [
    FEATURE_MANUAL_ROTATION,
    FEATURE_KEY_VALIDATION,
    FEATURE_EMAIL_NOTIFICATION,
    FEATURE_GITHUB_SECRETS_UPDATE,
    FEATURE_PAYMENT_WORKFLOW_TEST,
]

GROWTH_FEATURES = STARTER_FEATURES + [
    FEATURE_SCHEDULED_ROTATION,
    FEATURE_SLACK_NOTIFICATION,
    FEATURE_AUDIT_TRAIL,
    FEATURE_OLD_KEY_DEACTIVATION,
]

ENTERPRISE_FEATURES = GROWTH_FEATURES + [
    FEATURE_MULTI_ENV_ROTATION,
]


@dataclass
class TierConfig:
    """Configuration for a Stripe Key Rotation Bot subscription tier."""

    name: str
    tier: Tier
    price_usd_monthly: float
    features: list = field(default_factory=list)
    support_level: str = "Community"
    # Days between automatic scheduled rotations; None means manual-only.
    # Used by the GitHub Actions workflow cron schedule.
    rotation_interval_days: Optional[int] = None

    def has_feature(self, feature: str) -> bool:
        return feature in self.features


TIER_CATALOGUE: dict[str, TierConfig] = {
    Tier.STARTER.value: TierConfig(
        name="Starter",
        tier=Tier.STARTER,
        price_usd_monthly=0.0,
        features=STARTER_FEATURES,
        support_level="Community",
        rotation_interval_days=None,
    ),
    Tier.GROWTH.value: TierConfig(
        name="Growth",
        tier=Tier.GROWTH,
        price_usd_monthly=29.0,
        features=GROWTH_FEATURES,
        support_level="Email (24 h SLA)",
        rotation_interval_days=30,
    ),
    Tier.ENTERPRISE.value: TierConfig(
        name="Enterprise",
        tier=Tier.ENTERPRISE,
        price_usd_monthly=99.0,
        features=ENTERPRISE_FEATURES,
        support_level="Dedicated 24/7",
        rotation_interval_days=7,
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
