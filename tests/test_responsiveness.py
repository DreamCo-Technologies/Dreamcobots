"""
Bot responsiveness benchmarks.

These tests measure response times for bot operations and assert they stay
within the defined threshold.  The pytest-benchmark plugin is used to collect
statistics across multiple rounds.

Run standalone:
    pytest tests/test_responsiveness.py --benchmark-min-rounds=5 -v
"""
import importlib.util
import os
import time

import pytest

# ---------------------------------------------------------------------------
# Threshold configuration
# ---------------------------------------------------------------------------

RESPONSE_TIME_THRESHOLD_MS = 500  # maximum acceptable mean response time


# ---------------------------------------------------------------------------
# Module-level bot loading (avoids repeated I/O inside each test)
# ---------------------------------------------------------------------------

_REPO_ROOT = os.path.join(os.path.dirname(__file__), "..")
_GOV_BOT_PATH = os.path.join(
    _REPO_ROOT,
    "bots",
    "government-contract-grant-bot",
    "government_contract_grant_bot.py",
)
_spec = importlib.util.spec_from_file_location("government_contract_grant_bot", _GOV_BOT_PATH)
_gov_bot_module = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_gov_bot_module)
GovernmentContractGrantBot = _gov_bot_module.GovernmentContractGrantBot


# ---------------------------------------------------------------------------
# Benchmark tests
# ---------------------------------------------------------------------------

def test_gov_bot_initialization_time(benchmark):
    """GovernmentContractGrantBot should initialize within the response threshold."""
    result = benchmark(GovernmentContractGrantBot)
    assert result is not None
    mean_ms = benchmark.stats["mean"] * 1000
    assert mean_ms < RESPONSE_TIME_THRESHOLD_MS, (
        f"Bot initialization took {mean_ms:.2f} ms, "
        f"exceeding the {RESPONSE_TIME_THRESHOLD_MS} ms threshold"
    )


def test_gov_bot_run_time(benchmark, capsys):
    """GovernmentContractGrantBot.run() should complete within the response threshold."""

    def _run():
        bot = GovernmentContractGrantBot()
        bot.run()

    benchmark(_run)
    mean_ms = benchmark.stats["mean"] * 1000
    assert mean_ms < RESPONSE_TIME_THRESHOLD_MS, (
        f"Bot run() took {mean_ms:.2f} ms, "
        f"exceeding the {RESPONSE_TIME_THRESHOLD_MS} ms threshold"
    )


def test_gov_bot_process_contracts_time(benchmark, capsys):
    """process_contracts() should complete within the response threshold."""
    bot = GovernmentContractGrantBot()

    benchmark(bot.process_contracts)
    mean_ms = benchmark.stats["mean"] * 1000
    assert mean_ms < RESPONSE_TIME_THRESHOLD_MS, (
        f"process_contracts() took {mean_ms:.2f} ms, "
        f"exceeding the {RESPONSE_TIME_THRESHOLD_MS} ms threshold"
    )


def test_gov_bot_process_grants_time(benchmark, capsys):
    """process_grants() should complete within the response threshold."""
    bot = GovernmentContractGrantBot()

    benchmark(bot.process_grants)
    mean_ms = benchmark.stats["mean"] * 1000
    assert mean_ms < RESPONSE_TIME_THRESHOLD_MS, (
        f"process_grants() took {mean_ms:.2f} ms, "
        f"exceeding the {RESPONSE_TIME_THRESHOLD_MS} ms threshold"
    )


# ---------------------------------------------------------------------------
# Direct timing test (no benchmark fixture – always runs)
# ---------------------------------------------------------------------------

def test_bot_response_time_direct():
    """Direct wall-clock check: initialisation + run must be under threshold."""
    start = time.perf_counter()
    bot = GovernmentContractGrantBot()
    bot.run()
    elapsed_ms = (time.perf_counter() - start) * 1000
    assert elapsed_ms < RESPONSE_TIME_THRESHOLD_MS, (
        f"End-to-end bot response took {elapsed_ms:.2f} ms, "
        f"exceeding the {RESPONSE_TIME_THRESHOLD_MS} ms threshold"
    )
