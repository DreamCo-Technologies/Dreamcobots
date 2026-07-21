#!/usr/bin/env python3
"""
Dreamcobots — Guardian Monitor
================================

Self-healing runtime monitor that orchestrates the bot test validator and
guardian debugger to provide an automated CI/CD repair pipeline.

Pipeline
--------
1. Run ``tools/bot_test_validator.py`` — pytest for all discovered bots.
2. On failure, run ``guardian_debug.py`` — analyse logs and identify causes.
3. Apply automated healing actions (pip install, compliance check).
4. Re-run the failing tests (up to max_retries times).
5. Escalate with actionable recommendations when automation cannot fix.

Usage
-----
    python guardian_monitor.py [--tests-dir DIR] [--repo-root DIR]
                                [--report FILE] [--max-retries N]

Exit codes
----------
0 — All tests passed (before or after self-healing).
1 — Failures remain after all self-healing attempts.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

DEFAULT_MAX_RETRIES = 2
DEFAULT_REPORT_FILE = "logs/guardian_monitor_report.md"
VALIDATOR_TIMEOUT_SECONDS = 600  # 10 minutes for full test suite run


def _utcnow() -> str:
    return datetime.now(tz=timezone.utc).isoformat()


# ---------------------------------------------------------------------------
# Self-healing actions
# ---------------------------------------------------------------------------


def _attempt_pip_install(repo_root: Path) -> bool:
    """Try to fix missing dependencies via pip install -r requirements.txt."""
    req_file = repo_root / "requirements.txt"
    if not req_file.exists():
        return False
    print("[guardian_monitor] 🔧 Attempting: pip install -r requirements.txt")
    result = subprocess.run(
        [sys.executable, "-m", "pip", "install", "-r", str(req_file), "--quiet"],
        capture_output=True,
        text=True,
    )
    return result.returncode == 0


def _attempt_framework_compliance(repo_root: Path) -> bool:
    """Run the framework compliance checker and return True if it passes."""
    checker = repo_root / "tools" / "check_bot_framework.py"
    if not checker.exists():
        return True
    print("[guardian_monitor] 🔧 Running framework compliance check...")
    result = subprocess.run(
        [sys.executable, str(checker)],
        capture_output=True,
        text=True,
    )
    return result.returncode == 0


# ---------------------------------------------------------------------------
# Monitor
# ---------------------------------------------------------------------------


class GuardianMonitor:
    """
    Orchestrates the bot test validator, guardian debugger, and self-healing
    actions to provide an automated CI repair pipeline for Dreamcobots.
    """

    def __init__(
        self,
        repo_root: Optional[str] = None,
        tests_dir: Optional[str] = None,
        max_retries: int = DEFAULT_MAX_RETRIES,
    ):
        self.repo_root = (
            Path(repo_root).resolve()
            if repo_root
            else Path(__file__).resolve().parent
        )
        self.tests_dir = (
            Path(tests_dir).resolve() if tests_dir else self.repo_root / "tests"
        )
        self.max_retries = max_retries
        self._report_lines: List[str] = []

    def _log(self, msg: str) -> None:
        print(msg)
        self._report_lines.append(msg)

    # ------------------------------------------------------------------
    # Public entry point
    # ------------------------------------------------------------------

    def run(self) -> int:
        """
        Execute the full monitoring + self-healing pipeline.

        Returns 0 if all tests pass, 1 otherwise.
        """
        self._report_lines = []
        self._log("=" * 60)
        self._log("  Dreamcobots Guardian Monitor")
        self._log(f"  Started: {_utcnow()}")
        self._log("=" * 60)

        # Step 1 — initial test run
        self._log("\n[Step 1] Running Bot Test Validator...")
        exit_code, output = self._run_validator()
        self._log(output)

        if exit_code == 0:
            self._log("\n✅ All bot tests passed. No healing needed.")
            self._log(f"\nCompleted: {_utcnow()}")
            return 0

        # Step 2 — debug the failures
        self._log("\n[Step 2] Running Guardian Debugger...")
        debug_output = self._run_debugger()
        self._log(debug_output)

        # Step 3 — apply self-healing
        self._log("\n[Step 3] Attempting self-healing...")
        healed = self._attempt_self_heal(debug_output)

        # Step 4 — re-run tests if healing was applied
        if healed:
            self._log("\n[Step 4] Re-running tests after healing...")
            exit_code, output = self._run_validator()
            self._log(output)
            if exit_code == 0:
                self._log("\n✅ Self-healing successful! All tests now pass.")
                self._log(f"\nCompleted: {_utcnow()}")
                return 0
            self._log("\n⚠️  Tests still failing after self-healing attempt.")
        else:
            self._log("  No automated healing actions could be applied.")

        # Step 5 — escalate
        self._log("\n[Step 5] Escalation — manual intervention required.")
        self._log(self._build_escalation_message())
        self._log(f"\nCompleted: {_utcnow()}")
        return 1

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _run_validator(self) -> tuple:
        """Run bot_test_validator.py and return (exit_code, combined_output)."""
        validator = self.repo_root / "tools" / "bot_test_validator.py"
        if not validator.exists():
            return (
                1,
                "[guardian_monitor] ⚠️ tools/bot_test_validator.py not found.",
            )
        result = subprocess.run(
            [
                sys.executable,
                str(validator),
                "--tests-dir",
                str(self.tests_dir),
                "--max-retries",
                "1",
            ],
            capture_output=True,
            text=True,
            timeout=VALIDATOR_TIMEOUT_SECONDS,
        )
        return result.returncode, result.stdout + result.stderr

    def _run_debugger(self) -> str:
        """Run guardian_debug.py and return its combined output."""
        debugger = self.repo_root / "guardian_debug.py"
        if not debugger.exists():
            return "[guardian_monitor] ⚠️ guardian_debug.py not found."
        result = subprocess.run(
            [sys.executable, str(debugger), "--repo-root", str(self.repo_root)],
            capture_output=True,
            text=True,
            timeout=60,
        )
        return result.stdout + result.stderr

    def _attempt_self_heal(self, debug_output: str) -> bool:
        """Apply automated fixes based on debug output. Returns True if any fix was applied."""
        applied = False

        if any(
            kw in debug_output
            for kw in ("import_error", "ModuleNotFoundError", "ImportError")
        ):
            if _attempt_pip_install(self.repo_root):
                self._log("  ✅ pip install succeeded.")
                applied = True
            else:
                self._log("  ❌ pip install failed.")

        if any(
            kw in debug_output
            for kw in ("framework_compliance", "GlobalAISourcesFlow")
        ):
            if _attempt_framework_compliance(self.repo_root):
                self._log("  ✅ Framework compliance check passed.")
            else:
                self._log(
                    "  ⚠️  Framework compliance violations remain — manual fix needed."
                )

        return applied

    @staticmethod
    def _build_escalation_message() -> str:
        return (
            "\n🚨 Automated healing was unable to resolve all failures.\n"
            "   Manual intervention required:\n"
            "   1. Review test output above for specific failure details.\n"
            "   2. Run: python -m pytest tests/ -v --tb=long\n"
            "   3. Check bot implementations for import/logic errors.\n"
            "   4. Run: python tools/check_bot_framework.py\n"
            "   5. Verify requirements.txt includes all needed packages.\n"
            "   6. Run: python tools/auto_recovery.py for full diagnostics.\n"
        )

    # ------------------------------------------------------------------
    # Report
    # ------------------------------------------------------------------

    def save_report(self, report_file: Path) -> None:
        """Write the monitoring log to *report_file*."""
        report_file.parent.mkdir(parents=True, exist_ok=True)
        report_file.write_text("\n".join(self._report_lines), encoding="utf-8")
        print(f"[guardian_monitor] Report saved to: {report_file}")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Dreamcobots Guardian Monitor — self-healing CI pipeline.",
    )
    parser.add_argument(
        "--tests-dir",
        default=None,
        help="Directory containing test files.",
    )
    parser.add_argument(
        "--repo-root",
        default=None,
        help="Repository root directory.",
    )
    parser.add_argument(
        "--report",
        default=None,
        metavar="FILE",
        help=(
            f"Save the monitoring report to FILE "
            f"(default: <repo-root>/{DEFAULT_REPORT_FILE})."
        ),
    )
    parser.add_argument(
        "--max-retries",
        type=int,
        default=DEFAULT_MAX_RETRIES,
        help=f"Number of self-healing retries (default: {DEFAULT_MAX_RETRIES}).",
    )
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_arg_parser()
    args = parser.parse_args(argv)

    repo_root = (
        Path(args.repo_root).resolve()
        if args.repo_root
        else Path(__file__).resolve().parent
    )
    monitor = GuardianMonitor(
        repo_root=str(repo_root),
        tests_dir=args.tests_dir,
        max_retries=args.max_retries,
    )

    exit_code = monitor.run()

    report_path = (
        Path(args.report).resolve()
        if args.report
        else repo_root / DEFAULT_REPORT_FILE
    )
    monitor.save_report(report_path)

    return exit_code


if __name__ == "__main__":
    sys.exit(main())