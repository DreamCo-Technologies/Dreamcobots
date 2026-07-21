"""
Auto-Bot Factory — Competitor Analyzer Module

Extracts feature lists, user ratings, pricing, and reviews from similar
systems (SaaS / apps / bots).  Detects weak points and competitive gaps.
Results are saved to data/competitors.json for use by FeatureOptimizer.

Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.
"""

from __future__ import annotations

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from framework import GlobalAISourcesFlow  # noqa: F401  (GLOBAL AI SOURCES FLOW)

import json
from datetime import datetime, timezone
from typing import List, Optional


# ---------------------------------------------------------------------------
# Competitor data model
# ---------------------------------------------------------------------------

def _default_data_path() -> str:
    return os.path.join(
        os.path.dirname(__file__), "..", "..", "data", "competitors.json"
    )


# Simulated competitor database used when live scraping is unavailable
SIMULATED_COMPETITORS: List[dict] = [
    {
        "name": "LeadBot Pro",
        "category": "Lead Generation",
        "rating": 3.8,
        "monthly_price_usd": 149,
        "features": ["email outreach", "basic CRM", "lead import"],
        "weak_points": ["no SMS", "no follow-up automation", "poor analytics"],
        "reviews_summary": "Works for basic email campaigns but lacks automation depth.",
        "source": "simulated",
    },
    {
        "name": "SalesFlow AI",
        "category": "Sales Automation",
        "rating": 4.1,
        "monthly_price_usd": 199,
        "features": ["pipeline management", "email sequences", "basic reporting"],
        "weak_points": ["no voice outreach", "limited integrations", "no revenue forecasting"],
        "reviews_summary": "Good pipeline UX but weak on integrations and reporting.",
        "source": "simulated",
    },
    {
        "name": "SupportDesk Lite",
        "category": "Customer Support",
        "rating": 3.5,
        "monthly_price_usd": 79,
        "features": ["live chat", "basic ticketing"],
        "weak_points": ["no sentiment analysis", "no escalation management", "no 24/7 SLA"],
        "reviews_summary": "Cheap but limited.  Falls apart at scale.",
        "source": "simulated",
    },
    {
        "name": "DataHarvest",
        "category": "Data Scraping",
        "rating": 4.0,
        "monthly_price_usd": 99,
        "features": ["web scraping", "export to CSV"],
        "weak_points": ["no proxy rotation", "rate limits hit frequently", "no deduplication"],
        "reviews_summary": "Fast but unreliable on large scrapes.",
        "source": "simulated",
    },
    {
        "name": "RevenueMax",
        "category": "Revenue Optimization",
        "rating": 3.9,
        "monthly_price_usd": 299,
        "features": ["pricing dashboard", "basic upsell prompts"],
        "weak_points": ["no A/B testing", "no churn prediction", "no ROI breakdown"],
        "reviews_summary": "Decent dashboard but lacks predictive tools.",
        "source": "simulated",
    },
    {
        "name": "MarketPulse",
        "category": "Marketing",
        "rating": 4.2,
        "monthly_price_usd": 129,
        "features": ["email campaigns", "social posting", "basic analytics"],
        "weak_points": ["no audience segmentation", "no dynamic content", "no A/B testing"],
        "reviews_summary": "Easy to use but too basic for serious marketers.",
        "source": "simulated",
    },
]


# ---------------------------------------------------------------------------
# Competitor Analyzer
# ---------------------------------------------------------------------------

class CompetitorAnalyzerError(Exception):
    """Raised when analysis cannot be completed."""


