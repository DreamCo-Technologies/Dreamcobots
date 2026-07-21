"""
Messaging Network — DreamCo Global Bot Communication Network.

Provides real-time (in-process) bot-to-bot communication with:
  - Message routing (point-to-point and broadcast)
  - Delivery receipts and message logs
  - Rate limiting per bot
  - Permission enforcement
  - Subscriber / callback pattern (Socket.IO-style)

In production this layer would be backed by Firebase Realtime Database or
Socket.IO over WebSockets.  This pure-Python implementation matches that
interface so bots can be tested without external dependencies.
"""

from __future__ import annotations

import sys
import os
import threading
from collections import defaultdict, deque
from datetime import datetime, timezone
from typing import Callable, Optional

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from framework import GlobalAISourcesFlow  # noqa: F401  (GLOBAL AI SOURCES FLOW)

from bots.global_bot_network.universal_bot_protocol import (
    UBPMessage,
    MessageType,
    Permission,
    UBPError,
    UBPPermissionError,
    BROADCAST_TARGET,
    create_pong,
    create_error,
)


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------

class MessagingNetworkError(Exception):
    """Base exception for the Messaging Network."""


class RateLimitExceeded(MessagingNetworkError):
    """Raised when a bot exceeds its allowed message rate."""


class BotNotConnected(MessagingNetworkError):
    """Raised when a message targets a bot that is not connected."""


# ---------------------------------------------------------------------------
# Rate limiter
# ---------------------------------------------------------------------------

class RateLimiter:
    """
    Token-bucket-style rate limiter (in-memory, minute-window).

    Parameters
    ----------
    max_messages_per_minute : int
        Maximum messages a bot may send per 60-second window.
    """

    def __init__(self, max_messages_per_minute: int = 60) -> None:
        self._limit = max_messages_per_minute
        self._windows: dict[str, deque] = defaultdict(deque)
        self._lock = threading.Lock()

    def check(self, bot_id: str) -> None:
        """
        Record a send attempt.

        Raises
        ------
        RateLimitExceeded
            If the bot has already hit the per-minute cap.
        """
        now = datetime.now(timezone.utc).timestamp()
        window_start = now - 60.0
        with self._lock:
            q = self._windows[bot_id]
            while q and q[0] < window_start:
                q.popleft()
            if len(q) >= self._limit:
                raise RateLimitExceeded(
                    f"Bot '{bot_id}' has reached the rate limit of "
                    f"{self._limit} messages/minute."
                )
            q.append(now)

    def reset(self, bot_id: str) -> None:
        """Clear the rate-limit window for a bot (admin/testing use)."""
        with self._lock:
            self._windows.pop(bot_id, None)

    def current_count(self, bot_id: str) -> int:
        """Return the number of messages sent in the current window."""
        now = datetime.now(timezone.utc).timestamp()
        window_start = now - 60.0
        with self._lock:
            q = self._windows[bot_id]
            while q and q[0] < window_start:
                q.popleft()
            return len(q)


# ---------------------------------------------------------------------------
# Delivery receipt
# ---------------------------------------------------------------------------

class DeliveryReceipt:
    """Tracks whether a message was delivered and acknowledged."""

    def __init__(self, message_id: str) -> None:
        self.message_id = message_id
        self.delivered_to: list[str] = []
        self.acknowledged_by: list[str] = []
        self.failed_for: list[str] = []
        self.timestamp: str = datetime.now(timezone.utc).isoformat()

    def mark_delivered(self, bot_id: str) -> None:
        if bot_id not in self.delivered_to:
            self.delivered_to.append(bot_id)

    def mark_ack(self, bot_id: str) -> None:
        if bot_id not in self.acknowledged_by:
            self.acknowledged_by.append(bot_id)

    def mark_failed(self, bot_id: str) -> None:
        if bot_id not in self.failed_for:
            self.failed_for.append(bot_id)

    def to_dict(self) -> dict:
        return {
            "message_id": self.message_id,
            "delivered_to": list(self.delivered_to),
            "acknowledged_by": list(self.acknowledged_by),
            "failed_for": list(self.failed_for),
            "timestamp": self.timestamp,
        }


# ---------------------------------------------------------------------------
# Messaging Network
# ---------------------------------------------------------------------------

