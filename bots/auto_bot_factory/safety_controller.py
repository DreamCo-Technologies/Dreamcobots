"""
Safety Controller — enforces global limits (MAX_BOTS=200, MAX_MESSAGES_PER_CYCLE=10)
and provides self-healing crash recovery for the Auto-Bot Factory.

Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.
See framework/global_ai_sources_flow.py for the full pipeline specification.
"""

from __future__ import annotations

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from framework import GlobalAISourcesFlow  # noqa: F401  (GLOBAL AI SOURCES FLOW)

from datetime import datetime, timezone
from typing import Any, Optional


# ---------------------------------------------------------------------------
# Global safety limits
# ---------------------------------------------------------------------------

MAX_BOTS: int = 200
MAX_MESSAGES_PER_CYCLE: int = 10


class SafetyLimitError(Exception):
    """Raised when a safety limit is exceeded."""


# ---------------------------------------------------------------------------
# Safety Controller
# ---------------------------------------------------------------------------

class SafetyController:
    """
    Enforces global limits and provides self-healing crash recovery.

    Parameters
    ----------
    max_bots : int
        Maximum number of active bots (default: 200).
    max_messages_per_cycle : int
        Maximum messages sent per cycle (default: 10).
    """

    def __init__(
        self,
        max_bots: int = MAX_BOTS,
        max_messages_per_cycle: int = MAX_MESSAGES_PER_CYCLE,
    ) -> None:
        self.max_bots = max_bots
        self.max_messages_per_cycle = max_messages_per_cycle
        self._bot_count: int = 0
        self._bots: dict[str, Any] = {}
        self._message_count_this_cycle: int = 0
        self._crash_log: list[dict] = []
        self._removed_bots: list[str] = []
        self._health_log: list[dict] = []

    # ------------------------------------------------------------------
    # Bot registration and limits
    # ------------------------------------------------------------------

    def register_bot(self, name: str, bot: Any) -> None:
        """Register a bot. Raises SafetyLimitError if bot limit reached."""
        if self._bot_count >= self.max_bots:
            raise SafetyLimitError(
                f"🚫 Bot limit ({self.max_bots}) reached. "
                "Cannot register more bots."
            )
        self._bots[name] = bot
        self._bot_count += 1
        self._log_health(name, "registered")

    def unregister_bot(self, name: str) -> bool:
        """Unregister and remove a bot by name. Returns True if removed."""
        if name in self._bots:
            del self._bots[name]
            self._bot_count = max(0, self._bot_count - 1)
            self._removed_bots.append(name)
            self._log_health(name, "unregistered")
            return True
        return False

    def check_bot_limit(self) -> bool:
        """Return True if bot limit has NOT been reached."""
        return self._bot_count < self.max_bots

    def get_bot_count(self) -> int:
        return self._bot_count

    def list_bots(self) -> list[str]:
        return list(self._bots.keys())

    # ------------------------------------------------------------------
    # Message rate limiting
    # ------------------------------------------------------------------

    def reset_message_cycle(self) -> None:
        """Reset the message counter for a new cycle."""
        self._message_count_this_cycle = 0

    def check_message_limit(self) -> bool:
        """Return True if messages can still be sent this cycle."""
        return self._message_count_this_cycle < self.max_messages_per_cycle

    def record_message_sent(self) -> bool:
        """
        Record a sent message. Returns True if allowed, False if limit reached.
        """
        if self._message_count_this_cycle >= self.max_messages_per_cycle:
            return False
        self._message_count_this_cycle += 1
        return True

    def get_messages_sent_this_cycle(self) -> int:
        return self._message_count_this_cycle

    def get_messages_remaining(self) -> int:
        return max(0, self.max_messages_per_cycle - self._message_count_this_cycle)

    # ------------------------------------------------------------------
    # Self-healing
    # ------------------------------------------------------------------

    def run_bot_safe(self, name: str, bot: Any) -> str:
        """
        Run a bot's run() method safely, removing it on crash.

        Parameters
        ----------
        name : str
            Bot identifier.
        bot : Any
            Bot instance with a run() method.

        Returns
        -------
        str
            Result string from the bot, or an error/removal message.
        """
        try:
            result = bot.run()
            self._log_health(name, "run_ok")
            return result
        except Exception as exc:
            error_msg = str(exc)
            self._crash_log.append({
                "bot": name,
                "error": error_msg,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            })
            removed = self.unregister_bot(name)
            action = "removed broken bot" if removed else "bot not found for removal"
            self._log_health(name, f"crashed_and_{action}: {error_msg}")
            return f"❌ {name} crashed: {error_msg}. {action}"

    # ------------------------------------------------------------------
    # Reporting
    # ------------------------------------------------------------------

    def get_crash_log(self) -> list[dict]:
        return list(self._crash_log)

    def get_removed_bots(self) -> list[str]:
        return list(self._removed_bots)

    def get_health_log(self) -> list[dict]:
        return list(self._health_log)

    def get_status(self) -> dict:
        return {
            "bot_count": self._bot_count,
            "max_bots": self.max_bots,
            "bot_limit_reached": self._bot_count >= self.max_bots,
            "messages_sent_this_cycle": self._message_count_this_cycle,
            "max_messages_per_cycle": self.max_messages_per_cycle,
            "message_limit_reached": self._message_count_this_cycle >= self.max_messages_per_cycle,
            "messages_remaining": self.get_messages_remaining(),
            "crash_count": len(self._crash_log),
            "removed_bots": self._removed_bots,
            "active_bots": self.list_bots(),
        }

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _log_health(self, name: str, event: str) -> None:
        self._health_log.append({
            "bot": name,
            "event": event,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })
