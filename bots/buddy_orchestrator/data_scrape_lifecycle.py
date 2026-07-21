"""
DataScrapeLifecycle — Manages data-scraping schedule and deadline for all bots.

All bots and systems scrape data until the configured deadline (default: June 22, 2026).
After the deadline, scraping is halted and a final dataset summary is produced.

Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from enum import Enum
from typing import Optional


# ---------------------------------------------------------------------------
# Default scraping deadline (June 22, 2026)
# ---------------------------------------------------------------------------

SCRAPE_DEADLINE: date = date(2026, 6, 22)


class ScrapeStatus(Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"  # deadline passed, all data collected


@dataclass
class BotScrapeRecord:
    """Tracks scraping state for a single bot."""

    bot_id: str
    datasets_collected: int = 0
    last_scraped_at: Optional[str] = None
    status: ScrapeStatus = ScrapeStatus.ACTIVE


class DataScrapeLifecycle:
    """
    Manages the scraping lifecycle for all registered bots.

    The scraping window runs from object instantiation until *deadline*
    (default: June 22, 2026).  After the deadline, ``scraping_active``
    returns ``False`` and calls to ``record_scrape`` are silently ignored.

    Parameters
    ----------
    deadline : date
        The date on which scraping should cease (inclusive).
    """

    def __init__(self, deadline: date = SCRAPE_DEADLINE) -> None:
        self.deadline = deadline
        self._records: dict[str, BotScrapeRecord] = {}

    # ------------------------------------------------------------------
    # Status helpers
    # ------------------------------------------------------------------

    def scraping_active(self) -> bool:
        """Return True if the current date is on or before the deadline."""
        return date.today() <= self.deadline

    def days_remaining(self) -> int:
        """Return the number of days remaining until (and including) the deadline.

        Returns 0 when the deadline has passed.
        """
        delta = (self.deadline - date.today()).days
        return max(0, delta)

    def deadline_iso(self) -> str:
        """Return the deadline as an ISO-8601 date string."""
        return self.deadline.isoformat()

    # ------------------------------------------------------------------
    # Registration
    # ------------------------------------------------------------------

    def register_bot(self, bot_id: str) -> BotScrapeRecord:
        """Register a bot for scraping tracking.  Idempotent."""
        if bot_id not in self._records:
            self._records[bot_id] = BotScrapeRecord(bot_id=bot_id)
        return self._records[bot_id]

    # ------------------------------------------------------------------
    # Recording scrapes
    # ------------------------------------------------------------------

    def record_scrape(self, bot_id: str, datasets: int = 1) -> dict:
        """
        Record a completed scraping run for *bot_id*.

        If the deadline has passed, the call is a no-op and returns a
        ``deadline_passed`` status dict.

        Parameters
        ----------
        bot_id : str
            The bot performing the scrape.
        datasets : int
            Number of datasets collected in this run.

        Returns
        -------
        dict with keys: ``bot_id``, ``status``, ``datasets_collected``,
        ``last_scraped_at``, ``days_remaining``.
        """
        if not self.scraping_active():
            return {
                "bot_id": bot_id,
                "status": "deadline_passed",
                "datasets_collected": self._records.get(bot_id, BotScrapeRecord(bot_id)).datasets_collected,
                "last_scraped_at": self._records.get(bot_id, BotScrapeRecord(bot_id)).last_scraped_at,
                "days_remaining": 0,
            }

        record = self.register_bot(bot_id)
        record.datasets_collected += datasets
        record.last_scraped_at = datetime.now(tz=timezone.utc).isoformat()
        return {
            "bot_id": bot_id,
            "status": "recorded",
            "datasets_collected": record.datasets_collected,
            "last_scraped_at": record.last_scraped_at,
            "days_remaining": self.days_remaining(),
        }

    # ------------------------------------------------------------------
    # Summary
    # ------------------------------------------------------------------

    def summary(self) -> dict:
        """Return an aggregate summary of the scraping lifecycle."""
        total_datasets = sum(r.datasets_collected for r in self._records.values())
        return {
            "deadline": self.deadline_iso(),
            "scraping_active": self.scraping_active(),
            "days_remaining": self.days_remaining(),
            "registered_bots": len(self._records),
            "total_datasets_collected": total_datasets,
            "bots": [
                {
                    "bot_id": r.bot_id,
                    "datasets_collected": r.datasets_collected,
                    "last_scraped_at": r.last_scraped_at,
                    "status": r.status.value,
                }
                for r in self._records.values()
            ],
        }
