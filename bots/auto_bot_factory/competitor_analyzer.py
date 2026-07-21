"""
Competitor Analyzer — scans app stores, GitHub repos, and SaaS directories
to benchmark competitor features, ratings, and performance gaps.

Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.
See framework/global_ai_sources_flow.py for the full pipeline specification.
"""

from __future__ import annotations

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from framework import GlobalAISourcesFlow  # noqa: F401  (GLOBAL AI SOURCES FLOW)

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional


# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------

@dataclass
class CompetitorProfile:
    """Profile of a competing bot or SaaS product."""
    name: str
    category: str
    source: str
    rating: float = 0.0
    price_usd_monthly: float = 0.0
    features: list[str] = field(default_factory=list)
    weaknesses: list[str] = field(default_factory=list)
    strengths: list[str] = field(default_factory=list)
    user_reviews_summary: str = ""
    analyzed_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "category": self.category,
            "source": self.source,
            "rating": self.rating,
            "price_usd_monthly": self.price_usd_monthly,
            "features": self.features,
            "weaknesses": self.weaknesses,
            "strengths": self.strengths,
            "user_reviews_summary": self.user_reviews_summary,
            "analyzed_at": self.analyzed_at,
        }


@dataclass
class MarketGap:
    """An identified gap in the competitor landscape."""
    category: str
    description: str
    opportunity_score: float  # 0-100
    recommended_features: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "category": self.category,
            "description": self.description,
            "opportunity_score": self.opportunity_score,
            "recommended_features": self.recommended_features,
        }


@dataclass
class AnalysisReport:
    """Full competitor analysis report."""
    query: str
    competitors: list[CompetitorProfile] = field(default_factory=list)
    gaps: list[MarketGap] = field(default_factory=list)
    top_features_missing: list[str] = field(default_factory=list)
    recommended_price_usd: float = 0.0
    generated_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def to_dict(self) -> dict:
        return {
            "query": self.query,
            "competitors": [c.to_dict() for c in self.competitors],
            "gaps": [g.to_dict() for g in self.gaps],
            "top_features_missing": self.top_features_missing,
            "recommended_price_usd": self.recommended_price_usd,
            "generated_at": self.generated_at,
            "competitor_count": len(self.competitors),
            "gap_count": len(self.gaps),
        }


# ---------------------------------------------------------------------------
# Simulated competitor data by category
# ---------------------------------------------------------------------------

_COMPETITOR_DB: dict[str, list[dict]] = {
    "lead_generation": [
        {
            "name": "LeadBot Pro",
            "rating": 3.8,
            "price": 149.0,
            "features": ["basic scraping", "email outreach"],
            "weaknesses": ["no SMS", "slow speed", "no follow-up", "no AI"],
            "strengths": ["simple UI"],
        },
        {
            "name": "SalesFlow AI",
            "rating": 4.1,
            "price": 299.0,
            "features": ["CRM integration", "email sequences"],
            "weaknesses": ["expensive", "no voice", "no real-time data"],
            "strengths": ["CRM", "email automation"],
        },
    ],
    "sales": [
        {
            "name": "CloserBot",
            "rating": 3.5,
            "price": 199.0,
            "features": ["SMS outreach", "basic analytics"],
            "weaknesses": ["no follow-up automation", "no conversion tracking", "crashes"],
            "strengths": ["SMS"],
        },
        {
            "name": "DealMaker SaaS",
            "rating": 4.0,
            "price": 399.0,
            "features": ["pipeline management", "team collaboration"],
            "weaknesses": ["complex setup", "no bot automation", "no AI"],
            "strengths": ["pipeline UI", "team features"],
        },
    ],
    "automation": [
        {
            "name": "AutoTask Bot",
            "rating": 3.9,
            "price": 99.0,
            "features": ["workflow automation", "basic integrations"],
            "weaknesses": ["no NLP", "rigid workflows", "no self-healing"],
            "strengths": ["workflow builder"],
        },
    ],
    "default": [
        {
            "name": "Generic SaaS Bot",
            "rating": 3.5,
            "price": 99.0,
            "features": ["basic automation"],
            "weaknesses": ["limited features", "slow", "no AI", "no analytics"],
            "strengths": ["low price"],
        },
    ],
}

