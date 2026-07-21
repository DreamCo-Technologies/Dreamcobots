#!/usr/bin/env python3
"""
Dreamcobots — Guardian Debugger
================================

Dynamic debugger that identifies failure points by analyzing logs,
exception traces, and system inconsistencies. Suggests fixes or directly
adjusts faulty configurations (e.g., workflows.json, API mismatches).

Usage
-----
    python guardian_debug.py [--log-file FILE] [--workflows WORKFLOWS_JSON]
                              [--repo-root DIR] [--report FILE]

Exit codes
----------
0 — No issues requiring manual intervention.
1 — One or more issues require manual review.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional


# ---------------------------------------------------------------------------
# Failure patterns and diagnosis
# ---------------------------------------------------------------------------

# Each entry: (pattern, failure_type, description, fix_suggestion, requires_manual)
_FAILURE_PATTERNS = [
    (
        re.compile(r"ModuleNotFoundError|ImportError|No module named", re.IGNORECASE),
        "import_error",
        "Missing Python module or incorrect import path.",
        "Run: pip install -r requirements.txt\n"
        "Verify sys.path includes the correct bot directory.",
        False,
    ),
    (
        re.compile(r"AssertionError", re.IGNORECASE),
        "assertion_error",
        "A test assertion failed — expected value does not match actual.",
        "Review the assertion and update expected values or fix the bot logic.",
        False,
    ),
    (
        re.compile(r"AttributeError", re.IGNORECASE),
        "attribute_error",
        "Missing attribute or method on a class/object.",
        "Check the class definition and ensure all required attributes are initialized.",
        False,
    ),
    (
        re.compile(r"TypeError", re.IGNORECASE),
        "type_error",
        "A function was called with incompatible argument types.",
        "Check function signatures and argument types in the failing test or bot code.",
        False,
    ),
    (
        re.compile(r"FileNotFoundError|No such file or directory", re.IGNORECASE),
        "file_not_found",
        "A required file or configuration is missing.",
        "Ensure all required files (workflows.json, config files) are present.",
        False,
    ),
    (
        re.compile(r"KeyError", re.IGNORECASE),
        "key_error",
        "A dictionary key is missing — possibly a workflows.json schema mismatch.",
        "Check workflows.json and configuration files for missing keys.",
        False,
    ),
    (
        re.compile(
            r"ConnectionError|requests\.exceptions|URLError|timeout",
            re.IGNORECASE,
        ),
        "network_error",
        "Network connection failed — likely an unmocked external API call.",
        "Mock all external API calls in tests using unittest.mock or pytest-mock.",
        False,
    ),
    (
        re.compile(r"SyntaxError", re.IGNORECASE),
        "syntax_error",
        "Python syntax error in bot or test code.",
        "Fix the syntax error reported in the traceback.",
        True,
    ),
    (
        re.compile(r"IndentationError", re.IGNORECASE),
        "indentation_error",
        "Python indentation error.",
        "Fix incorrect indentation in the reported file.",
        True,
    ),
    (
        re.compile(r"workflows\.json|workflow.*schema|workflow.*mismatch", re.IGNORECASE),
        "workflow_config_error",
        "workflows.json schema mismatch or missing required fields.",
        "Validate workflows.json — each entry needs: file, priority, global_settings.",
        False,
    ),
]

# Expected top-level keys in each workflows.json entry
_WORKFLOW_REQUIRED_KEYS = {"id", "name", "trigger", "action"}


def _utcnow() -> str:
    return datetime.now(tz=timezone.utc).isoformat()


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------


class FailureDiagnosis:
    """A detected failure with its analysis and recommended fix."""

    def __init__(
        self,
        failure_type: str,
        description: str,
        fix_suggestion: str,
        matched_pattern: str,
        requires_manual: bool = False,
    ):
        self.failure_type = failure_type
        self.description = description
        self.fix_suggestion = fix_suggestion
        self.matched_pattern = matched_pattern
        self.requires_manual = requires_manual
        self.timestamp = _utcnow()

    def to_dict(self) -> dict:
        return {
            "failure_type": self.failure_type,
            "description": self.description,
            "fix_suggestion": self.fix_suggestion,
            "matched_pattern": self.matched_pattern,
            "requires_manual": self.requires_manual,
            "timestamp": self.timestamp,
        }


# ---------------------------------------------------------------------------
# Debugger
# ---------------------------------------------------------------------------


class GuardianDebugger:
    """
    Analyses test logs and exception traces to identify failure points
    and suggest or apply automated fixes.
    """

    def __init__(self, repo_root: Optional[str] = None):
        self.repo_root = (
            Path(repo_root).resolve()
            if repo_root
            else Path(__file__).resolve().parent
        )
        self._diagnoses: List[FailureDiagnosis] = []

    # ------------------------------------------------------------------
    # Analysis
    # ------------------------------------------------------------------

    def analyze(self, log_content: str) -> List[FailureDiagnosis]:
        """Scan *log_content* for known failure patterns and return diagnoses."""
        self._diagnoses = []
        matched_types: set = set()

        for pattern, failure_type, description, fix, manual in _FAILURE_PATTERNS:
            if failure_type in matched_types:
                continue
            if pattern.search(log_content):
                self._diagnoses.append(
                    FailureDiagnosis(
                        failure_type=failure_type,
                        description=description,
                        fix_suggestion=fix,
                        matched_pattern=pattern.pattern,
                        requires_manual=manual,
                    )
                )
                matched_types.add(failure_type)

        if not self._diagnoses:
            self._diagnoses.append(
                FailureDiagnosis(
                    failure_type="unknown",
                    description="No known failure pattern matched the log content.",
                    fix_suggestion=(
                        "Manually review the full log output.\n"
                        "Run: python -m pytest tests/ -v --tb=long"
                    ),
                    matched_pattern="",
                    requires_manual=True,
                )
            )

        return self._diagnoses

    def analyze_file(self, log_file: Path) -> List[FailureDiagnosis]:
        """Read *log_file* and analyse its content."""
        if not log_file.exists():
            return [
                FailureDiagnosis(
                    failure_type="log_not_found",
                    description=f"Log file not found: {log_file}",
                    fix_suggestion="Ensure the test validator has been run first.",
                    matched_pattern="",
                    requires_manual=True,
                )
            ]
        content = log_file.read_text(encoding="utf-8", errors="replace")
        return self.analyze(content)

    # ------------------------------------------------------------------
    # Configuration validation
    # ------------------------------------------------------------------

    def check_workflows_json(
        self, workflows_path: Optional[Path] = None
    ) -> dict:
        """
        Validate workflows.json against the expected schema.

        Expected schema per workflow entry::

            { "id": str, "name": str, "trigger": str, "action": str }

        Returns a dict with keys: path, valid, issues, fix_applied.
        """
        if workflows_path is None:
            workflows_path = self.repo_root / "workflows.json"

        result: dict = {
            "path": str(workflows_path),
            "valid": False,
            "issues": [],
            "fix_applied": False,
        }

        if not workflows_path.exists():
            result["issues"].append(
                f"workflows.json not found at {workflows_path}"
            )
            return result

        try:
            data = json.loads(workflows_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            result["issues"].append(f"Invalid JSON: {exc}")
            return result

        workflows = (
            data if isinstance(data, list) else data.get("workflows", [])
        )
        for i, entry in enumerate(workflows):
            if not isinstance(entry, dict):
                result["issues"].append(
                    f"Workflow entry {i} is not a dict: {entry!r}"
                )
                continue
            missing = _WORKFLOW_REQUIRED_KEYS - set(entry.keys())
            if missing:
                result["issues"].append(
                    f"Workflow entry {i} ({entry.get('file', '?')!r}) "
                    f"missing keys: {sorted(missing)}"
                )

        result["valid"] = len(result["issues"]) == 0
        return result

    # ------------------------------------------------------------------
    # Reporting
    # ------------------------------------------------------------------

    def build_report(self, diagnoses: List[FailureDiagnosis]) -> str:
        """Generate a Markdown debug report."""
        lines = [
            "# 🔍 Dreamcobots Guardian Debug Report",
            "",
            f"**Generated:** {_utcnow()}",
            f"**Issues found:** {len(diagnoses)}",
            "",
        ]

        for i, d in enumerate(diagnoses, 1):
            icon = "⚠️" if d.requires_manual else "🔧"
            lines += [
                f"## {icon} Issue {i}: `{d.failure_type}`",
                "",
                f"**Description:** {d.description}",
                "",
                "**Suggested Fix:**",
                "```",
                d.fix_suggestion,
                "```",
                "",
            ]
            if d.requires_manual:
                lines.append("**⚠️ Manual intervention required.**")
                lines.append("")

        if diagnoses and all(not d.requires_manual for d in diagnoses):
            lines += [
                "---",
                "✅ All detected issues have automated fix suggestions.",
            ]

        return "\n".join(lines)

    def print_report(self, diagnoses: List[FailureDiagnosis]) -> None:
        """Print the debug report to stdout."""
        print(self.build_report(diagnoses))


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Dreamcobots Guardian Debugger — "
            "analyse logs and diagnose CI failures."
        ),
    )
    parser.add_argument(
        "--log-file",
        default=None,
        help="Path to a log file to analyse.",
    )
    parser.add_argument(
        "--workflows",
        default=None,
        help="Path to workflows.json to validate "
        "(default: <repo-root>/workflows.json).",
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
        help="Write the debug report to FILE.",
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
    debugger = GuardianDebugger(repo_root=str(repo_root))
    diagnoses: List[FailureDiagnosis] = []

    # Analyse provided log file, or fall back to the validator log
    if args.log_file:
        log_path = Path(args.log_file).resolve()
        print(f"[guardian_debug] Analysing log file: {log_path}")
        diagnoses = debugger.analyze_file(log_path)
    else:
        default_log = repo_root / "logs" / "bot_test_validator.log"
        if default_log.exists():
            print(f"[guardian_debug] Analysing default log: {default_log}")
            diagnoses = debugger.analyze_file(default_log)
        else:
            print(
                "[guardian_debug] No log file specified or found. "
                "Checking workflows.json only."
            )

    # Validate workflows.json
    wf_path = (
        Path(args.workflows).resolve()
        if args.workflows
        else repo_root / "workflows.json"
    )
    print(f"[guardian_debug] Checking workflows.json: {wf_path}")
    wf_check = debugger.check_workflows_json(wf_path)
    if not wf_check["valid"]:
        for issue in wf_check["issues"]:
            print(f"  ⚠️  {issue}")
        if not diagnoses:
            diagnoses.append(
                FailureDiagnosis(
                    failure_type="workflow_config_error",
                    description="; ".join(wf_check["issues"]),
                    fix_suggestion=(
                        "Validate and repair workflows.json.\n"
                        "Each entry needs: file, priority, global_settings."
                    ),
                    matched_pattern="workflows.json schema check",
                    requires_manual=bool(wf_check["issues"]),
                )
            )
    else:
        print("  ✅ workflows.json is valid.")

    report_md = debugger.build_report(diagnoses)
    print(report_md)

    if args.report:
        report_path = Path(args.report)
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(report_md, encoding="utf-8")
        print(f"[guardian_debug] Report saved to: {report_path}")

    requires_manual = any(d.requires_manual for d in diagnoses)
    return 1 if requires_manual else 0


if __name__ == "__main__":
    sys.exit(main())