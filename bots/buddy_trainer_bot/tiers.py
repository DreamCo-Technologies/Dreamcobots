"""
Tier configuration for the Buddy Trainer Bot.

Tiers:
  - FREE:           Conversational AI training guidance, basic human coaching,
                    5 AI training sessions/day, community datasets.
  - PRO ($49/mo):   Unlimited AI training sessions, robotics integration,
                    guided data-labeling workflows, version history, email support.
  - ENTERPRISE ($199/mo): Multi-model pipelines, advanced robotics adaptive loops,
                          white-label training environments, API access, priority support.
  - OWNER ($499 one-time): Personal GitHub-hosted Buddy bot system — full source,
                           datasets, and config; runtime ownership.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class Tier(Enum):
    FREE = "free"
    PRO = "pro"
    ENTERPRISE = "enterprise"
    OWNER = "owner"


@dataclass
class TierConfig:
    """Configuration for a Buddy Trainer subscription tier."""

    name: str
    tier: Tier
    price_usd_monthly: float
    price_usd_one_time: float          # non-zero for OWNER tier
    max_ai_sessions_per_day: Optional[int]   # None = unlimited
    max_robot_targets: Optional[int]         # None = unlimited
    max_human_learners: Optional[int]        # None = unlimited
    github_buddy_included: bool
    features: list
    support_level: str

    def has_feature(self, feature: str) -> bool:
        return feature in self.features

    def is_unlimited_sessions(self) -> bool:
        return self.max_ai_sessions_per_day is None


# ---------------------------------------------------------------------------
# Feature flags
# ---------------------------------------------------------------------------

FEATURE_AI_TRAINING = "ai_training"
FEATURE_AI_VERSIONING = "ai_versioning"
FEATURE_AI_DEPLOYMENT = "ai_deployment"
FEATURE_ROBOT_TRAINING = "robot_training"
FEATURE_ADAPTIVE_LOOPS = "adaptive_loops"
FEATURE_SENSOR_FEEDBACK = "sensor_feedback"
FEATURE_HUMAN_COACHING = "human_coaching"
FEATURE_DATA_LABELING = "data_labeling"
FEATURE_DATASET_MANAGEMENT = "dataset_management"
FEATURE_GUIDED_WORKFLOWS = "guided_workflows"
FEATURE_GITHUB_BUDDY = "github_buddy"
FEATURE_CUSTOM_DATASETS = "custom_datasets"
FEATURE_API_ACCESS = "api_access"
FEATURE_WHITE_LABEL = "white_label"
FEATURE_MULTI_MODEL = "multi_model"
FEATURE_PRIORITY_SUPPORT = "priority_support"
FEATURE_OWNERSHIP = "ownership"

FREE_FEATURES: list = [
    FEATURE_AI_TRAINING,
    FEATURE_HUMAN_COACHING,
    FEATURE_GUIDED_WORKFLOWS,
]

PRO_FEATURES: list = FREE_FEATURES + [
    FEATURE_AI_VERSIONING,
    FEATURE_AI_DEPLOYMENT,
    FEATURE_ROBOT_TRAINING,
    FEATURE_ADAPTIVE_LOOPS,
    FEATURE_DATA_LABELING,
    FEATURE_DATASET_MANAGEMENT,
    FEATURE_CUSTOM_DATASETS,
]

ENTERPRISE_FEATURES: list = PRO_FEATURES + [
    FEATURE_SENSOR_FEEDBACK,
    FEATURE_MULTI_MODEL,
    FEATURE_API_ACCESS,
    FEATURE_WHITE_LABEL,
    FEATURE_PRIORITY_SUPPORT,
]

OWNER_FEATURES: list = ENTERPRISE_FEATURES + [
    FEATURE_GITHUB_BUDDY,
    FEATURE_OWNERSHIP,
]

TIER_CATALOGUE: dict = {
    Tier.FREE.value: TierConfig(
        name="Free",
        tier=Tier.FREE,
        price_usd_monthly=0.0,
        price_usd_one_time=0.0,
        max_ai_sessions_per_day=5,
        max_robot_targets=0,
        max_human_learners=1,
        github_buddy_included=False,
        features=FREE_FEATURES,
        support_level="Community",
    ),
    Tier.PRO.value: TierConfig(
        name="Pro",
        tier=Tier.PRO,
        price_usd_monthly=49.0,
        price_usd_one_time=0.0,
        max_ai_sessions_per_day=None,
        max_robot_targets=10,
        max_human_learners=50,
        github_buddy_included=False,
        features=PRO_FEATURES,
        support_level="Email (24 h SLA)",
    ),
    Tier.ENTERPRISE.value: TierConfig(
        name="Enterprise",
        tier=Tier.ENTERPRISE,
        price_usd_monthly=199.0,
        price_usd_one_time=0.0,
        max_ai_sessions_per_day=None,
        max_robot_targets=None,
        max_human_learners=None,
        github_buddy_included=False,
        features=ENTERPRISE_FEATURES,
        support_level="Dedicated 24/7",
    ),
    Tier.OWNER.value: TierConfig(
        name="Owner",
        tier=Tier.OWNER,
        price_usd_monthly=0.0,
        price_usd_one_time=499.0,
        max_ai_sessions_per_day=None,
        max_robot_targets=None,
        max_human_learners=None,
        github_buddy_included=True,
        features=OWNER_FEATURES,
        support_level="Dedicated 24/7 + GitHub Runtime Control",
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
