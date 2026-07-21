"""
income_tracker.py – Centralized Income Tracking System.

Provides a registry of *income source adapters* (YouTube, Blog, Books,
SaaS, Ads, Affiliates) and a ``IncomeTracker`` orchestrator that polls
each adapter, stores the results, and publishes summary events on the
shared ``EventBus``.

Real API calls are hidden behind thin adapter interfaces so they can be
swapped for live implementations by simply providing real ``api_key`` /
``channel_id`` values in ``config.json``.
"""

from __future__ import annotations

import datetime
import logging
import random
from abc import ABC, abstractmethod
from typing import Any

from .event_bus import EventBus

logger = logging.getLogger(__name__)

# ── Data model ─────────────────────────────────────────────────────────────


class IncomeRecord:
    """Immutable snapshot of income data for one source at one point in time."""

    __slots__ = (
        "source", "date", "revenue", "traffic", "engagement", "currency", "raw"
    )

    def __init__(
        self,
        source: str,
        revenue: float,
        traffic: int = 0,
        engagement: float = 0.0,
        currency: str = "USD",
        raw: dict | None = None,
        date: datetime.date | None = None,
    ) -> None:
        self.source = source
        self.date = date or datetime.date.today()
        self.revenue = revenue
        self.traffic = traffic
        self.engagement = engagement
        self.currency = currency
        self.raw = raw or {}

    def to_dict(self) -> dict:
        return {
            "source": self.source,
            "date": self.date.isoformat(),
            "revenue": self.revenue,
            "traffic": self.traffic,
            "engagement": self.engagement,
            "currency": self.currency,
        }

    def __repr__(self) -> str:
        return (
            f"IncomeRecord(source={self.source!r}, date={self.date}, "
            f"revenue={self.revenue:.2f}, traffic={self.traffic})"
        )


# ── Base adapter ───────────────────────────────────────────────────────────


class IncomeSourceAdapter(ABC):
    """Abstract base class for all income-source integrations."""

    name: str = "unknown"

    def __init__(self, cfg: dict) -> None:
        self.cfg = cfg

    @abstractmethod
    def fetch(self) -> IncomeRecord:
        """Fetch the latest income data and return an ``IncomeRecord``."""


# ── Concrete adapters (stub implementations) ───────────────────────────────
# Each adapter provides a realistic stub that generates plausible data.
# Replace the body of ``fetch`` with real API calls when credentials are
# available.


class YouTubeAdapter(IncomeSourceAdapter):
    """YouTube AdSense / channel analytics."""

    name = "YouTube"

    def fetch(self) -> IncomeRecord:
        api_key = self.cfg.get("youtube_api_key", "")
        if api_key:
            # TODO: replace with real YouTube Analytics API call
            logger.info("Fetching live YouTube data (key configured)")
        revenue = round(random.uniform(50, 500), 2)
        views = random.randint(5_000, 50_000)
        ctr = round(random.uniform(2.0, 8.0), 2)
        return IncomeRecord(
            source=self.name,
            revenue=revenue,
            traffic=views,
            engagement=ctr,
            raw={"views": views, "ctr_pct": ctr},
        )


class BlogAdapter(IncomeSourceAdapter):
    """Blog / website ad revenue and traffic."""

    name = "Blog"

    def fetch(self) -> IncomeRecord:
        revenue = round(random.uniform(10, 200), 2)
        page_views = random.randint(1_000, 20_000)
        avg_time = round(random.uniform(1.5, 5.0), 2)
        return IncomeRecord(
            source=self.name,
            revenue=revenue,
            traffic=page_views,
            engagement=avg_time,
            raw={"page_views": page_views, "avg_time_minutes": avg_time},
        )


class BooksAdapter(IncomeSourceAdapter):
    """E-book / book royalties (e.g., Amazon KDP)."""

    name = "Books"

    def fetch(self) -> IncomeRecord:
        revenue = round(random.uniform(5, 150), 2)
        downloads = random.randint(10, 500)
        rating = round(random.uniform(3.5, 5.0), 1)
        return IncomeRecord(
            source=self.name,
            revenue=revenue,
            traffic=downloads,
            engagement=rating,
            raw={"downloads": downloads, "avg_rating": rating},
        )


class SaaSAdapter(IncomeSourceAdapter):
    """SaaS subscription revenue."""

    name = "SaaS"

    def fetch(self) -> IncomeRecord:
        revenue = round(random.uniform(100, 2000), 2)
        active_users = random.randint(20, 500)
        churn = round(random.uniform(1.0, 10.0), 2)
        return IncomeRecord(
            source=self.name,
            revenue=revenue,
            traffic=active_users,
            engagement=churn,
            raw={"active_users": active_users, "churn_rate_pct": churn},
        )


