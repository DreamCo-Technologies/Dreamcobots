"""
market_analysis.py – Autonomous Market Analysis module.

Continuously scans market trends and identifies high-potential areas for
new residual income streams.  Publishes structured opportunity reports on
the shared EventBus.

In production, plug real data feeds (Google Trends API, social listening
tools, news aggregators) into the ``TrendScanner`` class.  Out-of-the-box
the module ships with a curated seed dataset that produces realistic
outputs for testing and demo purposes.
"""

from __future__ import annotations

import datetime
import logging
import random
from dataclasses import dataclass, field
from typing import Any

from .event_bus import EventBus

logger = logging.getLogger(__name__)

# ── Seed trend data ────────────────────────────────────────────────────────

_TREND_SEED: list[dict] = [
    {
        "topic": "AI-powered writing tools",
        "category": "SaaS",
        "growth_pct": 142,
        "search_volume": 320_000,
        "competition": "medium",
        "monetization_paths": ["SaaS subscription", "affiliate", "e-book"],
    },
    {
        "topic": "Short-form video content",
        "category": "YouTube / TikTok",
        "growth_pct": 98,
        "search_volume": 1_200_000,
        "competition": "high",
        "monetization_paths": ["AdSense", "sponsorships", "affiliate"],
    },
    {
        "topic": "Micro-SaaS for solopreneurs",
        "category": "SaaS",
        "growth_pct": 78,
        "search_volume": 45_000,
        "competition": "low",
        "monetization_paths": ["SaaS subscription", "lifetime deal"],
    },
    {
        "topic": "Niche affiliate marketing",
        "category": "Affiliates",
        "growth_pct": 55,
        "search_volume": 210_000,
        "competition": "medium",
        "monetization_paths": ["affiliate commissions", "blog", "e-mail list"],
    },
    {
        "topic": "Digital product bundles",
        "category": "E-commerce",
        "growth_pct": 67,
        "search_volume": 89_000,
        "competition": "low",
        "monetization_paths": ["direct sales", "Gumroad", "Etsy"],
    },
    {
        "topic": "Print-on-demand merchandise",
        "category": "E-commerce",
        "growth_pct": 43,
        "search_volume": 175_000,
        "competition": "high",
        "monetization_paths": ["Merch by Amazon", "Redbubble", "Printful"],
    },
    {
        "topic": "Online course creation",
        "category": "Education",
        "growth_pct": 91,
        "search_volume": 530_000,
        "competition": "medium",
        "monetization_paths": ["Udemy", "Teachable", "cohort-based course"],
    },
    {
        "topic": "Dividend investing content",
        "category": "Finance / Blog",
        "growth_pct": 38,
        "search_volume": 410_000,
        "competition": "high",
        "monetization_paths": ["blog ads", "affiliate (brokerages)", "e-book"],
    },
    {
        "topic": "No-code app development",
        "category": "Apps",
        "growth_pct": 112,
        "search_volume": 68_000,
        "competition": "low",
        "monetization_paths": ["SaaS subscription", "consulting", "templates"],
    },
    {
        "topic": "Automated e-mail newsletters",
        "category": "Blog / Newsletter",
        "growth_pct": 74,
        "search_volume": 95_000,
        "competition": "medium",
        "monetization_paths": ["paid newsletter", "sponsorships", "affiliate"],
    },
    {
        "topic": "AI image generation services",
        "category": "SaaS",
        "growth_pct": 185,
        "search_volume": 400_000,
        "competition": "medium",
        "monetization_paths": ["SaaS subscription", "API access", "stock images"],
    },
    {
        "topic": "Faceless YouTube channels",
        "category": "YouTube",
        "growth_pct": 63,
        "search_volume": 140_000,
        "competition": "medium",
        "monetization_paths": ["AdSense", "affiliate", "sponsorships"],
    },
]


# ── Data models ────────────────────────────────────────────────────────────


@dataclass
class TrendSignal:
    topic: str
    category: str
    growth_pct: float
    search_volume: int
    competition: str          # low / medium / high
    monetization_paths: list[str] = field(default_factory=list)
    opportunity_score: float = 0.0
    date_scanned: str = field(
        default_factory=lambda: datetime.date.today().isoformat()
    )

    def to_dict(self) -> dict:
        return {
            "topic": self.topic,
            "category": self.category,
            "growth_pct": self.growth_pct,
            "search_volume": self.search_volume,
            "competition": self.competition,
            "monetization_paths": self.monetization_paths,
            "opportunity_score": round(self.opportunity_score, 2),
            "date_scanned": self.date_scanned,
        }


@dataclass
class MarketReport:
    date: str
    top_trends: list[TrendSignal]
    recommended_niches: list[str]
    emerging_categories: list[str]
    summary: str

    def to_dict(self) -> dict:
        return {
            "date": self.date,
            "top_trends": [t.to_dict() for t in self.top_trends],
            "recommended_niches": self.recommended_niches,
            "emerging_categories": self.emerging_categories,
            "summary": self.summary,
        }


# ── Core classes ───────────────────────────────────────────────────────────


