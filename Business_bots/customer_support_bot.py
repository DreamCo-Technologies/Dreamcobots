"""
CustomerSupportBot — AI customer support bot.

Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.
"""

from __future__ import annotations
import sys, os
import random
from enum import Enum
from typing import Optional, List, Dict, Any

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from framework import GlobalAISourcesFlow  # noqa: F401


class CustomerSupportBotTierError(Exception):
    """Raised when a feature is not available on the current tier."""


class Tier(Enum):
    FREE = "free"
    PRO = "pro"
    ENTERPRISE = "enterprise"


TIER_MONTHLY_PRICE: Dict[str, int] = {"free": 0, "pro": 29, "enterprise": 99}


class CustomerSupportBot:
    """Tier-aware AI customer support bot."""

    # String-keyed to avoid cross-module enum identity issues
    RESULT_LIMITS: Dict[str, int] = {"free": 5, "pro": 25, "enterprise": 100}

    MOCK_DATA: List[Dict[str, Any]] = [{'id': 'BIZ001', 'name': 'Biz 1', 'sector': 'Tech', 'revenue_potential': 8500, 'startup_cost': 1800, 'score': 47.6, 'roi_pct': 13.2}, {'id': 'BIZ002', 'name': 'Biz 2', 'sector': 'Service', 'revenue_potential': 12000, 'startup_cost': 2600, 'score': 50.2, 'roi_pct': 14.4}, {'id': 'BIZ003', 'name': 'Biz 3', 'sector': 'Food', 'revenue_potential': 15500, 'startup_cost': 3400, 'score': 52.8, 'roi_pct': 15.6}, {'id': 'BIZ004', 'name': 'Biz 4', 'sector': 'Retail', 'revenue_potential': 19000, 'startup_cost': 4200, 'score': 55.4, 'roi_pct': 16.8}, {'id': 'BIZ005', 'name': 'Biz 5', 'sector': 'Tech', 'revenue_potential': 22500, 'startup_cost': 5000, 'score': 58.0, 'roi_pct': 18.0}, {'id': 'BIZ006', 'name': 'Biz 6', 'sector': 'Service', 'revenue_potential': 26000, 'startup_cost': 5800, 'score': 60.6, 'roi_pct': 19.2}, {'id': 'BIZ007', 'name': 'Biz 7', 'sector': 'Food', 'revenue_potential': 29500, 'startup_cost': 6600, 'score': 63.2, 'roi_pct': 20.4}, {'id': 'BIZ008', 'name': 'Biz 8', 'sector': 'Retail', 'revenue_potential': 33000, 'startup_cost': 7400, 'score': 65.8, 'roi_pct': 21.6}, {'id': 'BIZ009', 'name': 'Biz 9', 'sector': 'Tech', 'revenue_potential': 36500, 'startup_cost': 8200, 'score': 68.4, 'roi_pct': 22.8}, {'id': 'BIZ010', 'name': 'Biz 10', 'sector': 'Service', 'revenue_potential': 40000, 'startup_cost': 9000, 'score': 71.0, 'roi_pct': 24.0}, {'id': 'BIZ011', 'name': 'Biz 11', 'sector': 'Food', 'revenue_potential': 43500, 'startup_cost': 9800, 'score': 73.6, 'roi_pct': 25.2}, {'id': 'BIZ012', 'name': 'Biz 12', 'sector': 'Retail', 'revenue_potential': 47000, 'startup_cost': 10600, 'score': 76.2, 'roi_pct': 26.4}, {'id': 'BIZ013', 'name': 'Biz 13', 'sector': 'Tech', 'revenue_potential': 50500, 'startup_cost': 11400, 'score': 78.8, 'roi_pct': 27.6}, {'id': 'BIZ014', 'name': 'Biz 14', 'sector': 'Service', 'revenue_potential': 54000, 'startup_cost': 12200, 'score': 81.4, 'roi_pct': 28.8}, {'id': 'BIZ015', 'name': 'Biz 15', 'sector': 'Food', 'revenue_potential': 57500, 'startup_cost': 13000, 'score': 84.0, 'roi_pct': 30.0}, {'id': 'BIZ016', 'name': 'Biz 16', 'sector': 'Retail', 'revenue_potential': 61000, 'startup_cost': 13800, 'score': 86.6, 'roi_pct': 31.2}, {'id': 'BIZ017', 'name': 'Biz 17', 'sector': 'Tech', 'revenue_potential': 64500, 'startup_cost': 14600, 'score': 89.2, 'roi_pct': 32.4}, {'id': 'BIZ018', 'name': 'Biz 18', 'sector': 'Service', 'revenue_potential': 68000, 'startup_cost': 15400, 'score': 91.8, 'roi_pct': 33.6}, {'id': 'BIZ019', 'name': 'Biz 19', 'sector': 'Food', 'revenue_potential': 71500, 'startup_cost': 16200, 'score': 94.4, 'roi_pct': 34.8}, {'id': 'BIZ020', 'name': 'Biz 20', 'sector': 'Retail', 'revenue_potential': 75000, 'startup_cost': 17000, 'score': 97.0, 'roi_pct': 36.0}]

    def __init__(self, tier: Tier = Tier.FREE):
        # Normalize cross-module Tier enum instances by value string
        if isinstance(tier, Tier):
            self.tier = tier
        else:
            self.tier = Tier(getattr(tier, "value", str(tier)))
        self._usage_count = 0

    # ── Revenue helpers ──────────────────────────────────────────────────

    def monthly_price(self) -> int:
        """Return the monthly subscription price for the current tier."""
        return TIER_MONTHLY_PRICE[self.tier.value]

    def get_tier_info(self) -> Dict[str, Any]:
        """Return tier metadata."""
        return {
            "tier": self.tier.value,
            "monthly_price_usd": self.monthly_price(),
            "result_limit": self.RESULT_LIMITS[self.tier.value],
            "usage_count": self._usage_count,
        }

    def _enforce_tier(self, required_value: str) -> None:
        """Raise TierError if current tier is below required_value."""
        order = ["free", "pro", "enterprise"]
        if order.index(self.tier.value) < order.index(required_value):
            raise CustomerSupportBotTierError(
                f"{required_value.upper()} tier required. "
                f"Current tier: {self.tier.value}. Upgrade to unlock this feature."
            )

    def list_items(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Return a list of customer_support_bot items up to the tier limit."""
        self._usage_count += 1
        cap = limit if limit else self.RESULT_LIMITS[self.tier.value]
        sample = random.sample(self.MOCK_DATA, min(cap, len(self.MOCK_DATA)))
        return sample

    def get_top_item(self) -> Dict[str, Any]:
        """Return the highest-value customer_support_bot item."""
        self._usage_count += 1
        return max(self.MOCK_DATA, key=lambda x: x.get("score", 0))

    def analyze(self) -> Dict[str, Any]:
        """Run analysis and return summary statistics (PRO+)."""
        self._enforce_tier("pro")
        self._usage_count += 1
        values = [x.get("score", 0) for x in self.MOCK_DATA]
        return {
            "count": len(self.MOCK_DATA),
            "max_score": max(values),
            "min_score": min(values),
            "avg_score": round(sum(values) / len(values), 2),
        }

    def filter_by_score(self, min_score: float) -> List[Dict[str, Any]]:
        """Return items where score >= min_score (PRO+)."""
        self._enforce_tier("pro")
        self._usage_count += 1
        results = [x for x in self.MOCK_DATA if x.get("score", 0) >= min_score]
        return results[: self.RESULT_LIMITS[self.tier.value]]

    def export_report(self) -> Dict[str, Any]:
        """Generate a full report (ENTERPRISE only)."""
        self._enforce_tier("enterprise")
        self._usage_count += 1
        return {
            "bot": "CustomerSupportBot",
            "tier": self.tier.value,
            "total_items": len(self.MOCK_DATA),
            "items": self.MOCK_DATA,
            "generated_by": "GLOBAL AI SOURCES FLOW",
        }
