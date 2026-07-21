"""
Revenue Validation Bot — checks whether bots are ready to monetize.

For each bot directory, verifies the presence of:
  - payments.js  (payment integration)
  - logger.js    (interaction logging)
  - index.js     (offer/entry point)

Produces a Markdown report and can block CI/CD pipelines if checks fail.
"""

from __future__ import annotations

import os
import sys
from dataclasses import dataclass, field
from typing import Dict, List, Optional

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from framework import GlobalAISourcesFlow  # noqa: F401


# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------

REQUIRED_FILES = {
    "payments.js": "Payment integration",
    "logger.js": "Interaction logger",
    "index.js": "Bot offer/entry point",
}


@dataclass
class BotRevenueStatus:
    bot_name: str
    checks: Dict[str, bool] = field(default_factory=dict)

    @property
    def is_ready(self) -> bool:
        return all(self.checks.values())

    @property
    def missing_files(self) -> List[str]:
        return [f for f, ok in self.checks.items() if not ok]

    def to_dict(self) -> dict:
        return {
            "bot_name": self.bot_name,
            "checks": dict(self.checks),
            "is_ready": self.is_ready,
            "missing_files": self.missing_files,
        }


@dataclass
class RevenueValidationReport:
    total_bots: int
    ready_bots: int
    blocked_bots: int
    results: List[BotRevenueStatus] = field(default_factory=list)
    passed: bool = True
    report_md: str = ""

    def to_dict(self) -> dict:
        return {
            "total_bots": self.total_bots,
            "ready_bots": self.ready_bots,
            "blocked_bots": self.blocked_bots,
            "passed": self.passed,
            "results": [r.to_dict() for r in self.results],
        }


# ---------------------------------------------------------------------------
# RevenueValidationBot
# ---------------------------------------------------------------------------


class RevenueValidationBot:
    """Scans bot directories and validates revenue readiness."""

    def __init__(self, bots_dir: str = "bots", strict: bool = False):
        self.bots_dir = os.path.abspath(bots_dir)
        # When strict=True the report is marked failed if ANY bot is missing files.
        self.strict = strict

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def validate(self, bot_names: Optional[List[str]] = None) -> RevenueValidationReport:
        """Run revenue validation for all (or specified) bots.

        Parameters
        ----------
        bot_names : list of str, optional
            If provided, only these bot subdirectory names are validated.
        """
        results = self._scan_bots(bot_names)
        ready = sum(1 for r in results if r.is_ready)
        blocked = len(results) - ready
        passed = blocked == 0 if self.strict else True
        report = RevenueValidationReport(
            total_bots=len(results),
            ready_bots=ready,
            blocked_bots=blocked,
            results=results,
            passed=passed,
        )
        report.report_md = self._build_report(report)
        return report

    def validate_single_bot(self, bot_path: str) -> BotRevenueStatus:
        """Validate a single bot directory (absolute or relative path)."""
        abs_path = (
            bot_path
            if os.path.isabs(bot_path)
            else os.path.join(self.bots_dir, bot_path)
        )
        bot_name = os.path.basename(abs_path)
        return self._check_bot(bot_name, abs_path)

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------

    def _scan_bots(self, bot_names: Optional[List[str]]) -> List[BotRevenueStatus]:
        results: List[BotRevenueStatus] = []
        if not os.path.isdir(self.bots_dir):
            return results
        entries = sorted(os.listdir(self.bots_dir))
        for entry in entries:
            if bot_names and entry not in bot_names:
                continue
            full_path = os.path.join(self.bots_dir, entry)
            if not os.path.isdir(full_path):
                continue
            results.append(self._check_bot(entry, full_path))
        return results

    def _check_bot(self, bot_name: str, bot_path: str) -> BotRevenueStatus:
        checks = {
            filename: os.path.isfile(os.path.join(bot_path, filename))
            for filename in REQUIRED_FILES
        }
        return BotRevenueStatus(bot_name=bot_name, checks=checks)

    def _build_report(self, report: RevenueValidationReport) -> str:
        lines: List[str] = [
            "## 💰 Revenue Validation Report",
            "",
            f"**Status:** {'✅ ALL CLEAR' if report.passed else '❌ BLOCKED'}",
            f"**Total Bots:** {report.total_bots}",
            f"**Revenue-Ready:** {report.ready_bots}",
            f"**Blocked (missing files):** {report.blocked_bots}",
            "",
            "| Bot | payments.js | logger.js | index.js | Revenue-Ready |",
            "|-----|-------------|-----------|----------|---------------|",
        ]
        for r in report.results:
            p = "✅" if r.checks.get("payments.js") else "❌"
            lg = "✅" if r.checks.get("logger.js") else "❌"
            o = "✅" if r.checks.get("index.js") else "❌"
            rdy = "✅" if r.is_ready else "❌"
            lines.append(f"| `{r.bot_name}` | {p} | {lg} | {o} | {rdy} |")

        if report.blocked_bots > 0:
            lines += [
                "",
                "### ⚠️ Bots Missing Revenue Files",
                "",
            ]
            for r in report.results:
                if not r.is_ready:
                    lines.append(
                        f"- **`{r.bot_name}`** — missing: "
                        + ", ".join(f"`{f}`" for f in r.missing_files)
                    )

        lines.append("")
        return "\n".join(lines)
