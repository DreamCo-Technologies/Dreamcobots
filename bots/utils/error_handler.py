"""
DreamCobots — Centralized Error Handling

Provides:
  - ``BotError`` — base exception class with context metadata.
  - ``retry`` — decorator that retries a function on transient errors.
  - ``safe_run`` — decorator / context-manager that catches all exceptions,
    logs them, and returns a fallback value instead of propagating.

Usage::

    from bots.utils.error_handler import BotError, retry, safe_run

    @retry(max_attempts=3, delay=1.0, exceptions=(ConnectionError,))
    def fetch_data(url: str) -> dict:
        ...

    @safe_run(fallback=None)
    def risky_operation() -> str:
        ...
"""

from __future__ import annotations

import functools
import time
import traceback
from typing import Any, Callable, Sequence, Type, TypeVar

F = TypeVar("F", bound=Callable[..., Any])


# ── Base exception ────────────────────────────────────────────────────────────

class BotError(Exception):
    """Base exception for all DreamCo bot errors.

    Parameters
    ----------
    message:
        Human-readable error description.
    bot_name:
        Name of the bot that raised the error.
    context:
        Arbitrary key-value metadata (e.g., ``{"tier": "PRO", "user_id": "x"}``).
    """

    def __init__(
        self,
        message: str,
        bot_name: str = "unknown",
        context: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.bot_name = bot_name
        self.context: dict[str, Any] = context or {}

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"bot={self.bot_name!r}, "
            f"message={str(self)!r}, "
            f"context={self.context!r})"
        )


class TierError(BotError):
    """Raised when an operation exceeds the bot's subscription tier limits."""


class ValidationError(BotError):
    """Raised when input data fails validation checks."""


class APIError(BotError):
    """Raised when an upstream API call fails."""


# ── retry decorator ───────────────────────────────────────────────────────────

def retry(
    max_attempts: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: Sequence[Type[Exception]] = (Exception,),
) -> Callable[[F], F]:
    """Retry *func* up to *max_attempts* times on transient failures.

    Parameters
    ----------
    max_attempts:
        Total number of attempts (including the first call).
    delay:
        Seconds to wait before the first retry.
    backoff:
        Multiplier applied to *delay* after each failed attempt.
    exceptions:
        Tuple of exception types that trigger a retry.  Any other
        exception is re-raised immediately.
    """

    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            wait = delay
            last_exc: Exception | None = None
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except tuple(exceptions) as exc:  # type: ignore[arg-type]
                    last_exc = exc
                    if attempt < max_attempts:
                        time.sleep(wait)
                        wait *= backoff
            raise last_exc  # type: ignore[misc]

        return wrapper  # type: ignore[return-value]

    return decorator


# ── safe_run decorator ────────────────────────────────────────────────────────

def safe_run(
    fallback: Any = None,
    log_errors: bool = True,
) -> Callable[[F], F]:
    """Wrap *func* so it never raises — instead returns *fallback* on error.

    Parameters
    ----------
    fallback:
        Value returned when *func* raises any exception.
    log_errors:
        When ``True`` (default) print the traceback to stderr so the error
        is visible in structured logs without crashing the caller.
    """

    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                return func(*args, **kwargs)
            except Exception:
                if log_errors:
                    traceback.print_exc()
                return fallback

        return wrapper  # type: ignore[return-value]

    return decorator
