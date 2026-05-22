"""
DreamCo Sandbox Builder Bot

Automatically discovers every bot in the repository, sets up an isolated
sandbox environment for each one, runs a configurable test suite, and
produces a client-facing performance report.

Responsibilities
----------------
1. Discover all bot modules under a configurable root directory.
2. Dynamically instantiate each :class:`~core.bot_base.BotBase` subclass.
3. Run the :class:`~sandbox.sandbox.SandboxTester` (military-grade scenarios)
   and the :class:`~sandbox.performance_rating.PerformanceRatingSystem` on
   every bot.
4. Aggregate results into a :class:`~sandbox.report_generator.SandboxReportGenerator`
   and write both a plain-text and JSON report.

The bot itself is a :class:`~core.bot_base.BotBase` subclass so it exposes
``start()`` / ``stop()`` lifecycle methods and can be wired into the
DreamCo orchestrator.
"""

from __future__ import annotations

import importlib
import inspect
import logging
import os
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Type

from core.bot_base import BotBase
from sandbox.performance_rating import (
    COMPLEXITY_WEIGHTS,
    PerformanceRatingSystem,
    TaskResult,
)
from sandbox.report_generator import SandboxReportGenerator
from sandbox.sandbox import Scenario, SandboxTester


logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Default scenarios used for every bot under test
# ---------------------------------------------------------------------------

_DEFAULT_SCENARIOS: List[Scenario] = [
    Scenario(
        name="basic_task",
        description="Simple generic task — verifies the bot can execute any workload",
        task={"type": "generic"},
        expected_status="ok",
        timeout_seconds=5.0,
    ),
    Scenario(
        name="validated_task",
        description="Task with human-confirmation flag set — semi-autonomous path",
        task={"type": "generic", "validated": True},
        expected_status="ok",
        timeout_seconds=5.0,
    ),
    Scenario(
        name="stress_spike",
        description="High-frequency burst to probe throughput limits",
        task={"type": "stress"},
        expected_status="ok",
        timeout_seconds=10.0,
    ),
]

# Complexity tiers assigned per scenario name for the rating system
_SCENARIO_COMPLEXITY: Dict[str, str] = {
    "basic_task": "easy",
    "validated_task": "medium",
    "stress_spike": "hard",
}


# ---------------------------------------------------------------------------
# SandboxBuilderBot
# ---------------------------------------------------------------------------


