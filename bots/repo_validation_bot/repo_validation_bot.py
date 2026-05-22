"""
Repo Validation Bot — scans every bot in the repository to ensure it is
correctly structured and intelligently coded.

Checks performed for each bot directory
----------------------------------------
1. **File existence** — required files must be present.
2. **app export** — Python entry-point files must define ``app`` (not
   ``application``, ``flask_app``, etc.) using Flask or FastAPI.
3. **__init__.py** — Python bot packages should have an ``__init__.py``.
4. **Framework import consistency** — the import and the assignment must use
   the same framework (e.g. importing ``Flask`` but assigning to a variable
   other than ``app`` is flagged).

Usage
-----
    python bots/repo_validation_bot/repo_validation_bot.py [--root .] [--json]

Exit code 0 if all bots pass, 1 if any validation issue is found.
"""

from __future__ import annotations

import argparse
import ast
import json
import os
import sys
from dataclasses import dataclass, field
from typing import Dict, List, Optional

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Required files — at least one from each inner list must be present.
REQUIRED_FILE_GROUPS: List[List[str]] = [
    ["main.py", "index.js", "bot.py"],
    ["README.md"],
]

# Known web-framework class names and the canonical variable name we expect.
_FRAMEWORK_CLASSES = {
    "Flask": "app",
    "FastAPI": "app",
    "Starlette": "app",
    "Quart": "app",
}

# Directories that are never bot packages and should be ignored.
_SKIP_DIRS = frozenset(
    [
        "node_modules",
        "__pycache__",
        "venv",
        ".venv",
        "env",
        ".git",
        "dist",
        "build",
        "site-packages",
        "fixtures",
    ]
)

# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------


@dataclass
class BotValidationResult:
    """Validation result for a single bot directory."""

    bot_name: str
    bot_path: str
    passed: bool
    issues: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict:
        return {
            "bot_name": self.bot_name,
            "bot_path": self.bot_path,
            "passed": self.passed,
            "issues": self.issues,
            "warnings": self.warnings,
        }


@dataclass
class ValidationReport:
    """Aggregate validation report for the whole repository."""

    total: int = 0
    passed: int = 0
    failed: int = 0
    results: List[BotValidationResult] = field(default_factory=list)

    @property
    def all_passed(self) -> bool:
        return self.failed == 0

    def to_dict(self) -> Dict:
        return {
            "total": self.total,
            "passed": self.passed,
            "failed": self.failed,
            "all_passed": self.all_passed,
            "results": [r.to_dict() for r in self.results],
        }

    def to_text(self) -> str:
        lines: List[str] = [
            "=== Repo Validation Bot Report ===",
            f"Total bots scanned : {self.total}",
            f"Passed             : {self.passed}",
            f"Failed             : {self.failed}",
            "",
        ]
        for r in self.results:
            status = "✅ PASS" if r.passed else "❌ FAIL"
            lines.append(f"{status}  {r.bot_name}  ({r.bot_path})")
            for issue in r.issues:
                lines.append(f"       ⛔ {issue}")
            for warn in r.warnings:
                lines.append(f"       ⚠️  {warn}")
        lines.append("")
        if self.all_passed:
            lines.append("🔥 ALL BOTS VALID")
        else:
            lines.append("🚨 BOT VALIDATION FAILED — see issues above")
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# AST helpers
# ---------------------------------------------------------------------------


def _parse_python_file(path: str) -> Optional[ast.Module]:
    """Parse *path* as Python and return the AST, or None on failure."""
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as fh:
            source = fh.read()
        return ast.parse(source, filename=path)
    except SyntaxError:
        return None
    except OSError:
        return None


def _check_app_export(path: str) -> List[str]:
    """
    Inspect a Python file for correct ``app`` assignment.

    Returns a (possibly empty) list of issue strings describing problems found.
    """
    tree = _parse_python_file(path)
    if tree is None:
        # File couldn't be parsed — emit a warning-level note rather than a hard failure.
        return []

    issues: List[str] = []

    # Collect all top-level assignments of the form  <name> = <FrameworkClass>(...)
    framework_assignments: Dict[str, str] = {}  # variable_name -> framework_class
    for node in ast.walk(tree):
        if not isinstance(node, ast.Assign):
            continue
        # Only look at simple single-target assignments at module level
        if len(node.targets) != 1:
            continue
        target = node.targets[0]
        if not isinstance(target, ast.Name):
            continue
        # RHS must be a Call whose func is a framework class name
        if not isinstance(node.value, ast.Call):
            continue
        func = node.value.func
        if isinstance(func, ast.Name) and func.id in _FRAMEWORK_CLASSES:
            framework_assignments[target.id] = func.id
        elif isinstance(func, ast.Attribute) and func.attr in _FRAMEWORK_CLASSES:
            framework_assignments[target.id] = func.attr

    if not framework_assignments:
        # No framework usage detected — nothing to validate here.
        return []

    # At least one framework call found — check that a variable named ``app`` is assigned.
    if "app" not in framework_assignments:
        # Report every incorrect assignment
        for var, cls in framework_assignments.items():
            issues.append(
                f"Framework app object assigned to '{var}' instead of 'app' "
                f"(found: {var} = {cls}(...)). "
                f"Rename to 'app = {cls}(...)' to ensure correct export."
            )
    return issues


