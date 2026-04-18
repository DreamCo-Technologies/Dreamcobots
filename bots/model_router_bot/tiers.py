"""
Tier configuration for the Model Router Bot — DreamCo's AI routing brain.

Tiers:
  - FREE ($0/mo):         Task classification + basic routing (3 task types),
                          basic resource tools (email only), view-only analytics.
  - PRO ($97/mo):         Full routing (all 6 task types), all resource tools,
                          performance tracking, cost optimization hints.
  - ENTERPRISE ($297/mo): Unlimited routing, multi-agent communication,
                          API access, white-label, dedicated support.
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
    """Configuration for a Model Router Bot subscription tier.

    Attributes
    ----------
    name : str
        Human-readable tier name.
    tier : Tier
        Enum value.
    price_usd_monthly : float
        Monthly subscription price in USD.
    max_task_types : int | None
        Maximum distinct task types supported.  None = unlimited.
    max_tools : int | None
        Maximum resource tools accessible.  None = unlimited.
    features : list[str]
        Feature flags enabled on this tier.
    support_level : str
        Support offering description.
    """

    name: str
    tier: Tier
    price_usd_monthly: float
    max_task_types: Optional[int]
    max_tools: Optional[int]
    features: list
    support_level: str

    def has_feature(self, feature: str) -> bool:
        """Return True if *feature* is available on this tier."""
        return feature in self.features

    def is_unlimited_tasks(self) -> bool:
        """Return True if all task types are supported."""
        return self.max_task_types is None


# ---------------------------------------------------------------------------
# Feature flags
# ---------------------------------------------------------------------------

FEATURE_TASK_CLASSIFICATION = "task_classification"
FEATURE_MODEL_ROUTING = "model_routing"
FEATURE_RESOURCE_TOOLS = "resource_tools"
FEATURE_PERFORMANCE_TRACKING = "performance_tracking"
FEATURE_COST_OPTIMIZATION = "cost_optimization"
FEATURE_MULTI_AGENT = "multi_agent"
FEATURE_WHITE_LABEL = "white_label"
FEATURE_API_ACCESS = "api_access"
FEATURE_DEDICATED_SUPPORT = "dedicated_support"

FREE_FEATURES: list = [
    FEATURE_TASK_CLASSIFICATION,
    FEATURE_MODEL_ROUTING,
    FEATURE_RESOURCE_TOOLS,
]

PRO_FEATURES: list = FREE_FEATURES + [
    FEATURE_PERFORMANCE_TRACKING,
    FEATURE_COST_OPTIMIZATION,
]

ENTERPRISE_FEATURES: list = PRO_FEATURES + [
    FEATURE_MULTI_AGENT,
    FEATURE_WHITE_LABEL,
    FEATURE_API_ACCESS,
    FEATURE_DEDICATED_SUPPORT,
]

TIER_CATALOGUE: dict = {
    Tier.FREE.value: TierConfig(
        name="Free",
        tier=Tier.FREE,
        price_usd_monthly=0.0,
        max_task_types=3,
        max_tools=1,
        features=FREE_FEATURES,
        support_level="Community",
    ),
    Tier.PRO.value: TierConfig(
        name="Pro",
        tier=Tier.PRO,
        price_usd_monthly=97.0,
        max_task_types=None,
        max_tools=None,
        features=PRO_FEATURES,
        support_level="Email (24 h SLA)",
    ),
    Tier.ENTERPRISE.value: TierConfig(
        name="Enterprise",
        tier=Tier.ENTERPRISE,
        price_usd_monthly=297.0,
        max_task_types=None,
        max_tools=None,
        features=ENTERPRISE_FEATURES,
        support_level="Dedicated 24/7",
    ),
}


def get_tier_config(tier: Tier) -> TierConfig:
    """Return the TierConfig for *tier*."""
    return TIER_CATALOGUE[tier.value]


def list_tiers() -> list:
    """Return all TierConfig objects in tier order."""
    return [TIER_CATALOGUE[t.value] for t in Tier]


def get_upgrade_path(current: Tier) -> Optional[TierConfig]:
    """Return the next tier's config, or None if already at the top."""
    order = list(Tier)
    idx = order.index(current)
    if idx + 1 < len(order):
        return get_tier_config(order[idx + 1])
    return None
