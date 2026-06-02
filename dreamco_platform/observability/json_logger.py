"""Structured JSON logging for DreamCo services."""

from __future__ import annotations

import logging
import os
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Any

from pythonjsonlogger.json import JsonFormatter


class DreamCoJsonFormatter(JsonFormatter):
    """Inject DreamCo logging fields for downstream observability tools."""

    def add_fields(self, log_record: dict[str, Any], record: logging.LogRecord, message_dict: dict[str, Any]) -> None:
        super().add_fields(log_record, record, message_dict)
        log_record.setdefault("timestamp", self.formatTime(record, self.datefmt))
        log_record.setdefault("level", record.levelname)
        log_record.setdefault("service", getattr(record, "service", os.getenv("DREAMCO_SERVICE", "dreamco")))
        log_record.setdefault("bot_id", getattr(record, "bot_id", "system"))
        log_record.setdefault("trace_id", getattr(record, "trace_id", ""))
        log_record.setdefault("message", record.getMessage())


def _build_handler(log_path: Path) -> RotatingFileHandler:
    handler = RotatingFileHandler(log_path, maxBytes=5_000_000, backupCount=5)
    handler.setFormatter(DreamCoJsonFormatter())
    return handler


def get_logger(name: str, bot_id: str | None = None) -> logging.LoggerAdapter:
    """Return a logger configured with JSON stream and rotating file handlers."""
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(os.getenv("LOG_LEVEL", "INFO").upper())
        logger.propagate = False
        logs_dir = Path(os.getenv("DREAMCO_LOG_DIR", "logs"))
        logs_dir.mkdir(parents=True, exist_ok=True)
        file_handler = _build_handler(logs_dir / f"{name}.log")
        stream_handler = logging.StreamHandler()
        formatter = DreamCoJsonFormatter()
        stream_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        logger.addHandler(stream_handler)

    class BotLoggerAdapter(logging.LoggerAdapter):
        def process(self, msg: str, kwargs: dict[str, Any]):
            extra = kwargs.setdefault("extra", {})
            extra.setdefault("bot_id", bot_id or "system")
            extra.setdefault("service", os.getenv("DREAMCO_SERVICE", name))
            return msg, kwargs

    return BotLoggerAdapter(logger, {"bot_id": bot_id or "system"})
