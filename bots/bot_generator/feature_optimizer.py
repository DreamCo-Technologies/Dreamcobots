"""
Auto-Bot Factory — Feature Optimizer Module

Uses competitor data and client input to prioritize high-impact features.
Adds DreamCo's proprietary optimizations (Auto-Upgrade, Adaptive Workflows).

Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.
"""

from __future__ import annotations

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from framework import GlobalAISourcesFlow  # noqa: F401  (GLOBAL AI SOURCES FLOW)

from typing import List, Optional
from bots.bot_generator.request_interface import BotRequest


# ---------------------------------------------------------------------------
# Feature Optimizer
# ---------------------------------------------------------------------------

class FeatureOptimizerError(Exception):
    """Raised when the optimizer cannot process the given input."""


# DreamCo proprietary optimizations always injected into generated bots
DREAMCO_CORE_OPTIMIZATIONS = [
    "Auto-Upgrade Engine",
    "Adaptive Workflows",
    "Self-Healing Error Recovery",
    "Performance Telemetry",
    "Revenue Tracking",
    "Safety Rate Limiter",
]

# High-impact features mapped to categories for intelligent injection
CATEGORY_FEATURE_MAP: dict = {
    "Lead Generation": [
        "multi-channel outreach",
        "lead scoring",
        "CRM integration",
        "follow-up automation",
        "conversion funnel tracking",
    ],
    "Sales Automation": [
        "deal pipeline management",
        "automated follow-ups",
        "SMS / voice outreach",
        "objection handling scripts",
        "revenue forecasting",
    ],
    "Customer Support": [
        "24/7 live chat",
        "ticket routing",
        "sentiment analysis",
        "knowledge base integration",
        "escalation management",
    ],
    "Data Scraping": [
        "rate-limit-aware scraping",
        "proxy rotation",
        "structured data extraction",
        "scheduled crawls",
        "deduplication",
    ],
    "Revenue Optimization": [
        "dynamic pricing",
        "upsell / cross-sell engine",
        "churn prediction",
        "A/B test framework",
        "ROI dashboard",
    ],
    "Marketing": [
        "campaign automation",
        "audience segmentation",
        "email sequences",
        "social media scheduling",
        "analytics dashboard",
    ],
    "Analytics": [
        "real-time dashboards",
        "KPI tracking",
        "anomaly detection",
        "predictive modelling",
        "exportable reports",
    ],
}

# Default high-impact features for uncategorised bots
DEFAULT_HIGH_IMPACT_FEATURES = [
    "authentication & access control",
    "API integration layer",
    "logging & monitoring",
    "data persistence",
    "error handling & retries",
]


class FeatureOptimizer:
    """
    DreamCo Auto-Bot Factory — Feature Optimizer.

    Merges client-requested features with DreamCo's proprietary optimizations
    and category-specific high-impact features to produce a ranked feature
    list ready for the :class:`~bots.bot_generator.code_generator.CodeGenerator`.

    Usage::

        optimizer = FeatureOptimizer()
        result = optimizer.optimize(request)
        print(result["optimized_features"])
    """

    def __init__(self, competitor_data: Optional[List[dict]] = None) -> None:
        self._competitor_data: List[dict] = competitor_data or []

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def optimize(self, request: BotRequest) -> dict:
        """
        Produce an optimized, ranked feature list for *request*.

        Parameters
        ----------
        request : BotRequest
            Validated bot creation request from :class:`RequestInterface`.

        Returns
        -------
        dict
            Keys: ``optimized_features``, ``dreamco_additions``,
            ``competitor_gaps``, ``priority_score``, ``category``.
        """
        if not request.features:
            raise FeatureOptimizerError("request.features must not be empty")

        client_features = list(request.features)
        category_features = self._get_category_features(request.category)
        competitor_gaps = self._extract_competitor_gaps(request.category)

        # Merge: client > category > competitor gaps (deduplicated)
        merged = self._deduplicate(
            client_features + category_features + competitor_gaps
        )

        # Always append DreamCo core optimizations at the end
        dreamco_additions = [
            f for f in DREAMCO_CORE_OPTIMIZATIONS if f not in merged
        ]

        optimized_features = merged + dreamco_additions
        priority_score = self._score(
            client_features, category_features, competitor_gaps
        )

        return {
            "category": request.category,
            "original_features": client_features,
            "optimized_features": optimized_features,
            "dreamco_additions": dreamco_additions,
            "competitor_gaps": competitor_gaps,
            "priority_score": priority_score,
            "total_features": len(optimized_features),
        }

    def set_competitor_data(self, data: List[dict]) -> None:
        """Update the competitor dataset used for gap analysis."""
        self._competitor_data = list(data)

    def list_dreamco_optimizations(self) -> List[str]:
        """Return DreamCo's proprietary optimization features."""
        return list(DREAMCO_CORE_OPTIMIZATIONS)

    def run(self) -> str:
        """GLOBAL AI SOURCES FLOW framework entry point."""
        return (
            f"FeatureOptimizer active — "
            f"{len(DREAMCO_CORE_OPTIMIZATIONS)} DreamCo optimizations available."
        )

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _get_category_features(self, category: str) -> List[str]:
        return list(
            CATEGORY_FEATURE_MAP.get(category, DEFAULT_HIGH_IMPACT_FEATURES)
        )

    def _extract_competitor_gaps(self, category: str) -> List[str]:
        """Return features missing from competitors for *category*."""
        gaps: List[str] = []
        for comp in self._competitor_data:
            if comp.get("category", "").lower() == category.lower():
                for gap in comp.get("weak_points", []):
                    if gap not in gaps:
                        gaps.append(gap)
        return gaps

    @staticmethod
    def _deduplicate(features: List[str]) -> List[str]:
        seen: set = set()
        result: List[str] = []
        for f in features:
            key = f.lower().strip()
            if key not in seen:
                seen.add(key)
                result.append(f)
        return result

    @staticmethod
    def _score(
        client: List[str],
        category: List[str],
        gaps: List[str],
    ) -> float:
        """Compute a priority score in [0, 1] based on feature overlap."""
        total = len(client) + len(category) + len(gaps)
        if total == 0:
            return 0.0
        overlap = len(set(f.lower() for f in client) & set(f.lower() for f in category))
        return round(min(1.0, (overlap + len(gaps)) / max(total, 1)), 4)
