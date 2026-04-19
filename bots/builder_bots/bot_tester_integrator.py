# Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.
"""
Bot Tester & Integrator

Provides automated end-to-end testing and cross-bot integration:

  Phase 1 — Foundation
    • Runs health-check probes against each builder bot's run() contract.
    • Reports per-bot pass/fail status and elapsed time.
    • Stamps milestones via TimestampButton.

  Phase 2 — Placeholders & Ideation
    • Scaffolds placeholder test suites for future bot categories.
    • Logs testing-domain bot ideas to bot_ideas_log.txt.

Adheres to the DreamCobots GLOBAL AI SOURCES FLOW framework.
"""

from __future__ import annotations

import time
import traceback
import uuid
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from core.timestamp_button import TimestampButton
from bots.builder_bots._shared import append_bot_ideas


# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------


@dataclass
class TestResult:
    """Result of a single bot integration health check."""

    test_id: str
    bot_name: str
    passed: bool
    elapsed_ms: float
    result: Any = None
    error: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "test_id": self.test_id,
            "bot_name": self.bot_name,
            "passed": self.passed,
            "elapsed_ms": self.elapsed_ms,
            "result": self.result,
            "error": self.error,
        }


# ---------------------------------------------------------------------------
# BotTesterIntegrator
# ---------------------------------------------------------------------------


class BotTesterIntegrator:
    """
    Builder bot responsible for automated testing and integration checks.

    Parameters
    ----------
    timestamp_button : TimestampButton | None
        Shared milestone tracker.
    """

    bot_id = "bot_tester_integrator"
    name = "Bot Tester & Integrator"
    category = "builder"

    PLACEHOLDER_TEMPLATES: List[str] = [
        "load_testing_pipeline_placeholder",
        "canary_deployment_test_placeholder",
        "integration_regression_suite_placeholder",
        "performance_benchmark_placeholder",
        "chaos_engineering_placeholder",
    ]

    BOT_IDEAS: List[str] = [
        "SyntheticMonitorBot — runs scheduled synthetic transactions to verify bot health",
        "ChaosMonkeyBot — randomly disables non-critical bots to test resilience",
        "LoadSimulatorBot — generates artificial traffic to stress-test pipelines",
        "CoverageTrackerBot — measures test-coverage deltas across bot code changes",
        "CanaryDeployerBot — gradually rolls out new bot versions to a small user segment",
        "AlertDispatcherBot — pages on-call when bot error rate exceeds thresholds",
    ]

    def __init__(self, timestamp_button: Optional[TimestampButton] = None) -> None:
        self._ts = timestamp_button or TimestampButton()
        self._results: List[TestResult] = []

    # ------------------------------------------------------------------
    # Phase 1: Foundation — health-check probes
    # ------------------------------------------------------------------

    def probe_bot(self, bot: Any, task: dict | None = None) -> TestResult:
        """
        Run a single health-check probe against *bot*.

        The probe calls ``bot.run(task)`` and verifies the return value is
        a dict with a ``"status"`` key.
        """
        test_id = str(uuid.uuid4())[:8]
        bot_name = getattr(bot, "name", type(bot).__name__)
        start = time.monotonic()
        try:
            result = bot.run(task or {})
            elapsed = round((time.monotonic() - start) * 1000, 2)
            passed = isinstance(result, dict) and "status" in result
            tr = TestResult(
                test_id=test_id,
                bot_name=bot_name,
                passed=passed,
                elapsed_ms=elapsed,
                result=result if passed else None,
                error=None if passed else f"Invalid run() return: {result!r}",
            )
        except Exception as exc:  # noqa: BLE001  # probed bots may raise any exception type
            elapsed = round((time.monotonic() - start) * 1000, 2)
            tr = TestResult(
                test_id=test_id,
                bot_name=bot_name,
                passed=False,
                elapsed_ms=elapsed,
                error=f"{type(exc).__name__}: {exc}\n{traceback.format_exc()}",
            )

        self._results.append(tr)
        self._ts.stamp(
            event="bot_probe_completed",
            detail=f"bot={bot_name} passed={tr.passed}",
            bot=self.name,
        )
        return tr

    def probe_all(self, bots: List[Any], task: dict | None = None) -> List[TestResult]:
        """Probe every bot in *bots* and return the list of TestResult objects."""
        return [self.probe_bot(b, task) for b in bots]

    def summary(self) -> Dict[str, Any]:
        """Return an aggregated pass/fail summary of all probes so far."""
        passed = sum(1 for r in self._results if r.passed)
        failed = len(self._results) - passed
        return {
            "total": len(self._results),
            "passed": passed,
            "failed": failed,
            "results": [r.to_dict() for r in self._results],
        }

    # ------------------------------------------------------------------
    # Phase 2: Placeholders & ideation
    # ------------------------------------------------------------------

    def generate_placeholders(self) -> List[str]:
        """Return scaffold template names for future test suites."""
        self._ts.stamp(
            event="test_placeholders_generated",
            detail=f"{len(self.PLACEHOLDER_TEMPLATES)} templates",
            bot=self.name,
        )
        return list(self.PLACEHOLDER_TEMPLATES)

    def log_bot_ideas(self, log_path: str = "bot_ideas_log.txt") -> None:
        """Append testing-domain bot ideas to bot_ideas_log.txt."""
        append_bot_ideas(log_path, self.name, self.BOT_IDEAS)
        self._ts.stamp(event="bot_ideas_logged", detail=f"section={self.name}", bot=self.name)

    # ------------------------------------------------------------------
    # Unified run()
    # ------------------------------------------------------------------

    def run(self, task: dict | None = None) -> dict:
        """
        Execute the tester's own lifecycle:
        1. Probe any bots provided in task["bots"] (list of bot instances).
        2. Generate placeholders.
        3. Log bot ideas.
        """
        task = task or {}
        bots_to_probe = task.get("bots", [])
        probe_results = self.probe_all(bots_to_probe)

        # Phase 2
        placeholders = self.generate_placeholders()
        self.log_bot_ideas(task.get("ideas_log", "bot_ideas_log.txt"))

        return {
            "status": "success",
            "bot": self.name,
            "probe_summary": self.summary(),
            "placeholders": placeholders,
        }
