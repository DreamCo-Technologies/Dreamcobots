#!/usr/bin/env python3
"""
Dreamcobots — Bot Test Validator
=================================

Automated test verification system that validates all bots by running
pytest for each discovered test file, logging failures with detailed
descriptions, and providing a comprehensive Markdown report.

Usage
-----
    python tools/bot_test_validator.py [--tests-dir DIR] [--bot PATTERN]
                                       [--log-file FILE] [--fail-fast]
                                       [--max-retries N] [--report FILE]

Exit codes
----------
0 — All tests passed (or no test files found).
1 — One or more tests failed.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

DEFAULT_TESTS_DIR = "tests"
DEFAULT_LOG_FILE = "logs/bot_test_validator.log"
DEFAULT_MAX_RETRIES = 2

# Test files that are intentionally excluded from the automated suite
IGNORED_TESTS: tuple = (
    "test_backend.py",
    "test_web_dashboard.py",
)


# ---------------------------------------------------------------------------
# Data Models
# ---------------------------------------------------------------------------


class TestResult:
    """Result of running a single test file."""

    def __init__(
        self,
        test_file: str,
        passed: bool,
        exit_code: int,
        stdout: str,
        stderr: str,
        duration: float,
        retry_count: int = 0,
    ):
        self.test_file = test_file
        self.passed = passed
        self.exit_code = exit_code
        self.stdout = stdout
        self.stderr = stderr
        self.duration = duration
        self.retry_count = retry_count
        self.timestamp = datetime.now(timezone.utc).isoformat()

    def to_dict(self) -> dict:
        return {
            "test_file": self.test_file,
            "passed": self.passed,
            "exit_code": self.exit_code,
            "stdout": self.stdout[-2000:] if len(self.stdout) > 2000 else self.stdout,
            "stderr": self.stderr[-1000:] if len(self.stderr) > 1000 else self.stderr,
            "duration_seconds": round(self.duration, 3),
            "retry_count": self.retry_count,
            "timestamp": self.timestamp,
        }


class ValidationReport:
    """Aggregated report of all test results."""

    def __init__(self, results: List[TestResult]):
        self.results = results
        self.timestamp = datetime.now(timezone.utc).isoformat()

    @property
    def total(self) -> int:
        return len(self.results)

    @property
    def passed_count(self) -> int:
        return sum(1 for r in self.results if r.passed)

    @property
    def failed_count(self) -> int:
        return sum(1 for r in self.results if not r.passed)

    @property
    def all_passed(self) -> bool:
        return self.failed_count == 0

    def failed_results(self) -> List[TestResult]:
        return [r for r in self.results if not r.passed]

    def to_dict(self) -> dict:
        return {
            "timestamp": self.timestamp,
            "total": self.total,
            "passed": self.passed_count,
            "failed": self.failed_count,
            "all_passed": self.all_passed,
            "results": [r.to_dict() for r in self.results],
        }

    def to_markdown(self) -> str:
        """Generate a human-readable Markdown report."""
        status = "✅ ALL PASSED" if self.all_passed else f"❌ {self.failed_count} FAILED"
        lines = [
            "# 🤖 Dreamcobots Bot Test Validation Report",
            "",
            f"**Generated:** {self.timestamp}",
            f"**Status:** {status}",
            (
                f"**Total:** {self.total} "
                f"| **Passed:** {self.passed_count} "
                f"| **Failed:** {self.failed_count}"
            ),
            "",
            "## Test Results",
            "",
            "| Test File | Status | Duration | Retries |",
            "|-----------|--------|----------|---------|",
        ]
        for r in self.results:
            icon = "✅" if r.passed else "❌"
            lines.append(
                f"| `{os.path.basename(r.test_file)}` "
                f"| {icon} "
                f"| {r.duration:.2f}s "
                f"| {r.retry_count} |"
            )

        if not self.all_passed:
            lines += ["", "## ❌ Failure Details", ""]
            for r in self.failed_results():
                lines += [
                    f"### `{os.path.basename(r.test_file)}`",
                    "",
                    f"- **Exit Code:** {r.exit_code}",
                    f"- **Duration:** {r.duration:.2f}s",
                    f"- **Retries:** {r.retry_count}",
                    "",
                ]
                if r.stdout:
                    last_lines = r.stdout.strip().splitlines()[-50:]
                    lines += ["**Output (last 50 lines):**", "```"] + last_lines + ["```"]
                if r.stderr:
                    lines += ["", "**Stderr:**", "```"] + r.stderr.strip().splitlines()[-20:] + ["```"]
                lines += ["", "**Suggested fixes:**"] + _suggest_fixes(r.stdout + "\n" + r.stderr) + [""]

        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Fix Suggestions
# ---------------------------------------------------------------------------


def _suggest_fixes(output: str) -> List[str]:
    """Analyze test output and return a list of human-readable fix suggestions."""
    suggestions = []
    if "ModuleNotFoundError" in output or "ImportError" in output:
        suggestions.append("- Run `pip install -r requirements.txt` to install missing dependencies.")
    if "No module named" in output:
        suggestions.append("- Verify the import path and that the package is listed in requirements.txt.")
    if "AssertionError" in output:
        suggestions.append("- Review the assertion — the expected value may need updating.")
    if "AttributeError" in output:
        suggestions.append("- An attribute is missing or misnamed; check the bot class definition.")
    if "TypeError" in output:
        suggestions.append("- A function was called with wrong argument types — check function signatures.")
    if "FileNotFoundError" in output:
        suggestions.append("- A required file is missing — ensure all bot configuration files are present.")
    if "ConnectionError" in output or "requests.exceptions" in output:
        suggestions.append("- Network error — mock all external connections in tests.")
    if not suggestions:
        suggestions.append("- Review the full test output above for specific failure details.")
        suggestions.append("- Run `python -m pytest <test_file> -v --tb=long` for a detailed traceback.")
    return suggestions


# ---------------------------------------------------------------------------
# Test Runner
# ---------------------------------------------------------------------------


class BotTestValidator:
    """Discovers and runs pytest for all bot test files, with retry support."""

    def __init__(
        self,
        tests_dir: Optional[str] = None,
        log_file: Optional[str] = None,
        max_retries: int = DEFAULT_MAX_RETRIES,
        fail_fast: bool = False,
        bot_pattern: Optional[str] = None,
    ):
        repo_root = Path(__file__).resolve().parent.parent
        self.tests_dir = (
            Path(tests_dir).resolve() if tests_dir else repo_root / DEFAULT_TESTS_DIR
        )
        self.log_file = (
            Path(log_file).resolve() if log_file else repo_root / DEFAULT_LOG_FILE
        )
        self.max_retries = max_retries
        self.fail_fast = fail_fast
        self.bot_pattern = bot_pattern
        self._results: List[TestResult] = []

    def discover_tests(self) -> List[Path]:
        """Return all test files in the tests directory, excluding ignored ones."""
        if not self.tests_dir.is_dir():
            print(
                f"[BotTestValidator] Tests directory not found: {self.tests_dir}",
                file=sys.stderr,
            )
            return []

        test_files = sorted(self.tests_dir.glob("test_*.py"))

        if self.bot_pattern:
            test_files = [f for f in test_files if self.bot_pattern in f.name]

        ignored = set(IGNORED_TESTS)
        test_files = [f for f in test_files if f.name not in ignored]

        return test_files

    def run_test_file(self, test_file: Path) -> TestResult:
        """Run pytest on a single test file with retry on failure."""
        retries = 0
        last_result: TestResult = TestResult(
            test_file=str(test_file),
            passed=False,
            exit_code=-1,
            stdout="",
            stderr="Not yet run",
            duration=0.0,
        )

        while retries <= self.max_retries:
            if retries > 0:
                print(
                    f"  [retry {retries}/{self.max_retries}] Retrying: {test_file.name}",
                    flush=True,
                )
                time.sleep(2)

            start = time.monotonic()
            try:
                proc = subprocess.run(
                    [
                        sys.executable,
                        "-m",
                        "pytest",
                        str(test_file),
                        "-q",
                        "--tb=short",
                        "--no-header",
                    ],
                    capture_output=True,
                    text=True,
                    timeout=120,
                )
                duration = time.monotonic() - start
                last_result = TestResult(
                    test_file=str(test_file),
                    passed=proc.returncode == 0,
                    exit_code=proc.returncode,
                    stdout=proc.stdout,
                    stderr=proc.stderr,
                    duration=duration,
                    retry_count=retries,
                )
            except subprocess.TimeoutExpired:
                duration = time.monotonic() - start
                last_result = TestResult(
                    test_file=str(test_file),
                    passed=False,
                    exit_code=-1,
                    stdout="",
                    stderr=f"Test timed out after {duration:.0f}s",
                    duration=duration,
                    retry_count=retries,
                )

            if last_result.passed:
                break
            retries += 1

        return last_result

    def run_all(self) -> ValidationReport:
        """Discover and run all bot tests, returning a ValidationReport."""
        test_files = self.discover_tests()
        if not test_files:
            print("[BotTestValidator] No test files found.")
            return ValidationReport([])

        print(f"[BotTestValidator] Found {len(test_files)} test file(s). Running...")
        self._results = []

        for test_file in test_files:
            print(f"  ▶ {test_file.name}", end=" ", flush=True)
            result = self.run_test_file(test_file)
            self._results.append(result)
            status = "✅ PASS" if result.passed else f"❌ FAIL (exit={result.exit_code})"
            print(f"→ {status} ({result.duration:.2f}s)", flush=True)

            if not result.passed and self.fail_fast:
                print("[BotTestValidator] --fail-fast: stopping on first failure.")
                break

        report = ValidationReport(self._results)
        self._write_log(report)
        return report

    def _write_log(self, report: ValidationReport) -> None:
        """Append a JSON-formatted report entry to the log file."""
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        with self.log_file.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(report.to_dict()) + "\n")
        print(f"[BotTestValidator] Log written to: {self.log_file}")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Dreamcobots — automated bot test validation framework.",
    )
    parser.add_argument(
        "--tests-dir",
        default=None,
        help=f"Directory containing test files (default: <repo-root>/{DEFAULT_TESTS_DIR}).",
    )
    parser.add_argument(
        "--bot",
        default=None,
        metavar="PATTERN",
        help="Only run tests whose filename contains PATTERN (e.g. 'mining_bot').",
    )
    parser.add_argument(
        "--log-file",
        default=None,
        help=f"Path to the validator log file (default: <repo-root>/{DEFAULT_LOG_FILE}).",
    )
    parser.add_argument(
        "--max-retries",
        type=int,
        default=DEFAULT_MAX_RETRIES,
        help=f"Number of times to retry a failing test (default: {DEFAULT_MAX_RETRIES}).",
    )
    parser.add_argument(
        "--fail-fast",
        action="store_true",
        default=False,
        help="Stop after the first test failure.",
    )
    parser.add_argument(
        "--report",
        default=None,
        metavar="FILE",
        help="Write a Markdown report to FILE.",
    )
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_arg_parser()
    args = parser.parse_args(argv)

    validator = BotTestValidator(
        tests_dir=args.tests_dir,
        log_file=args.log_file,
        max_retries=args.max_retries,
        fail_fast=args.fail_fast,
        bot_pattern=args.bot,
    )

    report = validator.run_all()
    md = report.to_markdown()
    print("\n" + "=" * 60)
    print(md)
    print("=" * 60)

    if args.report:
        report_path = Path(args.report)
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(md, encoding="utf-8")
        print(f"[BotTestValidator] Markdown report saved to: {report_path}")

    return 0 if report.all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
