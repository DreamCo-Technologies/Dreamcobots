"""
PR Validation Bot — validates pull requests, auto-restores deleted critical files,
enforces revenue readiness, and generates Markdown reports.

Key behaviors:
  - Only restores files with git status 'D' (deleted).  Files with status 'M'
    (modified) or 'R' (renamed) are intentional changes and must NOT be touched.
  - Validates that every bot directory contains the revenue-readiness files.
  - Outputs a detailed Markdown report for the PR comment.
"""

from __future__ import annotations

import os
import subprocess
import sys
from dataclasses import dataclass, field
from typing import Dict, List, Optional

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from framework import GlobalAISourcesFlow  # noqa: F401


# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------

CRITICAL_FILES = [
    "index.js",
    "package.json",
    "README.md",
    "requirements.txt",
    "framework/__init__.py",
    "tools/check_bot_framework.py",
]

REVENUE_REQUIRED_FILES = [
    "payments.js",
    "logger.js",
    "index.js",
]


@dataclass
class FileStatus:
    path: str
    status: str  # 'D', 'M', 'R', 'A', 'U', …


@dataclass
class RevenueCheck:
    bot_path: str
    has_payment: bool
    has_logger: bool
    has_offer: bool

    @property
    def is_ready(self) -> bool:
        return self.has_payment and self.has_logger and self.has_offer

    def to_dict(self) -> dict:
        return {
            "bot_path": self.bot_path,
            "has_payment": self.has_payment,
            "has_logger": self.has_logger,
            "has_offer": self.has_offer,
            "is_ready": self.is_ready,
        }


@dataclass
class ValidationResult:
    passed: bool
    critical_files_ok: bool
    restored_files: List[str] = field(default_factory=list)
    skipped_files: List[str] = field(default_factory=list)
    revenue_checks: List[RevenueCheck] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    report_md: str = ""


# ---------------------------------------------------------------------------
# PRValidationBot
# ---------------------------------------------------------------------------

