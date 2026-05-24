"""
DreamCo OS — Per-Bot Rate Limiter
====================================

Enforces per-bot API call rate limits centrally.  Uses a sliding window
counter backed by an in-process dict (upgradeable to Redis in production).

Usage::

    limiter = RateLimiter(default_calls_per_minute=60)
    limiter.check("lead_gen_bot")   # raises RateLimitExceededError if over limit
    limiter.record("lead_gen_bot")  # call after successful API call
"""

from __future__ import annotations

import time
from collections import defaultdict, deque
from typing import Any


class RateLimitExceededError(Exception):
    """Raised when a bot exceeds its configured rate limit."""


class RateLimiter:
    """Sliding-window per-bot rate limiter.

    Parameters
    ----------
    default_calls_per_minute:
        Default cap applied to all bots without a specific limit.
    bot_limits:
        Per-bot overrides: ``{"my_bot": 10}``.
    """

    def __init__(
        self,
        default_calls_per_minute: int = 60,
        bot_limits: dict[str, int] | None = None,
    ) -> None:
        self._default = default_calls_per_minute
        self._limits: dict[str, int] = bot_limits or {}
        # bot_name → deque of timestamps (sliding window)
        self._windows: dict[str, deque[float]] = defaultdict(deque)

    # ------------------------------------------------------------------
    # Configuration
    # ------------------------------------------------------------------

    def set_limit(self, bot_name: str, calls_per_minute: int) -> None:
        """Set or override the rate limit for a specific bot."""
        self._limits[bot_name] = calls_per_minute

    def get_limit(self, bot_name: str) -> int:
        return self._limits.get(bot_name, self._default)

    # ------------------------------------------------------------------
    # Enforcement
    # ------------------------------------------------------------------

    def check(self, bot_name: str) -> None:
        """Raise ``RateLimitExceededError`` if the bot is over its limit."""
        limit = self.get_limit(bot_name)
        if limit <= 0:
            return  # 0 = unlimited
        window = self._windows[bot_name]
        cutoff = time.time() - 60.0
        while window and window[0] < cutoff:
            window.popleft()
        if len(window) >= limit:
            raise RateLimitExceededError(
                f"Bot '{bot_name}' has exceeded its rate limit of "
                f"{limit} calls/minute (current: {len(window)})"
            )

    def record(self, bot_name: str) -> None:
        """Record one API call for *bot_name*."""
        self._windows[bot_name].append(time.time())

    def check_and_record(self, bot_name: str) -> None:
        """Check then record — the typical call pattern."""
        self.check(bot_name)
        self.record(bot_name)

    # ------------------------------------------------------------------
    # Introspection
    # ------------------------------------------------------------------

    def current_count(self, bot_name: str) -> int:
        """Return the number of calls made in the last minute."""
        window = self._windows[bot_name]
        cutoff = time.time() - 60.0
        return sum(1 for ts in window if ts >= cutoff)

    def stats(self) -> dict[str, Any]:
        return {
            bot: {
                "limit": self.get_limit(bot),
                "current_count": self.current_count(bot),
            }
            for bot in self._windows
        }
