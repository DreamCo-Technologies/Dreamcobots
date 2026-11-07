#!/usr/bin/env python3
"""Read-only, whole-repository health inventory for the five-minute Actions audit.

The audit never edits files, merges PRs, starts training, or treats URLs/metadata as
learning. Findings are written to reports/repository-health-latest.json and the
GitHub Actions job summary. Critical static failures make the job fail honestly.
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "reports" / "repository-health-latest.json"
GOALS = ROOT / "config" / "repository-goals.json"
SUMMARY = os.environ.get("GITHUB_STEP_SUMMARY")
REPO = os.environ.get("GITHUB_REPOSITORY", "")
TOKEN = os.environ.get("GH_TOKEN", "")
SHA = os.environ.get("GITHUB_SHA", "")
RUN_ID = os.environ.get("GITHUB_RUN_ID", "")

def command(args: list[str]) -> tuple[int, str, str]:
    result = subprocess.run(args, cwd=ROOT, text=True, capture_output=True, check=False)
    return result.returncode, result.stdout, result.stderr

def tracked_files() -> list[Path]:
    code, out, err = command(["git", "ls-files", "-z"])
    if code:
        raise RuntimeError("git ls-files failed: " + err[-2000:])
    return [ROOT / p for p in out.split("\0") if p]

def github_open_prs() -> dict:
    if not TOKEN or not REPO or "/" not in REPO:
        return {"available": False, "reason": "GitHub token/repository context unavailable"}
    url = f"https://api.github.com/repos/{REPO}/pulls?state=open&per_page=100&sort=updated&direction=desc"
    req = urllib.request.Request(url, headers={
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {TOKEN}",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "DreamCo-Repository-Health-Audit",
    })
    try:
        with urllib.request.urlopen(req, timeout=20) as response:
            items = json.loads(response.read().decode("utf-8"))
        return {
            "available": True,
            "count": len(items),
            "draft_count": sum(bool(x.get("draft")) for x in items),
            "ready_count": sum(not bool(x.get("draft")) for x in items),
            "items": [{
                "number": x["number"],
                "title": x["title"],
                "draft": x.get("draft", False),
                "url": x["html_url"],
                "updated_at": x.get("updated_at"),
                "head_sha": (x.get("head") or {}).get("sha"),
                "mergeable": x.get("mergeable"),
                "mergeable_state": x.get("mergeable_state"),
            } for x in items],
            "truncated": len(items) == 100,
        }
    except (urllib.error.URLError, TimeoutError, ValueError) as exc:
        return {"available": False, "reason": str(exc)}

def main() -> int:
    files = tracked_files()
    findings: list[dict] = []
    counts = {"tracked_files": len(files), "json_files": 0, "python_files": 0,
              "html_files": 0, "workflow_files": 0}

    def add(severity: str, code: str, path: str, message: str) -> None:
        findings.append({"severity": severity, "code": code, "path": path, "message": message})

    # Required project entry points: missing files are surfaced as critical findings.
    for required in ("README.md", ".gitignore", ".github/workflows"):
        if not (ROOT / required).exists():
            add("critical", "required_path_missing", required, "Required repository path is missing.")

    for path in files:
        if not path.is_file():
            continue
        rel = path.relative_to(ROOT).as_posix()
        if any(part in {".git", "node_modules", ".venv", "venv"} for part in path.parts):
            continue
        suffix = path.suffix.lower()
        try:
            raw = path.read_bytes()
        except OSError as exc:
            add("warning", "file_unreadable", rel, str(exc))
            continue
        if suffix == ".json":
            counts["json_files"] += 1
            try:
                json.loads(raw.decode("utf-8"))
            except Exception as exc:
                add("critical", "invalid_json", rel, str(exc))
        elif suffix == ".py":
            counts["python_files"] += 1
            try:
                compile(raw.decode("utf-8"), rel, "exec")
            except Exception as exc:
                add("critical", "python_syntax_error", rel, str(exc))
        elif suffix == ".html":
            counts["html_files"] += 1
            html = raw.decode("utf-8", errors="replace")
            # Match the repository's shared-controls contract.
            if not re.search(r'<script[^>]+src=["\'][^"\']*(?:nav|desk-chrome|repository-actions)\.js(?:[?][^"\']*)?["\']', html, re.I):
                add("critical", "page_controls_disconnected", rel,
                    "HTML page does not load nav.js, desk-chrome.js, or repository-actions.js.")
        if rel.startswith(".github/workflows/") and suffix in {".yml", ".yaml"}:
            counts["workflow_files"] += 1

    # Check that the workflow inventory itself is non-empty.
    if counts["workflow_files"] == 0:
        add("critical", "no_workflows", ".github/workflows", "No tracked GitHub Actions workflows found.")

    goals = {"available": False, "reason": "Goal registry missing or invalid"}
    try:
        goals_data = json.loads(GOALS.read_text(encoding="utf-8"))
        goals = {
            "available": True,
            "schema": goals_data.get("schema"),
            "updated_at": goals_data.get("updated_at"),
            "goals": goals_data.get("goals", []),
        }
    except (OSError, ValueError) as exc:
        add("warning", "goal_registry_unavailable", str(GOALS.relative_to(ROOT)), str(exc))

    prs = github_open_prs()
    if not prs.get("available"):
        add("warning", "pr_inventory_unavailable", "GitHub API", prs.get("reason", "Unknown API error"))
    elif prs.get("truncated"):
        add("warning", "pr_inventory_truncated", "GitHub API",
            "More than 100 open PRs; API pagination is required for a complete inventory.")

    critical = sum(x["severity"] == "critical" for x in findings)
    warnings = sum(x["severity"] == "warning" for x in findings)
    report = {
        "schema": "dreamco.repository_health_audit.v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "repository": REPO,
        "commit_sha": SHA,
        "workflow_run_id": RUN_ID,
        "mode": "read_only_static_inventory",
        "counts": counts,
        "pull_requests": prs,
        "goal_registry": goals,
        "finding_counts": {"critical": critical, "warning": warnings},
        "findings": findings,
        "limitations": [
            "Static checks do not prove runtime integrations work.",
            "This five-minute job does not run the entire expensive test suite by default.",
            "PR inventory does not prove each PR is safe to merge; required checks and review remain separate gates.",
            "No files are modified and no pull requests are merged automatically.",
        ],
    }
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    lines = [
        "## DreamCo repository health audit",
        f"- Revision: `{SHA or 'unknown'}`",
        f"- Tracked files: **{counts['tracked_files']}** ({counts['json_files']} JSON, {counts['python_files']} Python, {counts['html_files']} HTML, {counts['workflow_files']} workflows)",
        f"- Open pull requests: **{prs.get('count', 'unavailable')}**; drafts: {prs.get('draft_count', 'n/a')}",
        f"- Findings: **{critical} critical**, **{warnings} warnings**",
        "",
        "### Findings",
    ]
    if findings:
        lines.extend(f"- **{x['severity'].upper()} · {x['code']}** — `{x['path']}`: {x['message']}" for x in findings[:100])
        if len(findings) > 100:
            lines.append(f"- … {len(findings) - 100} additional findings are in the JSON artifact.")
    else:
        lines.append("- No static inventory findings.")
    lines.extend(["", "> Read-only audit. A clean static scan is not a production certification or a merge approval."])
    summary = "\n".join(lines) + "\n"
    if SUMMARY:
        with open(SUMMARY, "a", encoding="utf-8") as handle:
            handle.write(summary)
    print(summary)
    return 1 if critical else 0

if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"Repository audit crashed: {exc}", file=sys.stderr)
        raise
