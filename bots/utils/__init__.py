"""
DreamCobots — Shared Utilities Package

Provides structured logging, centralized error handling, and
performance metrics helpers for all bots.
"""

from .logger import get_logger, BotLogger
from .error_handler import BotError, retry, safe_run

__all__ = [
    "get_logger",
    "BotLogger",
    "BotError",
    "retry",
    "safe_run",
]
