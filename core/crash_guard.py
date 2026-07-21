"""CrashGuard: decorator and context manager for safe bot execution."""
import logging
import traceback
from contextlib import contextmanager
from typing import Callable, TypeVar

logger = logging.getLogger(__name__)

F = TypeVar("F", bound=Callable)


def crash_guard(func: F) -> F:
    """Decorator that catches exceptions, logs them, and prevents hard crashes."""

    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as exc:
            logger.error(
                "CrashGuard caught exception in '%s': %s\n%s",
                func.__name__,
                exc,
                traceback.format_exc(),
            )
            return None

    wrapper.__name__ = func.__name__
    wrapper.__doc__ = func.__doc__
    return wrapper  # type: ignore[return-value]


@contextmanager
def safe_run(label: str = "operation"):
    """Context manager that catches and logs exceptions without re-raising."""
    try:
        yield
    except Exception as exc:
        logger.error(
            "CrashGuard [%s] caught exception: %s\n%s",
            label,
            exc,
            traceback.format_exc(),
        )
