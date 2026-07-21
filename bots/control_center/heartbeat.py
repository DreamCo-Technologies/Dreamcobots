"""
DreamCo Control Tower — Heartbeat Monitor

Tracks whether bots are "live" or "offline" based on periodic pings.

# GLOBAL AI SOURCES FLOW
"""

from __future__ import annotations

import sys
import os
from datetime import datetime, timezone, timedelta
from typing import Optional

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'ai-models-integration'))
from framework import GlobalAISourcesFlow  # noqa: F401

# A bot is considered offline if it has not pinged within this many seconds.
DEFAULT_TIMEOUT_SECONDS: int = 60


class HeartbeatMonitor:
    """Track live/offline status of registered bots via periodic pings."""

    def __init__(self, timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS) -> None:
        self._timeout = timeout_seconds
        self._pings: dict[str, dict] = {}   # bot_name -> last ping metadata

    # ------------------------------------------------------------------
    # Ping
    # ------------------------------------------------------------------

    def ping(self, bot_name: str, metadata: Optional[dict] = None) -> dict:
        """Record a heartbeat ping for *bot_name*.

        Parameters
        ----------
        bot_name:
            Unique identifier for the bot.
        metadata:
            Optional extra info (version, host, etc.) to store with the ping.

        Returns
        -------
        dict with ``bot_name``, ``status``, and ``pinged_at``.
        """
        now = datetime.now(timezone.utc)
        record = {
            "bot_name": bot_name,
            "pinged_at": now.isoformat(),
            "status": "live",
            "metadata": metadata or {},
        }
        self._pings[bot_name] = record
        return record

    # ------------------------------------------------------------------
    # Status
    # ------------------------------------------------------------------

    def get_status(self, bot_name: str) -> dict:
        """Return the current live/offline status for *bot_name*."""
        if bot_name not in self._pings:
            return {
                "bot_name": bot_name,
                "status": "offline",
                "pinged_at": None,
                "seconds_since_ping": None,
            }

        record = self._pings[bot_name]
        pinged_at = datetime.fromisoformat(record["pinged_at"])
        elapsed = (datetime.now(timezone.utc) - pinged_at).total_seconds()
        status = "live" if elapsed <= self._timeout else "offline"

        return {
            "bot_name": bot_name,
            "status": status,
            "pinged_at": record["pinged_at"],
            "seconds_since_ping": round(elapsed, 1),
            "metadata": record.get("metadata", {}),
        }

    def get_all_status(self) -> dict:
        """Return live/offline status for every known bot."""
        result = {}
        for bot_name in self._pings:
            result[bot_name] = self.get_status(bot_name)
        return result

    # ------------------------------------------------------------------
    # Summary
    # ------------------------------------------------------------------

    def summary(self) -> dict:
        """Return a high-level summary (total, live, offline)."""
        statuses = self.get_all_status()
        live = sum(1 for s in statuses.values() if s["status"] == "live")
        offline = len(statuses) - live
        return {
            "total_monitored": len(statuses),
            "live": live,
            "offline": offline,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    # ------------------------------------------------------------------
    # Reset
    # ------------------------------------------------------------------

    def reset(self, bot_name: Optional[str] = None) -> None:
        """Remove heartbeat records for *bot_name* (or all bots if None)."""
        if bot_name is None:
            self._pings.clear()
        else:
            self._pings.pop(bot_name, None)


__all__ = ["HeartbeatMonitor", "DEFAULT_TIMEOUT_SECONDS"]
