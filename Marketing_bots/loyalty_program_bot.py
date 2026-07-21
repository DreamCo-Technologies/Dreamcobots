"""
LoyaltyProgramBot — customer loyalty program manager.

Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.
"""

from __future__ import annotations
import sys, os
import random
from enum import Enum
from typing import Optional, List, Dict, Any

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from framework import GlobalAISourcesFlow  # noqa: F401


class LoyaltyProgramBotTierError(Exception):
    """Raised when a feature is not available on the current tier."""


class Tier(Enum):
    FREE = "free"
    PRO = "pro"
    ENTERPRISE = "enterprise"


TIER_MONTHLY_PRICE: Dict[str, int] = {"free": 0, "pro": 29, "enterprise": 99}


class LoyaltyProgramBot:
    """Tier-aware customer loyalty program manager."""

    # String-keyed to avoid cross-module enum identity issues
    RESULT_LIMITS: Dict[str, int] = {"free": 5, "pro": 25, "enterprise": 100}

    MOCK_DATA: List[Dict[str, Any]] = [{'id': 'MKT001', 'campaign': 'Campaign 1', 'channel': 'Social', 'reach': 900, 'clicks': 85, 'conversions': 8, 'score': 47.7, 'budget_usd': 175}, {'id': 'MKT002', 'campaign': 'Campaign 2', 'channel': 'SEO', 'reach': 1300, 'clicks': 120, 'conversions': 11, 'score': 50.4, 'budget_usd': 250}, {'id': 'MKT003', 'campaign': 'Campaign 3', 'channel': 'PPC', 'reach': 1700, 'clicks': 155, 'conversions': 14, 'score': 53.1, 'budget_usd': 325}, {'id': 'MKT004', 'campaign': 'Campaign 4', 'channel': 'Content', 'reach': 2100, 'clicks': 190, 'conversions': 17, 'score': 55.8, 'budget_usd': 400}, {'id': 'MKT005', 'campaign': 'Campaign 5', 'channel': 'Email', 'reach': 2500, 'clicks': 225, 'conversions': 20, 'score': 58.5, 'budget_usd': 475}, {'id': 'MKT006', 'campaign': 'Campaign 6', 'channel': 'Social', 'reach': 2900, 'clicks': 260, 'conversions': 23, 'score': 61.2, 'budget_usd': 550}, {'id': 'MKT007', 'campaign': 'Campaign 7', 'channel': 'SEO', 'reach': 3300, 'clicks': 295, 'conversions': 26, 'score': 63.9, 'budget_usd': 625}, {'id': 'MKT008', 'campaign': 'Campaign 8', 'channel': 'PPC', 'reach': 3700, 'clicks': 330, 'conversions': 29, 'score': 66.6, 'budget_usd': 700}, {'id': 'MKT009', 'campaign': 'Campaign 9', 'channel': 'Content', 'reach': 4100, 'clicks': 365, 'conversions': 32, 'score': 69.3, 'budget_usd': 775}, {'id': 'MKT010', 'campaign': 'Campaign 10', 'channel': 'Email', 'reach': 4500, 'clicks': 400, 'conversions': 35, 'score': 72.0, 'budget_usd': 850}, {'id': 'MKT011', 'campaign': 'Campaign 11', 'channel': 'Social', 'reach': 4900, 'clicks': 435, 'conversions': 38, 'score': 74.7, 'budget_usd': 925}, {'id': 'MKT012', 'campaign': 'Campaign 12', 'channel': 'SEO', 'reach': 5300, 'clicks': 470, 'conversions': 41, 'score': 77.4, 'budget_usd': 1000}, {'id': 'MKT013', 'campaign': 'Campaign 13', 'channel': 'PPC', 'reach': 5700, 'clicks': 505, 'conversions': 44, 'score': 80.1, 'budget_usd': 1075}, {'id': 'MKT014', 'campaign': 'Campaign 14', 'channel': 'Content', 'reach': 6100, 'clicks': 540, 'conversions': 47, 'score': 82.8, 'budget_usd': 1150}, {'id': 'MKT015', 'campaign': 'Campaign 15', 'channel': 'Email', 'reach': 6500, 'clicks': 575, 'conversions': 50, 'score': 85.5, 'budget_usd': 1225}, {'id': 'MKT016', 'campaign': 'Campaign 16', 'channel': 'Social', 'reach': 6900, 'clicks': 610, 'conversions': 53, 'score': 88.2, 'budget_usd': 1300}, {'id': 'MKT017', 'campaign': 'Campaign 17', 'channel': 'SEO', 'reach': 7300, 'clicks': 645, 'conversions': 56, 'score': 90.9, 'budget_usd': 1375}, {'id': 'MKT018', 'campaign': 'Campaign 18', 'channel': 'PPC', 'reach': 7700, 'clicks': 680, 'conversions': 59, 'score': 93.6, 'budget_usd': 1450}, {'id': 'MKT019', 'campaign': 'Campaign 19', 'channel': 'Content', 'reach': 8100, 'clicks': 715, 'conversions': 62, 'score': 96.3, 'budget_usd': 1525}, {'id': 'MKT020', 'campaign': 'Campaign 20', 'channel': 'Email', 'reach': 8500, 'clicks': 750, 'conversions': 65, 'score': 99.0, 'budget_usd': 1600}]

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
            raise LoyaltyProgramBotTierError(
                f"{required_value.upper()} tier required. "
                f"Current tier: {self.tier.value}. Upgrade to unlock this feature."
            )

    def list_items(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Return a list of loyalty_program_bot items up to the tier limit."""
        self._usage_count += 1
        cap = limit if limit else self.RESULT_LIMITS[self.tier.value]
        sample = random.sample(self.MOCK_DATA, min(cap, len(self.MOCK_DATA)))
        return sample

    def get_top_item(self) -> Dict[str, Any]:
        """Return the highest-value loyalty_program_bot item."""
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
            "bot": "LoyaltyProgramBot",
            "tier": self.tier.value,
            "total_items": len(self.MOCK_DATA),
            "items": self.MOCK_DATA,
            "generated_by": "GLOBAL AI SOURCES FLOW",
        }
