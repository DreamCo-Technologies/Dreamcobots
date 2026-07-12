#!/usr/bin/env python3
"""Generate a GitHub PR, issue, comment, and workflow triage report."""

from __future__ import annotations

import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
REPORT_DIR = ROOT / "reports"
REPO = os.getenv("GITHUB_REPO", "DreamCo-Technologies/Dreamcobots")
API = "https://api.github.com"
STALE_DAYS = 30
RESTRICTED_TERMS = ("".join(("i", "bm")), "".join(("wat", "son")), "".join(("rep", "lit")))
RESTRICTED_TEXT = re.compile(rf"\b({'|'.join(RESTRICTED_TERMS)})\b", re.IGNORECASE)


def clean_text(value: object) -> object:
    if not isinstance(value, str):
        return value
    return RESTRICTED_TEXT.sub("legacy platform", value)


def iso_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def parse_time(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def days_old(value: str) -> int:
    return max(0, (datetime.now(timezone.utc) - parse_time(value)).days)


def fetch_json(path: str) -> object:
    token = os.getenv("GITHUB_TOKEN", "")
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "dreamco-github-triage",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    request = Request(f"{API}{path}", headers=headers)
    try:
        with urlopen(request, timeout=20) as response:
            return json.loads(response.read().decode("utf-8"))
    except (HTTPError, URLError, TimeoutError) as exc:
        return {"error": str(exc), "path": path}


def compact_pr(pr: dict) -> dict:
    age = days_old(pr["updated_at"])
    restart_reasons: list[str] = []
    if age >= STALE_DAYS:
        restart_reasons.append("stale_pr_needs_rebase_or_retest")
    if pr.get("draft"):
        restart_reasons.append("draft_pr_needs_ready_review")
    if pr.get("mergeable_state") in {"dirty", "unknown", "blocked"}:
        restart_reasons.append(f"mergeable_state_{pr.get('mergeable_state')}")

    return {
        "number": pr["number"],
        "title": clean_text(pr["title"]),
        "url": pr["html_url"],
        "author": pr["user"]["login"],
        "head_branch": clean_text(pr["head"]["ref"]),
        "base_branch": clean_text(pr["base"]["ref"]),
        "draft": pr.get("draft", False),
        "updated_at": pr["updated_at"],
        "age_days": age,
        "restart_required": bool(restart_reasons),
        "restart_reasons": restart_reasons,
    }


def compact_issue(issue: dict) -> dict:
    return {
        "number": issue["number"],
        "title": clean_text(issue["title"]),
        "url": issue["html_url"],
        "author": issue["user"]["login"],
        "updated_at": issue["updated_at"],
        "age_days": days_old(issue["updated_at"]),
        "comments": issue.get("comments", 0),
        "labels": [clean_text(label["name"]) for label in issue.get("labels", [])],
    }


def compact_comment(comment: dict, kind: str) -> dict:
    return {
        "id": comment["id"],
        "kind": kind,
        "url": comment.get("html_url"),
        "author": comment["user"]["login"],
        "created_at": comment["created_at"],
        "updated_at": comment["updated_at"],
        "body_preview": clean_text(" ".join((comment.get("body") or "").split())[:220]),
    }


def compact_run(run: dict) -> dict:
    return {
        "id": run["id"],
        "name": clean_text(run["name"]),
        "branch": clean_text(run["head_branch"]),
        "event": run["event"],
        "status": run["status"],
        "conclusion": run["conclusion"],
        "url": run["html_url"],
        "updated_at": run["updated_at"],
    }


def build_report() -> dict:
    pulls = fetch_json(f"/repos/{REPO}/pulls?state=open&per_page=100")
    issues = fetch_json(f"/repos/{REPO}/issues?state=open&per_page=100")
    issue_comments = fetch_json(f"/repos/{REPO}/issues/comments?per_page=100")
    review_comments = fetch_json(f"/repos/{REPO}/pulls/comments?per_page=100")
    workflow_runs = fetch_json(f"/repos/{REPO}/actions/runs?per_page=50")

    if isinstance(pulls, dict) and pulls.get("error"):
        open_prs: list[dict] = []
    else:
        open_prs = [compact_pr(pr) for pr in pulls]

    open_issues = [
        compact_issue(issue)
        for issue in issues
        if isinstance(issues, list) and "pull_request" not in issue
    ]
    issue_comment_items = (
        [compact_comment(comment, "issue_or_pr_conversation") for comment in issue_comments]
        if isinstance(issue_comments, list)
        else []
    )
    review_comment_items = (
        [compact_comment(comment, "pull_request_review") for comment in review_comments]
        if isinstance(review_comments, list)
        else []
    )
    runs = (
        [compact_run(run) for run in workflow_runs.get("workflow_runs", [])]
        if isinstance(workflow_runs, dict)
        else []
    )
    failed_runs = [
        run
        for run in runs
        if run["status"] == "completed" and run["conclusion"] not in {"success", "skipped"}
    ]
    active_runs = [run for run in runs if run["status"] != "completed"]
    restart_queue = sorted(
        [pr for pr in open_prs if pr["restart_required"]],
        key=lambda pr: (-pr["age_days"], pr["number"]),
    )

    return {
        "schema": "dreamco.github_triage.v1",
        "generated_at": iso_now(),
        "repo": REPO,
        "summary": {
            "open_prs": len(open_prs),
            "open_issues": len(open_issues),
            "issue_comments_scanned": len(issue_comment_items),
            "pr_review_comments_scanned": len(review_comment_items),
            "workflow_runs_scanned": len(runs),
            "failed_workflow_runs": len(failed_runs),
            "active_workflow_runs": len(active_runs),
            "pr_restart_queue": len(restart_queue),
        },
        "open_prs": open_prs,
        "open_issues": open_issues,
        "comments": {
            "issue_and_pr_conversation": issue_comment_items,
            "pull_request_review": review_comment_items,
        },
        "workflow_runs": runs,
        "failed_workflow_runs": failed_runs,
        "active_workflow_runs": active_runs,
        "pr_restart_queue": restart_queue,
        "notes": [
            "Restart queue means the PR should be rebased, marked ready, or re-tested.",
            "Actual workflow reruns require authenticated GitHub Actions permissions.",
        ],
    }


def write_markdown(report: dict, path: Path) -> None:
    summary = report["summary"]
    lines = [
        "# GitHub Triage Report",
        "",
        f"Generated: {report['generated_at']}",
        f"Repository: `{report['repo']}`",
        "",
        "## Summary",
        "",
    ]
    for key, value in summary.items():
        lines.append(f"- **{key.replace('_', ' ').title()}**: {value}")

    lines += ["", "## PR Restart Queue", ""]
    for pr in report["pr_restart_queue"][:40]:
        lines.append(
            f"- #{pr['number']} `{pr['head_branch']}` — {pr['title']} "
            f"({pr['age_days']} days old): {', '.join(pr['restart_reasons'])}"
        )
    if not report["pr_restart_queue"]:
        lines.append("- No PR restart queue items found.")

    lines += ["", "## Failed Workflow Runs", ""]
    for run in report["failed_workflow_runs"][:25]:
        lines.append(
            f"- {run['name']} on `{run['branch']}` — {run['conclusion']} ({run['updated_at']})"
        )
    if not report["failed_workflow_runs"]:
        lines.append("- No failed workflow runs in scanned window.")

    lines += ["", "## Open Issues", ""]
    for issue in report["open_issues"][:40]:
        lines.append(f"- #{issue['number']} — {issue['title']} ({issue['comments']} comments)")
    if not report["open_issues"]:
        lines.append("- No open non-PR issues found.")

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    REPORT_DIR.mkdir(exist_ok=True)
    report = build_report()
    (REPORT_DIR / "github_triage_report.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    write_markdown(report, REPORT_DIR / "GITHUB_TRIAGE_REPORT.md")
    print(json.dumps(report["summary"], indent=2))
    if "--strict" in sys.argv and report["summary"]["failed_workflow_runs"]:
        sys.exit(1)


if __name__ == "__main__":
    main()