_COMMON_GAPS: dict[str, list[str]] = {
    "lead_generation": [
        "AI-powered lead scoring",
        "Real-time competitor monitoring",
        "Multi-channel outreach (SMS + voice + email)",
        "Auto follow-up sequences",
        "Conversion funnel analytics",
    ],
    "sales": [
        "Automated deal closing",
        "Revenue tracking and forecasting",
        "Niche-specific messaging templates",
        "Self-healing crash recovery",
        "Usage-based pricing flexibility",
    ],
    "automation": [
        "NLP-driven workflow adaptation",
        "Self-optimizing decision loops",
        "Real-time performance dashboards",
        "GitHub-native deployment",
        "Persistent state across runs",
    ],
    "default": [
        "AI-driven decision engine",
        "Persistent memory across sessions",
        "Real metrics (not simulated data)",
        "Self-healing on crash",
        "24/7 GitHub-native operation",
    ],
}


# ---------------------------------------------------------------------------
# Analyzer
# ---------------------------------------------------------------------------

class CompetitorAnalyzer:
    """
    Scans simulated app stores, GitHub repos, and SaaS directories to benchmark
    competitor features, ratings, and performance gaps for a given category.

    Parameters
    ----------
    max_results : int
        Maximum number of competitor profiles to return per analysis.
    """

    def __init__(self, max_results: int = 10) -> None:
        self.max_results = max_results
        self._analysis_history: list[AnalysisReport] = []

    # ------------------------------------------------------------------
    # Core analysis
    # ------------------------------------------------------------------

    def analyze(self, category: str, query: str = "") -> AnalysisReport:
        """
        Run a full competitor analysis for the given category.

        Parameters
        ----------
        category : str
            Bot/product category, e.g. "lead_generation", "sales".
        query : str
            Optional free-text query for context.

        Returns
        -------
        AnalysisReport
            Full competitor analysis with gaps and recommendations.
        """
        norm_cat = category.lower().replace(" ", "_")
        raw_competitors = _COMPETITOR_DB.get(norm_cat, _COMPETITOR_DB["default"])
        raw_gaps = _COMMON_GAPS.get(norm_cat, _COMMON_GAPS["default"])

        competitors = [
            CompetitorProfile(
                name=c["name"],
                category=norm_cat,
                source="simulated_market_scan",
                rating=c["rating"],
                price_usd_monthly=c["price"],
                features=list(c["features"]),
                weaknesses=list(c["weaknesses"]),
                strengths=list(c["strengths"]),
                user_reviews_summary=(
                    f"Users report {c['name']} is limited by: "
                    + ", ".join(c["weaknesses"][:2])
                ),
            )
            for c in raw_competitors[: self.max_results]
        ]

        gaps = [
            MarketGap(
                category=norm_cat,
                description=gap_desc,
                opportunity_score=min(100.0, 60.0 + i * 8.0),
                recommended_features=[gap_desc],
            )
            for i, gap_desc in enumerate(raw_gaps)
        ]

        all_missing: list[str] = []
        for comp in competitors:
            all_missing.extend(comp.weaknesses)

        seen: set[str] = set()
        unique_missing: list[str] = []
        for f in all_missing:
            if f not in seen:
                seen.add(f)
                unique_missing.append(f)

        avg_price = (
            sum(c.price_usd_monthly for c in competitors) / len(competitors)
            if competitors
            else 99.0
        )
        recommended_price = round(avg_price * 0.8, 2)

        report = AnalysisReport(
            query=query or category,
            competitors=competitors,
            gaps=gaps,
            top_features_missing=unique_missing[:10],
            recommended_price_usd=recommended_price,
        )

        self._analysis_history.append(report)
        return report

    def get_top_opportunities(self, category: str) -> list[dict]:
        """Return the top market opportunities for a category, sorted by score."""
        report = self.analyze(category)
        return sorted(
            [g.to_dict() for g in report.gaps],
            key=lambda x: x["opportunity_score"],
            reverse=True,
        )

    def get_analysis_history(self) -> list[dict]:
        """Return all previous analysis reports."""
        return [r.to_dict() for r in self._analysis_history]

    def get_feature_recommendations(self, category: str) -> list[str]:
        """Return prioritized feature recommendations based on competitor gaps."""
        report = self.analyze(category)
        recs: list[str] = []
        for gap in sorted(report.gaps, key=lambda g: g.opportunity_score, reverse=True):
            recs.extend(gap.recommended_features)
        return recs[:20]