class TrendScanner:
    """
    Scans for trending topics and scores their income opportunity.

    Extend ``_fetch_raw_trends`` to integrate real data sources such as
    Google Trends, Reddit API, or Twitter / X trending topics.
    """

    _COMPETITION_WEIGHT = {"low": 1.3, "medium": 1.0, "high": 0.7}

    def __init__(self, cfg: dict) -> None:
        self.cfg = cfg
        self.limit = int(cfg.get("top_trends_limit", 10))

    def scan(self) -> list[TrendSignal]:
        """Return ranked ``TrendSignal`` objects for the current market."""
        raw = self._fetch_raw_trends()
        signals = [self._score(r) for r in raw]
        signals.sort(key=lambda s: s.opportunity_score, reverse=True)
        return signals[: self.limit]

    # ------------------------------------------------------------------

    def _fetch_raw_trends(self) -> list[dict]:
        """Fetch raw trend data.  Override for live API integration."""
        # Add slight randomness to simulate time-varying signals
        sampled = random.sample(_TREND_SEED, k=min(len(_TREND_SEED), self.limit + 2))
        for item in sampled:
            item = dict(item)
            item["growth_pct"] = item["growth_pct"] * random.uniform(0.9, 1.1)
            item["search_volume"] = int(item["search_volume"] * random.uniform(0.85, 1.15))
        return sampled

    def _score(self, raw: dict) -> TrendSignal:
        """Compute a composite opportunity score (0 – 10)."""
        competition_weight = self._COMPETITION_WEIGHT.get(
            raw.get("competition", "medium"), 1.0
        )
        # Normalise growth (assume 200% = max)
        growth_norm = min(raw.get("growth_pct", 0) / 200, 1.0)
        # Normalise search volume (assume 1M = max)
        volume_norm = min(raw.get("search_volume", 0) / 1_000_000, 1.0)
        score = ((growth_norm * 0.5 + volume_norm * 0.5) * 10) * competition_weight
        score = round(min(score, 10.0), 2)
        return TrendSignal(
            topic=raw["topic"],
            category=raw.get("category", "General"),
            growth_pct=round(raw.get("growth_pct", 0), 1),
            search_volume=raw.get("search_volume", 0),
            competition=raw.get("competition", "medium"),
            monetization_paths=raw.get("monetization_paths", []),
            opportunity_score=score,
        )


class MarketAnalysis:
    """
    High-level market analysis orchestrator.

    Usage::

        ma = MarketAnalysis(cfg, bus)
        report = ma.run_analysis()
        ma.print_report(report)
    """

    def __init__(self, cfg: dict, bus: EventBus) -> None:
        self.cfg = cfg
        self.bus = bus
        self.scanner = TrendScanner(cfg)

    def run_analysis(self) -> MarketReport:
        """Run a full market scan and return a ``MarketReport``."""
        logger.info("Starting market analysis scan…")
        signals = self.scanner.scan()

        top_n = signals[:5]
        recommended_niches = list({s.category for s in signals[:8]})
        emerging = [
            s.topic for s in signals if s.growth_pct > 80
        ][:5]

        summary = (
            f"Scanned {len(signals)} trending topics. "
            f"Top opportunity: '{top_n[0].topic}' (score {top_n[0].opportunity_score}/10). "
            f"Fastest growing category: {top_n[0].category}."
            if top_n else "No signals detected."
        )

        report = MarketReport(
            date=datetime.date.today().isoformat(),
            top_trends=top_n,
            recommended_niches=recommended_niches,
            emerging_categories=emerging,
            summary=summary,
        )
        logger.info("Market analysis complete. %s", summary)
        self.bus.publish("market.analysis_complete", report.to_dict())
        return report

    def print_report(self, report: MarketReport) -> None:
        """Print a formatted market report to stdout."""
        print(f"\n{'═' * 60}")
        print(f"  Market Analysis Report — {report.date}")
        print(f"{'═' * 60}")
        print(f"  Summary: {report.summary}\n")
        print(f"  {'Topic':<35} {'Score':>6}  {'Growth':>7}  {'Competition':>12}")
        print(f"  {'-'*35} {'-'*6}  {'-'*7}  {'-'*12}")
        for t in report.top_trends:
            print(
                f"  {t.topic:<35} {t.opportunity_score:>6.1f}  "
                f"{t.growth_pct:>6.0f}%  {t.competition:>12}"
            )
        print(f"\n  Recommended Niches : {', '.join(report.recommended_niches)}")
        print(f"  Emerging Topics    : {', '.join(report.emerging_categories)}")
        print(f"{'═' * 60}\n")

    def suggest_new_streams(
        self, report: MarketReport, top_k: int = 3
    ) -> list[dict[str, Any]]:
        """Return the top-*k* income stream suggestions from the report."""
        suggestions = []
        for trend in report.top_trends[:top_k]:
            suggestions.append({
                "topic": trend.topic,
                "category": trend.category,
                "opportunity_score": trend.opportunity_score,
                "monetization_paths": trend.monetization_paths,
                "rationale": (
                    f"{trend.growth_pct:.0f}% growth rate with "
                    f"{trend.competition} competition and "
                    f"{trend.search_volume:,} monthly searches."
                ),
            })
        self.bus.publish("market.new_streams_suggested", suggestions)
        return suggestions