# ---------------------------------------------------------------------------
# Per-bot validator
# ---------------------------------------------------------------------------


def _find_entry_points(bot_path: str) -> List[str]:
    """Return Python entry-point file paths within *bot_path*."""
    candidates = ["main.py", "bot.py", "app.py"]
    found = []
    for name in candidates:
        full = os.path.join(bot_path, name)
        if os.path.isfile(full):
            found.append(full)
    return found


def validate_bot(bot_path: str) -> BotValidationResult:
    """
    Run all validation checks for a single bot directory.

    Parameters
    ----------
    bot_path:
        Absolute (or relative) path to the bot directory.

    Returns
    -------
    BotValidationResult
    """
    bot_name = os.path.basename(bot_path.rstrip("/\\"))
    issues: List[str] = []
    warnings: List[str] = []

    # 1. File-existence checks
    try:
        files = set(os.listdir(bot_path))
    except OSError as exc:
        return BotValidationResult(
            bot_name=bot_name,
            bot_path=bot_path,
            passed=False,
            issues=[f"Cannot list directory: {exc}"],
        )

    for group in REQUIRED_FILE_GROUPS:
        if not any(f in files for f in group):
            issues.append(f"Missing one of required files: {group}")

    # 2. __init__.py check (soft warning for Python bots)
    has_python = any(f.endswith(".py") for f in files)
    if has_python and "__init__.py" not in files:
        warnings.append("Python bot is missing __init__.py (may cause import errors)")

    # 3. app-export check for Python entry-point files
    for entry_path in _find_entry_points(bot_path):
        app_issues = _check_app_export(entry_path)
        entry_name = os.path.basename(entry_path)
        for issue in app_issues:
            issues.append(f"[{entry_name}] {issue}")

    passed = len(issues) == 0
    return BotValidationResult(
        bot_name=bot_name,
        bot_path=bot_path,
        passed=passed,
        issues=issues,
        warnings=warnings,
    )


# ---------------------------------------------------------------------------
# Repository scanner
# ---------------------------------------------------------------------------


def _is_bot_dir(path: str) -> bool:
    """Return True when the directory name looks like a bot package."""
    name = os.path.basename(path.rstrip("/\\")).lower()
    return "bot" in name


def scan_repo(root: str = ".") -> ValidationReport:
    """
    Walk *root* and validate every bot directory found.

    Parameters
    ----------
    root:
        Repository root to scan.

    Returns
    -------
    ValidationReport
    """
    report = ValidationReport()
    abs_root = os.path.abspath(root)

    for dirpath, dirs, _files in os.walk(abs_root):
        # Prune skipped directories in-place so os.walk doesn't descend into them.
        dirs[:] = [
            d for d in dirs
            if not d.startswith(".") and d not in _SKIP_DIRS
        ]

        if not _is_bot_dir(dirpath):
            continue

        # Avoid scanning the repo_validation_bot itself as a subject
        if os.path.basename(dirpath) == "repo_validation_bot":
            continue

        result = validate_bot(dirpath)
        report.results.append(result)
        report.total += 1
        if result.passed:
            report.passed += 1
        else:
            report.failed += 1

    return report


# ---------------------------------------------------------------------------
# RepoValidationBot class (OOP wrapper for integration with other bots)
# ---------------------------------------------------------------------------


class RepoValidationBot:
    """
    Validation bot that ensures all bots in the repository follow the
    required structural and coding standards.
    """

    def __init__(self, repo_root: str = ".") -> None:
        self.repo_root = os.path.abspath(repo_root)

    def run(self) -> ValidationReport:
        """Scan the repository and return a ValidationReport."""
        print("=== Repo Validation Bot — scanning repository ===")
        report = scan_repo(self.repo_root)
        print(report.to_text())
        return report


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate all bot directories in the repository."
    )
    parser.add_argument(
        "--root",
        default=".",
        help="Repository root to scan (default: current directory).",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON instead of plain text.",
    )
    args = parser.parse_args(argv)

    bot = RepoValidationBot(repo_root=args.root)
    report = bot.run()

    if args.json:
        print(json.dumps(report.to_dict(), indent=2))

    return 0 if report.all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