class CompetitorAnalyzer:
    """
    DreamCo Auto-Bot Factory — Competitor Analyzer.

    Analyses competing products in a given category to surface feature
    gaps, pricing benchmarks, and quality weaknesses that DreamCo bots
    can exploit.

    Data is persisted to ``data/competitors.json`` so the
    :class:`~bots.bot_generator.feature_optimizer.FeatureOptimizer` can
    consume it without a live scrape.

    Usage::

        analyzer = CompetitorAnalyzer()
        report = analyzer.analyze(category="Lead Generation")
        print(report["gaps"])
    """

    def __init__(
        self,
        data_path: Optional[str] = None,
        simulated: bool = True,
    ) -> None:
        self._data_path = os.path.abspath(data_path or _default_data_path())
        self._simulated = simulated
        self._competitors: List[dict] = []
        self._load()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def analyze(self, category: str) -> dict:
        """
        Analyse competitors in *category* and return an insight report.

        Parameters
        ----------
        category : str
            Bot category to analyse (e.g. "Lead Generation").

        Returns
        -------
        dict
            Keys: ``category``, ``competitors``, ``avg_rating``,
            ``avg_price_usd``, ``gaps``, ``pricing_benchmark``.
        """
        if not category.strip():
            raise CompetitorAnalyzerError("category must not be empty")

        matches = self._fetch(category)
        if not matches:
            return {
                "category": category,
                "competitors": [],
                "avg_rating": 0.0,
                "avg_price_usd": 0.0,
                "gaps": [],
                "pricing_benchmark": {},
                "analyzed_at": datetime.now(timezone.utc).isoformat(),
            }

        ratings = [c["rating"] for c in matches if "rating" in c]
        prices = [c["monthly_price_usd"] for c in matches if "monthly_price_usd" in c]

        all_gaps: List[str] = []
        for comp in matches:
            for gap in comp.get("weak_points", []):
                if gap not in all_gaps:
                    all_gaps.append(gap)

        return {
            "category": category,
            "competitors": matches,
            "avg_rating": round(sum(ratings) / len(ratings), 2) if ratings else 0.0,
            "avg_price_usd": round(sum(prices) / len(prices), 2) if prices else 0.0,
            "gaps": all_gaps,
            "pricing_benchmark": {
                "min_usd": min(prices) if prices else 0,
                "max_usd": max(prices) if prices else 0,
                "avg_usd": round(sum(prices) / len(prices), 2) if prices else 0,
            },
            "analyzed_at": datetime.now(timezone.utc).isoformat(),
        }

    def scrape_and_save(self, categories: Optional[List[str]] = None) -> dict:
        """
        Scrape (or simulate) competitor data for *categories* and persist
        the results to ``data/competitors.json``.

        Parameters
        ----------
        categories : list[str], optional
            Categories to scrape.  Defaults to all simulated categories.

        Returns
        -------
        dict
            Summary of competitors saved and path written.
        """
        if categories is None:
            categories = list({c["category"] for c in SIMULATED_COMPETITORS})

        new_entries: List[dict] = []
        for cat in categories:
            entries = self._fetch(cat)
            new_entries.extend(entries)

        self._competitors = new_entries
        self._save()
        return {
            "saved": len(new_entries),
            "categories": categories,
            "path": self._data_path,
            "scraped_at": datetime.now(timezone.utc).isoformat(),
        }

    def list_competitors(self, category: Optional[str] = None) -> List[dict]:
        """Return all stored competitors, optionally filtered by category."""
        if category:
            return [c for c in self._competitors if c.get("category", "").lower() == category.lower()]
        return list(self._competitors)

    def run(self) -> str:
        """GLOBAL AI SOURCES FLOW framework entry point."""
        return (
            f"CompetitorAnalyzer active — "
            f"{len(self._competitors)} competitor(s) loaded."
        )

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _fetch(self, category: str) -> List[dict]:
        """Return competitor records for *category*."""
        if self._simulated:
            return [
                c for c in SIMULATED_COMPETITORS
                if c["category"].lower() == category.lower()
            ]
        # Live scraping would be implemented here (GitHub, app stores, SaaS)
        return [
            c for c in self._competitors
            if c.get("category", "").lower() == category.lower()
        ]

    def _save(self) -> None:
        os.makedirs(os.path.dirname(self._data_path), exist_ok=True)
        payload = {
            "last_updated": datetime.now(timezone.utc).isoformat(),
            "competitors": self._competitors,
        }
        with open(self._data_path, "w", encoding="utf-8") as fh:
            json.dump(payload, fh, indent=2)

    def _load(self) -> None:
        if not os.path.exists(self._data_path):
            self._competitors = list(SIMULATED_COMPETITORS) if self._simulated else []
            return
        try:
            with open(self._data_path, encoding="utf-8") as fh:
                data = json.load(fh)
            self._competitors = data.get("competitors", [])
            if not self._competitors and self._simulated:
                self._competitors = list(SIMULATED_COMPETITORS)
        except (json.JSONDecodeError, OSError):
            self._competitors = list(SIMULATED_COMPETITORS) if self._simulated else []
