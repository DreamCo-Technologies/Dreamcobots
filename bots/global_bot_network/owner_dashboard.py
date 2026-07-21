"""
Owner Dashboard — DreamCo Global Bot Communication Network.

Provides each owner with a real-time view of their bots:

  - Registered bot list
  - Live chat feed (last N messages per bot)
  - Bot activity logs
  - Earnings tracker
  - Kill switch (instantly disable a bot)

The dashboard is a pure-Python, in-memory implementation designed to be
backed by a real-time data store (Firebase / Socket.IO) in production.
"""

from __future__ import annotations

import sys
import os
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from framework import GlobalAISourcesFlow  # noqa: F401  (GLOBAL AI SOURCES FLOW)


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------

class DashboardError(Exception):
    """Base exception for owner dashboard errors."""


class BotNotOwned(DashboardError):
    """Raised when an owner tries to operate a bot they do not own."""


class BotAlreadyKilled(DashboardError):
    """Raised when attempting to kill an already-disabled bot."""


# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------

@dataclass
class ActivityLogEntry:
    """A single line in a bot's activity log."""

    bot_id: str
    event: str
    details: dict = field(default_factory=dict)
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def to_dict(self) -> dict:
        return {
            "bot_id": self.bot_id,
            "event": self.event,
            "details": dict(self.details),
            "timestamp": self.timestamp,
        }


@dataclass
class ChatMessage:
    """A message in a bot's chat feed."""

    bot_id: str
    direction: str          # "sent" | "received"
    content: str
    peer: str = ""          # bot/user the message was to/from
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def to_dict(self) -> dict:
        return {
            "bot_id": self.bot_id,
            "direction": self.direction,
            "content": self.content,
            "peer": self.peer,
            "timestamp": self.timestamp,
        }


@dataclass
class EarningsRecord:
    """Records an earnings event for a bot."""

    bot_id: str
    amount_usd: float
    source: str
    description: str = ""
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def to_dict(self) -> dict:
        return {
            "bot_id": self.bot_id,
            "amount_usd": self.amount_usd,
            "source": self.source,
            "description": self.description,
            "timestamp": self.timestamp,
        }


@dataclass
class BotControl:
    """Runtime control record for a bot."""

    bot_id: str
    owner_id: str
    display_name: str = ""
    is_active: bool = True
    kill_reason: str = ""
    registered_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    last_seen: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def touch(self) -> None:
        self.last_seen = datetime.now(timezone.utc).isoformat()

    def to_dict(self) -> dict:
        return {
            "bot_id": self.bot_id,
            "owner_id": self.owner_id,
            "display_name": self.display_name,
            "is_active": self.is_active,
            "kill_reason": self.kill_reason,
            "registered_at": self.registered_at,
            "last_seen": self.last_seen,
        }


# ---------------------------------------------------------------------------
# Owner Dashboard
# ---------------------------------------------------------------------------