class MessagingNetwork:
    """
    Central message broker for the DreamCo Global Bot Communication Network.

    Bots connect by calling :meth:`connect` (optionally with a callback), then
    send messages via :meth:`send`.  All traffic is logged and receipts are
    tracked.

    Parameters
    ----------
    max_messages_per_minute : int
        Default rate limit applied to every bot.
    enforce_permissions : bool
        When *True*, messages that lack the required permission flag will be
        rejected.
    max_log_size : int
        Maximum number of messages kept in the in-memory log.
    """

    def __init__(
        self,
        max_messages_per_minute: int = 60,
        enforce_permissions: bool = True,
        max_log_size: int = 10_000,
    ) -> None:
        self._max_messages_per_minute = max_messages_per_minute
        self._enforce_permissions = enforce_permissions
        self._max_log_size = max_log_size

        self._connected: dict[str, Callable | None] = {}
        self._rate_limiter = RateLimiter(max_messages_per_minute)
        self._message_log: deque[dict] = deque(maxlen=max_log_size)
        self._receipts: dict[str, DeliveryReceipt] = {}
        self._lock = threading.Lock()

    # ------------------------------------------------------------------
    # Connection management
    # ------------------------------------------------------------------

    def connect(self, bot_id: str, callback: Optional[Callable[[UBPMessage], None]] = None) -> None:
        """
        Register a bot on the network.

        Parameters
        ----------
        bot_id : str
            Unique identifier for the bot.
        callback : callable, optional
            Function called with each :class:`UBPMessage` delivered to this bot.
        """
        with self._lock:
            self._connected[bot_id] = callback

    def disconnect(self, bot_id: str) -> None:
        """Remove a bot from the network."""
        with self._lock:
            self._connected.pop(bot_id, None)

    def is_connected(self, bot_id: str) -> bool:
        """Return *True* if *bot_id* is currently connected."""
        return bot_id in self._connected

    def connected_bots(self) -> list[str]:
        """Return a list of all currently connected bot IDs."""
        return list(self._connected.keys())

    # ------------------------------------------------------------------
    # Sending
    # ------------------------------------------------------------------

    def send(self, message: UBPMessage) -> DeliveryReceipt:
        """
        Route *message* to its target(s).

        The sender is rate-limited.  If *enforce_permissions* is enabled the
        message must carry at least :attr:`Permission.WRITE` or
        :attr:`Permission.EXECUTE` for task/request types.

        Raises
        ------
        RateLimitExceeded
            If the sending bot has exceeded its rate limit.
        UBPPermissionError
            If the message violates permission constraints.
        BotNotConnected
            If the target bot is not connected (point-to-point only).
        """
        self._rate_limiter.check(message.from_bot)

        if self._enforce_permissions:
            _check_permissions(message)

        receipt = DeliveryReceipt(message.id)
        self._receipts[message.id] = receipt

        log_entry = message.to_dict()
        log_entry["_delivery_status"] = "pending"
        self._message_log.append(log_entry)

        if message.is_broadcast():
            self._deliver_broadcast(message, receipt)
        else:
            self._deliver_direct(message, receipt)

        # Update log entry status
        log_entry["_delivery_status"] = (
            "delivered" if receipt.delivered_to else "failed"
        )

        return receipt

    def _deliver_direct(self, message: UBPMessage, receipt: DeliveryReceipt) -> None:
        target = message.to_bot
        if target not in self._connected:
            receipt.mark_failed(target)
            raise BotNotConnected(
                f"Bot '{target}' is not connected to the network."
            )
        self._invoke_callback(target, message, receipt)

        # Auto-pong for ping messages
        if message.type == MessageType.PING:
            pong = create_pong(target, message.from_bot, message.id)
            if message.from_bot in self._connected:
                self._invoke_callback(message.from_bot, pong, DeliveryReceipt(pong.id))

    def _deliver_broadcast(self, message: UBPMessage, receipt: DeliveryReceipt) -> None:
        for bot_id in list(self._connected.keys()):
            if bot_id == message.from_bot:
                continue
            self._invoke_callback(bot_id, message, receipt)

    def _invoke_callback(
        self, bot_id: str, message: UBPMessage, receipt: DeliveryReceipt
    ) -> None:
        callback = self._connected.get(bot_id)
        try:
            if callable(callback):
                callback(message)
            receipt.mark_delivered(bot_id)
        except Exception as exc:  # pragma: no cover – runtime errors in bot code
            receipt.mark_failed(bot_id)
            error_entry = {
                "bot_id": bot_id,
                "message_id": message.id,
                "error": str(exc),
                "_delivery_status": "callback_error",
            }
            self._message_log.append(error_entry)

    # ------------------------------------------------------------------
    # Logs & receipts
    # ------------------------------------------------------------------

    def get_message_log(self, bot_id: Optional[str] = None) -> list[dict]:
        """
        Return the message log, optionally filtered to a single bot.

        Parameters
        ----------
        bot_id : str, optional
            If provided, return only messages sent from or to *bot_id*.
        """
        if bot_id is None:
            return list(self._message_log)
        return [
            m for m in self._message_log
            if m.get("from") == bot_id or m.get("to") in (bot_id, BROADCAST_TARGET)
        ]

    def get_receipt(self, message_id: str) -> Optional[DeliveryReceipt]:
        """Return the DeliveryReceipt for *message_id*, or *None*."""
        return self._receipts.get(message_id)

    def message_count(self) -> int:
        """Return total number of messages logged."""
        return len(self._message_log)

    def get_stats(self) -> dict:
        """Return high-level network statistics."""
        return {
            "connected_bots": len(self._connected),
            "total_messages": len(self._message_log),
            "total_receipts": len(self._receipts),
            "rate_limit_per_minute": self._max_messages_per_minute,
        }

    # ------------------------------------------------------------------
    # Admin helpers
    # ------------------------------------------------------------------

    def reset_rate_limit(self, bot_id: str) -> None:
        """Reset the rate-limit window for *bot_id* (admin use)."""
        self._rate_limiter.reset(bot_id)

    def clear_log(self) -> None:
        """Clear the in-memory message log."""
        with self._lock:
            self._message_log.clear()


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _check_permissions(message: UBPMessage) -> None:
    """
    Enforce permission requirements for specific message types.

    - TASK and REQUEST messages must carry EXECUTE permission.
    - ADMIN operations require the ADMIN permission.
    """
    if message.type in (MessageType.TASK, MessageType.REQUEST):
        if Permission.EXECUTE.value not in message.permissions:
            raise UBPPermissionError(
                f"Message type '{message.type.value}' requires "
                f"'{Permission.EXECUTE.value}' permission."
            )
