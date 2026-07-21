"""
DreamCobots — Structured Logging

Provides JSON-structured, leveled logging for every bot.
Each log record includes:
  - timestamp (ISO-8601 UTC)
  - level
  - bot_name
  - message
  - extra context fields (optional)

Usage::

    from bots.utils.logger import get_logger

    log = get_logger("my_bot")
    log.info("Bot started", tier="PRO", user_id="u123")
    log.error("API call failed", endpoint="/v1/chat", status_code=429)
"""

from __future__ import annotations

import json
import logging
import os
import sys
from datetime import datetime, timezone
from typing import Any


# ── Custom JSON formatter ─────────────────────────────────────────────────────

class _JsonFormatter(logging.Formatter):
    """Emit log records as single-line JSON objects."""

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "bot": getattr(record, "bot_name", record.name),
            "message": record.getMessage(),
        }

        # Merge any extra context fields attached by BotLogger._log
        for key, val in record.__dict__.items():
            if key.startswith("ctx_"):
                payload[key[4:]] = val

        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)

        return json.dumps(payload, default=str)


# ── BotLogger wrapper ─────────────────────────────────────────────────────────

class BotLogger:
    """Thin wrapper around :class:`logging.Logger` with structured context.

    Parameters
    ----------
    bot_name:
        Human-readable name shown in every log record (e.g. ``"sales_bot"``).
    level:
        Minimum log level.  Defaults to the ``LOG_LEVEL`` environment
        variable, falling back to ``"INFO"``.
    """

    def __init__(self, bot_name: str, level: str | None = None) -> None:
        self.bot_name = bot_name
        effective_level = (
            level
            or os.environ.get("LOG_LEVEL", "INFO")
        ).upper()

        self._logger = logging.getLogger(f"dreamco.{bot_name}")
        if not self._logger.handlers:
            handler = logging.StreamHandler(sys.stdout)
            handler.setFormatter(_JsonFormatter())
            self._logger.addHandler(handler)
            self._logger.propagate = False

        self._logger.setLevel(effective_level)

    # ── Public helpers ────────────────────────────────────────────────────────

    def debug(self, message: str, **ctx: Any) -> None:
        self._log(logging.DEBUG, message, **ctx)

    def info(self, message: str, **ctx: Any) -> None:
        self._log(logging.INFO, message, **ctx)

    def warning(self, message: str, **ctx: Any) -> None:
        self._log(logging.WARNING, message, **ctx)

    def error(self, message: str, **ctx: Any) -> None:
        self._log(logging.ERROR, message, **ctx)

    def critical(self, message: str, **ctx: Any) -> None:
        self._log(logging.CRITICAL, message, **ctx)

    # ── Internal ──────────────────────────────────────────────────────────────

    def _log(self, level: int, message: str, **ctx: Any) -> None:
        extra = {f"ctx_{k}": v for k, v in ctx.items()}
        extra["bot_name"] = self.bot_name
        self._logger.log(level, message, extra=extra, stacklevel=3)


# ── Module-level convenience factory ─────────────────────────────────────────

def get_logger(bot_name: str, level: str | None = None) -> BotLogger:
    """Return a :class:`BotLogger` for *bot_name*.

    Parameters
    ----------
    bot_name:
        Identifies the bot in every log line.
    level:
        Optional override for the log level (``DEBUG``, ``INFO``, …).
    """
    return BotLogger(bot_name, level=level)