class SandboxBuilderBot(BotBase):
    """
    Discovers all bots in the repository, builds an isolated sandbox for
    each one, runs standardised test scenarios, and emits a performance
    report with star ratings.

    Parameters
    ----------
    bots_root : str | Path
        Root directory to search for bot modules (defaults to the ``bots/``
        directory at the repository root).
    iterations : int
        Number of iterations per scenario per bot (default 50).
    test_duration_hours : float
        Displayed in the report header; does NOT control real wall-clock time
        (the CI workflow handles the 24-hour gate).
    report_dir : str | Path
        Directory where report files are written.  Defaults to ``logs/``.
    extra_scenarios : list[Scenario] | None
        Additional :class:`~sandbox.sandbox.Scenario` objects to run on
        every bot in addition to the defaults.
    """

    def __init__(
        self,
        bots_root: Optional[str] = None,
        iterations: int = 50,
        test_duration_hours: float = 24.0,
        report_dir: Optional[str] = None,
        extra_scenarios: Optional[List[Scenario]] = None,
    ) -> None:
        super().__init__("SandboxBuilderBot")
        repo_root = Path(__file__).resolve().parents[2]
        self.bots_root: Path = Path(bots_root) if bots_root else repo_root / "bots"
        self.iterations = iterations
        self.test_duration_hours = test_duration_hours
        self.report_dir: Path = Path(report_dir) if report_dir else repo_root / "logs"
        self.extra_scenarios: List[Scenario] = extra_scenarios or []
        self._all_scenarios: List[Scenario] = _DEFAULT_SCENARIOS + self.extra_scenarios

    # ------------------------------------------------------------------
    # BotBase task dispatch
    # ------------------------------------------------------------------

    def _run_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a sandbox build task.

        The ``task`` dict may carry:
        - ``action`` : ``"run_all"`` (default) | ``"discover"``
        - ``bot_name_filter`` : only test bots whose name contains this string
        """
        action = task.get("action", "run_all")
        name_filter: Optional[str] = task.get("bot_name_filter")

        if action == "discover":
            discovered = self._discover_bot_classes()
            return {
                "status": "ok",
                "discovered": [cls.__name__ for cls in discovered],
            }

        # Default: discover + run + report
        report = self.build_and_test(name_filter=name_filter)
        return {"status": "ok", "report_summary": report}

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def build_and_test(
        self,
        name_filter: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Full pipeline: discover → sandbox → rate → report.

        Parameters
        ----------
        name_filter : str | None
            When provided, only bots whose class name contains this string
            (case-insensitive) are tested.

        Returns
        -------
        dict
            The report summary dict produced by
            :class:`~sandbox.report_generator.SandboxReportGenerator`.
        """
        logger.info("SandboxBuilderBot: starting build-and-test pipeline")
        bot_classes = self._discover_bot_classes()

        if name_filter:
            bot_classes = [
                cls for cls in bot_classes
                if name_filter.lower() in cls.__name__.lower()
            ]

        if not bot_classes:
            logger.warning("No bot classes discovered — nothing to test.")
            return {"bots_evaluated": 0}

        report_gen = SandboxReportGenerator(
            test_duration_hours=self.test_duration_hours,
        )

        for bot_class in bot_classes:
            rating = self._test_bot_class(bot_class)
            if rating is not None:
                report_gen.add_rating(rating)

        # Write reports
        self.report_dir.mkdir(parents=True, exist_ok=True)
        ts = int(time.time())
        text_path = self.report_dir / f"sandbox_report_{ts}.txt"
        json_path = self.report_dir / f"sandbox_report_{ts}.json"
        report_gen.save_text(str(text_path))
        report_gen.save_json(str(json_path))

        text_report = report_gen.render_text()
        logger.info("\n%s", text_report)
        print(text_report)

        summary = report_gen.summary()
        logger.info("SandboxBuilderBot: pipeline complete. Summary: %s", summary)
        return summary

    # ------------------------------------------------------------------
    # Discovery
    # ------------------------------------------------------------------

    def _discover_bot_classes(self) -> List[Type[BotBase]]:
        """
        Walk ``bots_root`` and return all concrete :class:`BotBase` subclasses.

        Only files named ``*bot*.py`` or ``*_bot.py`` are imported to keep
        discovery fast and safe.
        """
        discovered: List[Type[BotBase]] = []
        seen_classes: set = set()

        if not self.bots_root.is_dir():
            logger.warning("bots_root does not exist: %s", self.bots_root)
            return discovered

        repo_root = self.bots_root.parent
        if str(repo_root) not in sys.path:
            sys.path.insert(0, str(repo_root))

        for py_file in sorted(self.bots_root.rglob("*.py")):
            if py_file.name.startswith("_"):
                continue
            # Only consider files that look like bot implementations
            name_lower = py_file.stem.lower()
            if "bot" not in name_lower and "agent" not in name_lower:
                continue

            module_path = py_file.relative_to(repo_root)
            module_name = ".".join(module_path.with_suffix("").parts)

            try:
                mod = importlib.import_module(module_name)
            except Exception as exc:
                logger.debug("Skipping %s: %s", module_name, exc)
                continue

            for _name, obj in inspect.getmembers(mod, inspect.isclass):
                if (
                    obj is BotBase
                    or id(obj) in seen_classes
                    or not issubclass(obj, BotBase)
                ):
                    continue
                # Skip abstract classes that can't be instantiated directly
                if inspect.isabstract(obj):
                    continue
                seen_classes.add(id(obj))
                discovered.append(obj)

        logger.info("SandboxBuilderBot: discovered %d bot class(es)", len(discovered))
        return discovered

    # ------------------------------------------------------------------
    # Per-bot test pipeline
    # ------------------------------------------------------------------

    @staticmethod
    def _instantiate_bot(bot_class: Type[BotBase], bot_name: str) -> Optional[BotBase]:
        """
        Instantiate *bot_class* using :func:`inspect.signature` to determine
        whether the constructor accepts a positional ``name`` argument.

        Returns the bot instance, or ``None`` if instantiation fails.
        """
        try:
            sig = inspect.signature(bot_class.__init__)
            params = list(sig.parameters.keys())
            # params[0] is always 'self'; check for a second positional param
            has_name_param = len(params) > 1 and params[1] not in ("*args", "**kwargs")
            if has_name_param:
                return bot_class(bot_name)
            return bot_class()
        except Exception as exc:
            logger.warning("Cannot instantiate %s: %s", bot_name, exc)
            return None

    def _test_bot_class(self, bot_class: Type[BotBase]):
        """Instantiate, test, and rate one bot class.  Returns None on error."""
        bot_name = bot_class.__name__
        logger.info("Testing bot: %s", bot_name)

        bot = self._instantiate_bot(bot_class, bot_name)
        if bot is None:
            return None

        try:
            bot.start()
        except Exception as exc:
            logger.warning("Cannot start %s: %s", bot_name, exc)
            return None

        # ---- SandboxTester (scenario-level metrics) ----
        tester = SandboxTester(iterations=self.iterations)
        for scenario in self._all_scenarios:
            tester.add_scenario(scenario)

        try:
            scenario_results = tester.run(bot)
        except Exception as exc:
            logger.warning("SandboxTester failed for %s: %s", bot_name, exc)
            scenario_results = {}

        # ---- PerformanceRatingSystem (star rating) ----
        prs = PerformanceRatingSystem(bot_name)
        for scenario_name, metrics in scenario_results.items():
            complexity = _SCENARIO_COMPLEXITY.get(scenario_name, "medium")
            for _ in range(metrics.passed):
                prs.record(TaskResult(task_type=scenario_name, success=True, complexity=complexity))
            for _ in range(metrics.failed):
                prs.record(TaskResult(task_type=scenario_name, success=False, complexity=complexity))

        rating = prs.compute_rating()

        try:
            bot.stop()
        except Exception:
            pass

        logger.info(
            "%s → %s (%.1f★, score=%.2f)",
            bot_name, rating.label, rating.star_rating, rating.weighted_score,
        )
        return rating
