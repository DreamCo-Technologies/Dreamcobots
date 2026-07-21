"""
MortgageCalculatorBot — mortgage payment calculator.

Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.
"""

from __future__ import annotations
import sys, os
import random
from enum import Enum
from typing import Optional, List, Dict, Any

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from framework import GlobalAISourcesFlow  # noqa: F401


class MortgageCalculatorBotTierError(Exception):
    """Raised when a feature is not available on the current tier."""


class Tier(Enum):
    FREE = "free"
    PRO = "pro"
    ENTERPRISE = "enterprise"


TIER_MONTHLY_PRICE: Dict[str, int] = {"free": 0, "pro": 29, "enterprise": 99}


class MortgageCalculatorBot:
    """Tier-aware mortgage payment calculator."""

    # String-keyed to avoid cross-module enum identity issues
    RESULT_LIMITS: Dict[str, int] = {"free": 5, "pro": 25, "enterprise": 100}

    MOCK_DATA: List[Dict[str, Any]] = [{'id': 'RE001', 'address': '313 Pine', 'city': 'Dallas', 'state': 'TX', 'value': 168000, 'roi_pct': 4.9, 'score': 52.4, 'type': 'Condo'}, {'id': 'RE002', 'address': '326 Pine', 'city': 'Dallas', 'state': 'TX', 'value': 186000, 'roi_pct': 5.3, 'score': 54.8, 'type': 'Duplex'}, {'id': 'RE003', 'address': '339 Pine', 'city': 'Dallas', 'state': 'TX', 'value': 204000, 'roi_pct': 5.7, 'score': 57.2, 'type': 'Townhouse'}, {'id': 'RE004', 'address': '352 Pine', 'city': 'Dallas', 'state': 'TX', 'value': 222000, 'roi_pct': 6.1, 'score': 59.6, 'type': 'Land'}, {'id': 'RE005', 'address': '365 Pine', 'city': 'Dallas', 'state': 'TX', 'value': 240000, 'roi_pct': 6.5, 'score': 62.0, 'type': 'SFH'}, {'id': 'RE006', 'address': '378 Pine', 'city': 'Dallas', 'state': 'TX', 'value': 258000, 'roi_pct': 6.9, 'score': 64.4, 'type': 'Condo'}, {'id': 'RE007', 'address': '391 Pine', 'city': 'Dallas', 'state': 'TX', 'value': 276000, 'roi_pct': 7.3, 'score': 66.8, 'type': 'Duplex'}, {'id': 'RE008', 'address': '404 Pine', 'city': 'Dallas', 'state': 'TX', 'value': 294000, 'roi_pct': 7.7, 'score': 69.2, 'type': 'Townhouse'}, {'id': 'RE009', 'address': '417 Pine', 'city': 'Dallas', 'state': 'TX', 'value': 312000, 'roi_pct': 8.1, 'score': 71.6, 'type': 'Land'}, {'id': 'RE010', 'address': '430 Pine', 'city': 'Dallas', 'state': 'TX', 'value': 330000, 'roi_pct': 8.5, 'score': 74.0, 'type': 'SFH'}, {'id': 'RE011', 'address': '443 Pine', 'city': 'Dallas', 'state': 'TX', 'value': 348000, 'roi_pct': 8.9, 'score': 76.4, 'type': 'Condo'}, {'id': 'RE012', 'address': '456 Pine', 'city': 'Dallas', 'state': 'TX', 'value': 366000, 'roi_pct': 9.3, 'score': 78.8, 'type': 'Duplex'}, {'id': 'RE013', 'address': '469 Pine', 'city': 'Dallas', 'state': 'TX', 'value': 384000, 'roi_pct': 9.7, 'score': 81.2, 'type': 'Townhouse'}, {'id': 'RE014', 'address': '482 Pine', 'city': 'Dallas', 'state': 'TX', 'value': 402000, 'roi_pct': 10.1, 'score': 83.6, 'type': 'Land'}, {'id': 'RE015', 'address': '495 Pine', 'city': 'Dallas', 'state': 'TX', 'value': 420000, 'roi_pct': 10.5, 'score': 86.0, 'type': 'SFH'}, {'id': 'RE016', 'address': '508 Pine', 'city': 'Dallas', 'state': 'TX', 'value': 438000, 'roi_pct': 10.9, 'score': 88.4, 'type': 'Condo'}, {'id': 'RE017', 'address': '521 Pine', 'city': 'Dallas', 'state': 'TX', 'value': 456000, 'roi_pct': 11.3, 'score': 90.8, 'type': 'Duplex'}, {'id': 'RE018', 'address': '534 Pine', 'city': 'Dallas', 'state': 'TX', 'value': 474000, 'roi_pct': 11.7, 'score': 93.2, 'type': 'Townhouse'}, {'id': 'RE019', 'address': '547 Pine', 'city': 'Dallas', 'state': 'TX', 'value': 492000, 'roi_pct': 12.1, 'score': 95.6, 'type': 'Land'}, {'id': 'RE020', 'address': '560 Pine', 'city': 'Dallas', 'state': 'TX', 'value': 510000, 'roi_pct': 12.5, 'score': 98.0, 'type': 'SFH'}]

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
            raise MortgageCalculatorBotTierError(
                f"{required_value.upper()} tier required. "
                f"Current tier: {self.tier.value}. Upgrade to unlock this feature."
            )

    def list_items(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Return a list of mortgage_calculator_bot items up to the tier limit."""
        self._usage_count += 1
        cap = limit if limit else self.RESULT_LIMITS[self.tier.value]
        sample = random.sample(self.MOCK_DATA, min(cap, len(self.MOCK_DATA)))
        return sample

    def get_top_item(self) -> Dict[str, Any]:
        """Return the highest-value mortgage_calculator_bot item."""
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
            "bot": "MortgageCalculatorBot",
            "tier": self.tier.value,
            "total_items": len(self.MOCK_DATA),
            "items": self.MOCK_DATA,
            "generated_by": "GLOBAL AI SOURCES FLOW",
        }