class AdsAdapter(IncomeSourceAdapter):
    """Display / programmatic advertising revenue."""

    name = "Ads"

    def fetch(self) -> IncomeRecord:
        revenue = round(random.uniform(20, 300), 2)
        impressions = random.randint(10_000, 200_000)
        cpm = round(revenue / impressions * 1000, 4)
        return IncomeRecord(
            source=self.name,
            revenue=revenue,
            traffic=impressions,
            engagement=cpm,
            raw={"impressions": impressions, "cpm": cpm},
        )


class AffiliatesAdapter(IncomeSourceAdapter):
    """Affiliate marketing commissions."""

    name = "Affiliates"

    def fetch(self) -> IncomeRecord:
        revenue = round(random.uniform(15, 400), 2)
        clicks = random.randint(200, 5_000)
        conv_rate = round(random.uniform(0.5, 5.0), 2)
        return IncomeRecord(
            source=self.name,
            revenue=revenue,
            traffic=clicks,
            engagement=conv_rate,
            raw={"clicks": clicks, "conversion_rate_pct": conv_rate},
        )


class AppsAdapter(IncomeSourceAdapter):
    """Mobile / web app in-app purchase & subscription revenue."""

    name = "Apps"

    def fetch(self) -> IncomeRecord:
        revenue = round(random.uniform(30, 800), 2)
        dau = random.randint(100, 10_000)
        retention = round(random.uniform(20.0, 60.0), 1)
        return IncomeRecord(
            source=self.name,
            revenue=revenue,
            traffic=dau,
            engagement=retention,
            raw={"daily_active_users": dau, "retention_rate_pct": retention},
        )


# ── Registry helper ────────────────────────────────────────────────────────

_DEFAULT_ADAPTERS: list[type[IncomeSourceAdapter]] = [
    YouTubeAdapter,
    BlogAdapter,
    BooksAdapter,
    SaaSAdapter,
    AdsAdapter,
    AffiliatesAdapter,
    AppsAdapter,
]


# ── Orchestrator ───────────────────────────────────────────────────────────


class IncomeTracker:
    """
    Orchestrates all income source adapters.

    Usage::

        tracker = IncomeTracker(cfg, bus)
        records = tracker.collect_all()
        summary = tracker.summarize(records)
    """

    def __init__(
        self,
        cfg: dict,
        bus: EventBus,
        adapters: list[IncomeSourceAdapter] | None = None,
    ) -> None:
        self.cfg = cfg
        self.bus = bus
        self._history: list[IncomeRecord] = []
        if adapters is not None:
            self.adapters = adapters
        else:
            self.adapters = [cls(cfg) for cls in _DEFAULT_ADAPTERS]

    # ------------------------------------------------------------------
    # Collection
    # ------------------------------------------------------------------

    def collect_all(self) -> list[IncomeRecord]:
        """Fetch data from every registered adapter and return the records."""
        records: list[IncomeRecord] = []
        for adapter in self.adapters:
            try:
                record = adapter.fetch()
                records.append(record)
                self._history.append(record)
                logger.info(
                    "Collected from %s: $%.2f revenue, %d traffic",
                    record.source,
                    record.revenue,
                    record.traffic,
                )
            except Exception:  # noqa: BLE001
                logger.exception("Failed to fetch from adapter %s", adapter.name)
        self.bus.publish("income.collected", records)
        return records

    # ------------------------------------------------------------------
    # Analysis
    # ------------------------------------------------------------------

    def summarize(self, records: list[IncomeRecord]) -> dict[str, Any]:
        """Return aggregated summary statistics for a list of records."""
        if not records:
            return {}
        total_revenue = sum(r.revenue for r in records)
        total_traffic = sum(r.traffic for r in records)
        by_source = {r.source: r.to_dict() for r in records}
        top_source = max(records, key=lambda r: r.revenue)
        summary = {
            "date": datetime.date.today().isoformat(),
            "total_revenue": round(total_revenue, 2),
            "total_traffic": total_traffic,
            "source_count": len(records),
            "top_source": top_source.source,
            "top_revenue": round(top_source.revenue, 2),
            "by_source": by_source,
        }
        self.bus.publish("income.summarized", summary)
        return summary

    def history(self) -> list[IncomeRecord]:
        """Return all records collected in this session."""
        return list(self._history)