class OwnerDashboard:
    """
    Per-owner dashboard that tracks bots, chat feeds, logs, and earnings.

    Parameters
    ----------
    owner_id : str
        Identifier for the dashboard owner.
    max_chat_feed_size : int
        Maximum chat messages kept per bot.
    max_activity_log_size : int
        Maximum activity log entries kept per bot.
    """

    def __init__(
        self,
        owner_id: str,
        max_chat_feed_size: int = 200,
        max_activity_log_size: int = 500,
    ) -> None:
        self.owner_id = owner_id
        self._bots: dict[str, BotControl] = {}
        self._chat_feeds: dict[str, deque] = defaultdict(
            lambda: deque(maxlen=max_chat_feed_size)
        )
        self._activity_logs: dict[str, deque] = defaultdict(
            lambda: deque(maxlen=max_activity_log_size)
        )
        self._earnings: list[EarningsRecord] = []

    # ------------------------------------------------------------------
    # Bot management
    # ------------------------------------------------------------------

    def add_bot(self, bot_id: str, display_name: str = "") -> BotControl:
        """Register a bot with this owner's dashboard."""
        ctrl = BotControl(
            bot_id=bot_id,
            owner_id=self.owner_id,
            display_name=display_name or bot_id,
        )
        self._bots[bot_id] = ctrl
        self._log_activity(bot_id, "bot_added", {"display_name": display_name})
        return ctrl

    def remove_bot(self, bot_id: str) -> None:
        """Remove a bot from the dashboard."""
        self._bots.pop(bot_id, None)

    def list_bots(self) -> list[dict]:
        """Return metadata for all registered bots."""
        return [ctrl.to_dict() for ctrl in self._bots.values()]

    def get_bot(self, bot_id: str) -> BotControl:
        """Return the BotControl for *bot_id*."""
        if bot_id not in self._bots:
            raise BotNotOwned(
                f"Bot '{bot_id}' is not registered on dashboard for owner '{self.owner_id}'."
            )
        return self._bots[bot_id]

    # ------------------------------------------------------------------
    # Kill switch
    # ------------------------------------------------------------------

    def kill_bot(self, bot_id: str, reason: str = "Owner initiated kill switch") -> BotControl:
        """
        Immediately disable *bot_id*.

        Raises
        ------
        BotNotOwned
            If the bot is not on this dashboard.
        BotAlreadyKilled
            If the bot is already disabled.
        """
        ctrl = self.get_bot(bot_id)
        if not ctrl.is_active:
            raise BotAlreadyKilled(f"Bot '{bot_id}' is already disabled.")
        ctrl.is_active = False
        ctrl.kill_reason = reason
        ctrl.touch()
        self._log_activity(bot_id, "kill_switch_activated", {"reason": reason})
        return ctrl

    def revive_bot(self, bot_id: str) -> BotControl:
        """Re-enable a killed bot."""
        ctrl = self.get_bot(bot_id)
        ctrl.is_active = True
        ctrl.kill_reason = ""
        ctrl.touch()
        self._log_activity(bot_id, "bot_revived", {})
        return ctrl

    # ------------------------------------------------------------------
    # Chat feed
    # ------------------------------------------------------------------

    def record_chat(
        self,
        bot_id: str,
        content: str,
        direction: str = "sent",
        peer: str = "",
    ) -> ChatMessage:
        """Add a message to *bot_id*'s chat feed."""
        msg = ChatMessage(
            bot_id=bot_id,
            direction=direction,
            content=content,
            peer=peer,
        )
        self._chat_feeds[bot_id].append(msg)
        return msg

    def get_chat_feed(self, bot_id: str, limit: Optional[int] = None) -> list[dict]:
        """Return recent chat messages for *bot_id*."""
        messages = list(self._chat_feeds[bot_id])
        if limit is not None:
            messages = messages[-limit:]
        return [m.to_dict() for m in messages]

    # ------------------------------------------------------------------
    # Activity log
    # ------------------------------------------------------------------

    def _log_activity(self, bot_id: str, event: str, details: dict) -> None:
        entry = ActivityLogEntry(bot_id=bot_id, event=event, details=details)
        self._activity_logs[bot_id].append(entry)

    def log_activity(self, bot_id: str, event: str, details: Optional[dict] = None) -> None:
        """Manually append to *bot_id*'s activity log."""
        self._log_activity(bot_id, event, details or {})

    def get_activity_log(self, bot_id: str, limit: Optional[int] = None) -> list[dict]:
        """Return recent activity log entries for *bot_id*."""
        entries = list(self._activity_logs[bot_id])
        if limit is not None:
            entries = entries[-limit:]
        return [e.to_dict() for e in entries]

    # ------------------------------------------------------------------
    # Earnings tracker
    # ------------------------------------------------------------------

    def record_earning(
        self,
        bot_id: str,
        amount_usd: float,
        source: str,
        description: str = "",
    ) -> EarningsRecord:
        """Record an earnings event for *bot_id*."""
        rec = EarningsRecord(
            bot_id=bot_id,
            amount_usd=amount_usd,
            source=source,
            description=description,
        )
        self._earnings.append(rec)
        self._log_activity(
            bot_id, "earning_recorded",
            {"amount_usd": amount_usd, "source": source},
        )
        return rec

    def get_earnings(
        self, bot_id: Optional[str] = None
    ) -> list[dict]:
        """Return earnings records, optionally filtered by bot."""
        records = self._earnings
        if bot_id:
            records = [r for r in records if r.bot_id == bot_id]
        return [r.to_dict() for r in records]

    def total_earnings(self, bot_id: Optional[str] = None) -> float:
        """Return total earnings in USD, optionally for a single bot."""
        return sum(r.amount_usd for r in self._earnings
                   if bot_id is None or r.bot_id == bot_id)

    # ------------------------------------------------------------------
    # Dashboard snapshot
    # ------------------------------------------------------------------

    def snapshot(self) -> dict:
        """Return a full real-time snapshot of the dashboard."""
        return {
            "owner_id": self.owner_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "bots": self.list_bots(),
            "total_bots": len(self._bots),
            "active_bots": sum(1 for c in self._bots.values() if c.is_active),
            "killed_bots": sum(1 for c in self._bots.values() if not c.is_active),
            "total_earnings_usd": self.total_earnings(),
            "total_earnings_records": len(self._earnings),
        }