class PRValidationBot:
    """Validates PRs, auto-restores deleted critical files, and checks revenue readiness."""

    def __init__(self, repo_root: str = ".", base_branch: str = "main"):
        self.repo_root = os.path.abspath(repo_root)
        self.base_branch = base_branch

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def validate(self) -> ValidationResult:
        """Run full PR validation and return a ValidationResult."""
        changed = self._get_changed_files()
        deleted, skipped = self._classify_files(changed)
        restored = self._restore_deleted_critical_files(deleted)
        revenue_checks = self._validate_revenue_bots()
        errors = self._collect_errors(restored, revenue_checks)
        critical_ok = self._check_critical_files_exist()
        passed = critical_ok and not errors
        result = ValidationResult(
            passed=passed,
            critical_files_ok=critical_ok,
            restored_files=restored,
            skipped_files=skipped,
            revenue_checks=revenue_checks,
            errors=errors,
        )
        result.report_md = self._build_report(result)
        return result

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _run(self, cmd: List[str], check: bool = True) -> subprocess.CompletedProcess:
        return subprocess.run(
            cmd,
            cwd=self.repo_root,
            capture_output=True,
            text=True,
            check=check,
        )

    def _get_changed_files(self) -> List[FileStatus]:
        """Return list of FileStatus objects for files changed relative to base branch."""
        try:
            result = self._run(
                ["git", "diff", "--name-status", f"{self.base_branch}...HEAD"], check=False
            )
            statuses: List[FileStatus] = []
            for line in result.stdout.splitlines():
                line = line.strip()
                if not line:
                    continue
                parts = line.split("\t", 1)
                if len(parts) == 2:
                    status_code = parts[0][0]  # first char: D, M, R, A, …
                    path = parts[1]
                    statuses.append(FileStatus(path=path, status=status_code))
            return statuses
        except Exception:
            return []

    def _classify_files(
        self, changed: List[FileStatus]
    ) -> tuple[List[FileStatus], List[str]]:
        """Split changed files into truly-deleted vs intentionally-modified.

        Only files with status 'D' (deleted) are eligible for auto-restore.
        Files with status 'M' (modified) or 'R' (renamed) represent intentional
        changes and must NOT be overwritten.
        """
        deleted: List[FileStatus] = []
        skipped: List[str] = []
        for fs in changed:
            if fs.status == "D":
                deleted.append(fs)
            elif fs.status in ("M", "R"):
                # Intentional change — skip to avoid overwriting developer work
                skipped.append(fs.path)
        return deleted, skipped

    def _restore_deleted_critical_files(self, deleted: List[FileStatus]) -> List[str]:
        """Restore critical files that were deleted, from the base branch."""
        restored: List[str] = []
        critical_set = set(CRITICAL_FILES)
        for fs in deleted:
            if fs.path not in critical_set:
                continue
            try:
                self._run(["git", "checkout", self.base_branch, "--", fs.path])
                restored.append(fs.path)
            except subprocess.CalledProcessError:
                pass
        return restored

    def _check_critical_files_exist(self) -> bool:
        """Verify all critical files are present in the working tree."""
        for f in CRITICAL_FILES:
            full_path = os.path.join(self.repo_root, f)
            if not os.path.exists(full_path):
                return False
        return True

    def _validate_revenue_bots(self) -> List[RevenueCheck]:
        """Check every bot directory for revenue-readiness files."""
        checks: List[RevenueCheck] = []
        bots_dir = os.path.join(self.repo_root, "bots")
        if not os.path.isdir(bots_dir):
            return checks
        for entry in sorted(os.listdir(bots_dir)):
            bot_path = os.path.join(bots_dir, entry)
            if not os.path.isdir(bot_path):
                continue
            check = RevenueCheck(
                bot_path=entry,
                has_payment=os.path.isfile(os.path.join(bot_path, "payments.js")),
                has_logger=os.path.isfile(os.path.join(bot_path, "logger.js")),
                has_offer=os.path.isfile(os.path.join(bot_path, "index.js")),
            )
            checks.append(check)
        return checks

    def _collect_errors(
        self, restored: List[str], revenue_checks: List[RevenueCheck]
    ) -> List[str]:
        errors: List[str] = []
        for rc in revenue_checks:
            if not rc.is_ready:
                missing = []
                if not rc.has_payment:
                    missing.append("payments.js")
                if not rc.has_logger:
                    missing.append("logger.js")
                if not rc.has_offer:
                    missing.append("index.js")
                errors.append(
                    f"Bot '{rc.bot_path}' missing revenue files: {', '.join(missing)}"
                )
        return errors

    def _build_report(self, result: ValidationResult) -> str:
        """Generate a Markdown summary report for the PR comment."""
        lines: List[str] = [
            "## 🤖 PR Validation Report",
            "",
            f"**Overall Status:** {'✅ PASSED' if result.passed else '❌ FAILED'}",
            f"**Critical Files:** {'✅ All present' if result.critical_files_ok else '❌ Some missing'}",
            "",
        ]

        if result.restored_files:
            lines.append("### 🔧 Auto-Restored Deleted Files")
            for f in result.restored_files:
                lines.append(f"- `{f}` — restored from `{self.base_branch}`")
            lines.append("")

        if result.skipped_files:
            lines.append("### ⏭️ Skipped (Intentional Changes — Not Overwritten)")
            for f in result.skipped_files:
                lines.append(f"- `{f}`")
            lines.append("")

        # Revenue readiness table
        lines.append("### 💰 Revenue Readiness")
        lines.append("")
        lines.append("| Bot | payments.js | logger.js | index.js | Ready |")
        lines.append("|-----|-------------|-----------|----------|-------|")
        for rc in result.revenue_checks:
            p = "✅" if rc.has_payment else "❌"
            lg = "✅" if rc.has_logger else "❌"
            o = "✅" if rc.has_offer else "❌"
            r = "✅" if rc.is_ready else "❌"
            lines.append(f"| `{rc.bot_path}` | {p} | {lg} | {o} | {r} |")
        lines.append("")

        if result.errors:
            lines.append("### ⚠️ Errors")
            for e in result.errors:
                lines.append(f"- {e}")
            lines.append("")

        return "\n".join(lines)
