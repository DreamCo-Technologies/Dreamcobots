"""
Tests for bots/utils/ — structured logging and error handling utilities.
"""

import json
import os
import sys
import time

import pytest

REPO_ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, REPO_ROOT)

from bots.utils.logger import get_logger, BotLogger, _JsonFormatter  # noqa: E402
from bots.utils.error_handler import (  # noqa: E402
    BotError,
    TierError,
    ValidationError,
    APIError,
    retry,
    safe_run,
)


# ─────────────────────────────────────────────────────────────────────────────
# Logger tests
# ─────────────────────────────────────────────────────────────────────────────

class TestGetLogger:
    def test_returns_bot_logger_instance(self):
        log = get_logger("test_bot")
        assert isinstance(log, BotLogger)

    def test_bot_name_stored(self):
        log = get_logger("my_bot")
        assert log.bot_name == "my_bot"

    def test_level_default_info(self):
        log = get_logger("level_bot")
        import logging
        assert log._logger.level == logging.INFO

    def test_level_override(self):
        log = get_logger("debug_bot", level="DEBUG")
        import logging
        assert log._logger.level == logging.DEBUG

    def test_get_logger_same_bot_reuses_underlying_logger(self):
        a = get_logger("shared_bot")
        b = get_logger("shared_bot")
        assert a._logger is b._logger


class TestBotLoggerOutput:
    """Verify that log output is valid JSON with expected keys."""

    def _capture_line(self, capsys, log, method, message, **ctx):
        getattr(log, method)(message, **ctx)
        captured = capsys.readouterr()
        return json.loads(captured.out.strip())

    def test_info_emits_json(self, capsys):
        log = get_logger("json_bot")
        record = self._capture_line(capsys, log, "info", "hello world")
        assert record["message"] == "hello world"
        assert record["level"] == "INFO"
        assert record["bot"] == "json_bot"
        assert "timestamp" in record

    def test_error_level(self, capsys):
        log = get_logger("err_bot")
        record = self._capture_line(capsys, log, "error", "something broke")
        assert record["level"] == "ERROR"

    def test_context_fields_included(self, capsys):
        log = get_logger("ctx_bot")
        record = self._capture_line(
            capsys, log, "info", "ctx test", tier="PRO", user_id="u99"
        )
        assert record.get("tier") == "PRO"
        assert record.get("user_id") == "u99"

    def test_warning_level(self, capsys):
        log = get_logger("warn_bot")
        record = self._capture_line(capsys, log, "warning", "watch out")
        assert record["level"] == "WARNING"

    def test_debug_below_info_not_emitted(self, capsys):
        log = get_logger("silent_bot")  # default INFO level
        log.debug("this should be silent")
        captured = capsys.readouterr()
        assert captured.out.strip() == ""


# ─────────────────────────────────────────────────────────────────────────────
# BotError tests
# ─────────────────────────────────────────────────────────────────────────────

class TestBotError:
    def test_basic_instantiation(self):
        err = BotError("something went wrong", bot_name="test_bot")
        assert str(err) == "something went wrong"
        assert err.bot_name == "test_bot"

    def test_default_bot_name(self):
        err = BotError("oops")
        assert err.bot_name == "unknown"

    def test_context_stored(self):
        err = BotError("ctx error", context={"tier": "PRO", "code": 429})
        assert err.context["tier"] == "PRO"
        assert err.context["code"] == 429

    def test_repr_includes_fields(self):
        err = BotError("bad", bot_name="sales_bot", context={"k": "v"})
        r = repr(err)
        assert "sales_bot" in r
        assert "bad" in r

    def test_tier_error_is_bot_error(self):
        err = TierError("limit exceeded", bot_name="sales_bot")
        assert isinstance(err, BotError)

    def test_validation_error_is_bot_error(self):
        err = ValidationError("invalid input")
        assert isinstance(err, BotError)

    def test_api_error_is_bot_error(self):
        err = APIError("upstream failure")
        assert isinstance(err, BotError)


# ─────────────────────────────────────────────────────────────────────────────
# retry decorator tests
# ─────────────────────────────────────────────────────────────────────────────

class TestRetry:
    def test_succeeds_on_first_attempt(self):
        calls = []

        @retry(max_attempts=3, delay=0.0)
        def fn():
            calls.append(1)
            return "ok"

        result = fn()
        assert result == "ok"
        assert len(calls) == 1

    def test_retries_on_specified_exception(self):
        calls = []

        @retry(max_attempts=3, delay=0.0, exceptions=(ValueError,))
        def fn():
            calls.append(1)
            if len(calls) < 3:
                raise ValueError("not ready")
            return "done"

        result = fn()
        assert result == "done"
        assert len(calls) == 3

    def test_raises_after_max_attempts(self):
        @retry(max_attempts=2, delay=0.0, exceptions=(RuntimeError,))
        def always_fails():
            raise RuntimeError("always")

        with pytest.raises(RuntimeError):
            always_fails()

    def test_does_not_retry_unexpected_exception(self):
        calls = []

        @retry(max_attempts=5, delay=0.0, exceptions=(ValueError,))
        def fn():
            calls.append(1)
            raise TypeError("unexpected")

        with pytest.raises(TypeError):
            fn()
        assert len(calls) == 1

    def test_backoff_increases_delay(self):
        """Verify that total delay is consistent with backoff multiplier."""
        call_times = []

        @retry(max_attempts=3, delay=0.01, backoff=2.0, exceptions=(OSError,))
        def fn():
            call_times.append(time.perf_counter())
            raise OSError("err")

        with pytest.raises(OSError):
            fn()

        assert len(call_times) == 3
        gap1 = call_times[1] - call_times[0]
        gap2 = call_times[2] - call_times[1]
        assert gap2 >= gap1 * 1.5, "Expected exponential backoff"

    def test_preserves_function_name(self):
        @retry(max_attempts=1, delay=0.0)
        def my_function():
            pass

        assert my_function.__name__ == "my_function"


# ─────────────────────────────────────────────────────────────────────────────
# safe_run decorator tests
# ─────────────────────────────────────────────────────────────────────────────

class TestSafeRun:
    def test_returns_result_on_success(self):
        @safe_run(fallback="FALLBACK")
        def fn():
            return "real_value"

        assert fn() == "real_value"

    def test_returns_fallback_on_exception(self):
        @safe_run(fallback=42, log_errors=False)
        def fn():
            raise RuntimeError("oops")

        assert fn() == 42

    def test_fallback_none_by_default(self):
        @safe_run(log_errors=False)
        def fn():
            raise KeyError("missing")

        assert fn() is None

    def test_does_not_raise(self):
        @safe_run(fallback=-1, log_errors=False)
        def fn():
            raise SystemError("bad")

        result = fn()
        assert result == -1

    def test_preserves_function_name(self):
        @safe_run()
        def compute_value():
            return 1

        assert compute_value.__name__ == "compute_value"

    def test_passes_args_and_kwargs(self):
        @safe_run(fallback=0)
        def add(a, b, *, multiplier=1):
            return (a + b) * multiplier

        assert add(2, 3, multiplier=4) == 20
