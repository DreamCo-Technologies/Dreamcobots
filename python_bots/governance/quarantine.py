"""
DreamCo OS — Quarantine Manager
=================================

Moves misbehaving bots to a quarantine state, logs the reason, and
provides operator tools to inspect and release quarantined bots.
"""

from __future__ import annotations

import time
from typing import Any


class QuarantineManager:
    """Manages bot quarantine state and release workflows.

    Parameters
    ----------
    audit_log:
        Optional governance audit log for recording quarantine events.
    """

    def __init__(self, audit_log: Any = None) -> None:
        self._audit = audit_log
        self._quarantined: dict[str, dict[str, Any]] = {}  # bot_name → record

    def quarantine(self, bot_name: str, reason: str, bot: Any = None) -> None:
        """Move *bot_name* into quarantine and log the reason."""
        record = {
            "bot_name": bot_name,
            "reason": reason,
            "quarantined_at": time.time(),
            "released_at": None,
        }
        self._quarantined[bot_name] = record

        if bot is not None and hasattr(bot, "_state"):
            from python_bots.core.lifecycle import BotState
            bot._state = BotState.QUARANTINED

        if self._audit:
            self._audit.record(
                actor="orchestrator",
                action="bot.quarantined",
                resource=bot_name,
                outcome="success",
                metadata={"reason": reason},
            )

    def release(self, bot_name: str, operator: str = "system") -> bool:
        """Release a bot from quarantine.  Returns True if it was quarantined."""
        record = self._quarantined.get(bot_name)
        if record is None:
            return False
        record["released_at"] = time.time()
        record["released_by"] = operator
        del self._quarantined[bot_name]

        if self._audit:
            self._audit.record(
                actor=operator,
                action="bot.released_from_quarantine",
                resource=bot_name,
                outcome="success",
            )
        return True

    def is_quarantined(self, bot_name: str) -> bool:
        return bot_name in self._quarantined

    def list_quarantined(self) -> list[dict[str, Any]]:
        return list(self._quarantined.values())

    def quarantine_count(self) -> int:
        return len(self._quarantined)
