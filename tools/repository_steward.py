#!/usr/bin/env python3
"""Build the DreamCo repository stewardship report.

The steward keeps PRs and issues clean by converting noisy GitHub state into
owner-approved queues, then running local syntax gates before anything is
presented as ready.
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import py_compile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
REPORT_DIR = ROOT / "reports"
TRIAGE_REPORT = REPORT_DIR / "github_triage_report.json"
GOAL_CONSOLIDATION = ROOT / "config" / "github_goal_consolidation.json"
JSON_TARGETS = (
    ROOT / "config",
    ROOT / "dreamco-control-tower" / "config",
    ROOT / "reports",
)
CODE_EXCLUDE_PARTS = {
    ".git",
    ".venv",
    "__pycache__",
    "node_modules",
    "dist",
    "build",
    ".next",
    "coverage",
    "work",
}
JS_SUFFIXES = {".js", ".mjs", ".cjs"}
BUNDLED_NODE = Path.home() / ".cache" / "codex-runtimes" / "codex-primary-runtime" / "dependencies" / "node" / "bin" / "node"


@dataclass(frozen=True)
class CheckResult:
    name: str
    status: str
    scanned: int
    failures: list[dict[str, str]]


def iso_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def read_json(path: Path, fallback: Any) -> Any:
    if not path.exists():
        return fallback
    return json.loads(path.read_text(encoding="utf-8"))


def should_skip(path: Path) -> bool:
    return any(part in CODE_EXCLUDE_PARTS for part in path.relative_to(ROOT).parts)


def repo_files(suffixes: set[str]) -> list[Path]:
    files: list[Path] = []
    for path in ROOT.rglob("*"):
        if path.is_file() and path.suffix in suffixes and not should_skip(path):
            files.append(path)
    return sorted(files)


def json_files() -> list[Path]:
    files: list[Path] = []
    for base in JSON_TARGETS:
        if not base.exists():
            continue
        files.extend(path for path in base.rglob("*.json") if path.is_file() and not should_skip(path))
    return sorted(set(files))


def check_json() -> CheckResult:
    failures: list[dict[str, str]] = []
    files = json_files()
    for path in files:
        try:
            json.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:  # noqa: BLE001 - report all parse failures.
            failures.append({"file": str(path.relative_to(ROOT)), "error": str(exc)})
    return CheckResult("json_parse", "pass" if not failures else "fail", len(files), failures)


def check_python() -> CheckResult:
    failures: list[dict[str, str]] = []
    files = repo_files({".py"})
    for path in files:
        try:
            py_compile.compile(str(path), doraise=True)
        except py_compile.PyCompileError as exc:
            failures.append({"file": str(path.relative_to(ROOT)), "error": exc.msg})
    return CheckResult("python_syntax", "pass" if not failures else "fail", len(files), failures)


def check_javascript() -> CheckResult:
    node = shutil.which("node") or (str(BUNDLED_NODE) if BUNDLED_NODE.exists() else None)
    files = repo_files(JS_SUFFIXES)
    if not node:
        return CheckResult(
            "javascript_syntax",
            "skipped",
            len(files),
            [{"file": "node", "error": "node executable not found"}],
        )

    failures: list[dict[str, str]] = []
    for path in files:
        result = subprocess.run(
            [node, "--check", str(path)],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        if result.returncode != 0:
            failures.append(
                {
                    "file": str(path.relative_to(ROOT)),
                    "error": (result.stderr or result.stdout).strip()[:1000],
                }
            )
    return CheckResult("javascript_syntax", "pass" if not failures else "fail", len(files), failures)


def planned_items_from_goal_config() -> dict[str, list[dict[str, Any]]]:
    config = read_json(GOAL_CONSOLIDATION, {})
    pr_items = config.get("pull_request_cleanup", [])
    issue_items = config.get("issue_cleanup", [])
    return {
        "keep_prs": [item for item in pr_items if "keep" in item.get("decision", "")],
        "close_pr_candidates": [
            item
            for item in pr_items
            if any(token in item.get("decision", "") for token in ("close", "archive"))
        ],
        "keep_issues": [item for item in issue_items if "keep" in item.get("decision", "")],
        "close_issue_candidates": [
            item
            for item in issue_items
            if any(token in item.get("decision", "") for token in ("close", "archive", "merge"))
        ],
    }


def classify_triage(triage: dict[str, Any]) -> dict[str, Any]:
    summary = triage.get("summary", {})
    open_prs = triage.get("open_prs", [])
    open_issues = triage.get("open_issues", [])
    failed_runs = triage.get("failed_workflow_runs", [])
    restart_queue = triage.get("pr_restart_queue", [])
    goal_items = planned_items_from_goal_config()
    fresh_prs = [pr for pr in open_prs if not pr.get("restart_required")]
    stale_prs = [pr for pr in open_prs if pr.get("restart_required")]
    stale_issues = [issue for issue in open_issues if issue.get("age_days", 0) >= 30]

    return {
        "summary": {
            "open_prs": summary.get("open_prs", len(open_prs)),
            "open_issues": summary.get("open_issues", len(open_issues)),
            "ready_prs": len(fresh_prs),
            "stale_prs": len(stale_prs),
            "stale_issues": len(stale_issues),
            "failed_workflow_runs": summary.get("failed_workflow_runs", len(failed_runs)),
            "restart_queue": summary.get("pr_restart_queue", len(restart_queue)),
            "planned_close_prs": len(goal_items["close_pr_candidates"]),
            "planned_close_issues": len(goal_items["close_issue_candidates"]),
        },
        "ready_prs": fresh_prs[:25],
        "stale_prs": stale_prs[:25],
        "stale_issues": stale_issues[:25],
        "failed_workflow_runs": failed_runs[:25],
        "restart_queue": restart_queue[:25],
        "cleanup_plan": goal_items,
    }


def check_quality() -> list[CheckResult]:
    return [check_json(), check_python(), check_javascript()]


def build_report() -> dict[str, Any]:
    triage = read_json(
        TRIAGE_REPORT,
        {
            "summary": {},
            "open_prs": [],
            "open_issues": [],
            "failed_workflow_runs": [],
            "pr_restart_queue": [],
        },
    )
    quality = check_quality()
    failed_checks = [check for check in quality if check.status == "fail"]
    skipped_checks = [check for check in quality if check.status == "skipped"]
    cleanup = classify_triage(triage)
    blockers = len(failed_checks) + cleanup["summary"]["failed_workflow_runs"]
    cleanroom_ready = blockers == 0

    return {
        "schema": "dreamco.repository_steward.v1",
        "generated_at": iso_now(),
        "repo": triage.get("repo", "DreamCo-Technologies/Dreamcobots"),
        "mission": "Keep pull requests, issues, comments, and workflow quality organized with evidence-first cleanup queues.",
        "policy": {
            "auto_close_without_owner_approval": False,
            "auto_merge_without_green_checks": False,
            "required_before_ready": [
                "json_parse",
                "python_syntax",
                "javascript_syntax",
                "workflow_failures_resolved_or_retested",
                "owner_approval_for_close_or_merge",
            ],
        },
        "summary": {
            **cleanup["summary"],
            "quality_checks": len(quality),
            "failed_quality_checks": len(failed_checks),
            "skipped_quality_checks": len(skipped_checks),
            "cleanroom_ready": cleanroom_ready,
        },
        "quality_checks": [check.__dict__ for check in quality],
        "queues": {
            "ready_prs": cleanup["ready_prs"],
            "stale_prs": cleanup["stale_prs"],
            "stale_issues": cleanup["stale_issues"],
            "failed_workflow_runs": cleanup["failed_workflow_runs"],
            "restart_queue": cleanup["restart_queue"],
        },
        "cleanup_plan": cleanup["cleanup_plan"],
        "next_actions": [
            "Merge or close duplicate PRs only after green checks and owner approval.",
            "Retest stale PRs before deciding whether their goals are already covered.",
            "Archive old attachment/import issues after confirming no unique requirement remains.",
            "Run this steward on schedule and before every production PR.",
        ],
    }


def write_markdown(report: dict[str, Any], path: Path) -> None:
    summary = report["summary"]
    lines = [
        "# Repository Stewardship Report",
        "",
        f"Generated: {report['generated_at']}",
        f"Repository: `{report['repo']}`",
        "",
        "## Cleanroom Summary",
        "",
        f"- **Cleanroom ready**: {summary['cleanroom_ready']}",
        f"- **Open PRs**: {summary['open_prs']}",
        f"- **Open issues**: {summary['open_issues']}",
        f"- **Ready PRs**: {summary['ready_prs']}",
        f"- **Stale PRs**: {summary['stale_prs']}",
        f"- **Stale issues**: {summary['stale_issues']}",
        f"- **Failed workflow runs**: {summary['failed_workflow_runs']}",
        f"- **Failed quality checks**: {summary['failed_quality_checks']}",
        "",
        "## Quality Gates",
        "",
    ]
    for check in report["quality_checks"]:
        lines.append(
            f"- **{check['name']}**: {check['status']} "
            f"({check['scanned']} scanned, {len(check['failures'])} failure(s))"
        )
        for failure in check["failures"][:10]:
            lines.append(f"  - `{failure['file']}`: {failure['error'].splitlines()[0]}")

    lines += ["", "## PR Cleanup Queue", ""]
    for pr in report["queues"]["stale_prs"][:15]:
        lines.append(f"- #{pr['number']} `{pr['head_branch']}` — {pr['title']}")
    if not report["queues"]["stale_prs"]:
        lines.append("- No stale PRs in the latest report.")

    lines += ["", "## Issue Cleanup Queue", ""]
    for issue in report["queues"]["stale_issues"][:15]:
        lines.append(f"- #{issue['number']} — {issue['title']} ({issue['age_days']} days old)")
    if not report["queues"]["stale_issues"]:
        lines.append("- No stale issues in the latest report.")

    lines += ["", "## Required Policy", ""]
    for item in report["policy"]["required_before_ready"]:
        lines.append(f"- {item}")

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--strict", action="store_true", help="Exit non-zero when the cleanroom is not ready.")
    args = parser.parse_args()

    REPORT_DIR.mkdir(exist_ok=True)
    report = build_report()
    (REPORT_DIR / "repository_stewardship_report.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    write_markdown(report, REPORT_DIR / "REPOSITORY_STEWARDSHIP_REPORT.md")
    print(json.dumps(report["summary"], indent=2))

    if args.strict and not report["summary"]["cleanroom_ready"]:
        sys.exit(1)


if __name__ == "__main__":
    main()
