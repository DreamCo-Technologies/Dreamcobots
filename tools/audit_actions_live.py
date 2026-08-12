#!/usr/bin/env python3
"""Audit GitHub Actions live state without changing workflows or runs.

Requires GITHUB_TOKEN and GITHUB_REPOSITORY in Actions. Static repository health
and live GitHub run health are intentionally separate evidence classes.
"""
from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT_JSON = ROOT / "config" / "generated" / "actions-live-health.json"
OUT_MD = ROOT / "reports" / "ACTIONS_LIVE_HEALTH.md"
PUBLIC_JSON = ROOT / "website" / "data" / "actions-live-health.json"

TARGETS = {
    "dreamcobots_workflows.yml",
    "observability.yml",
    "actions-failure-sweep.yml",
    "actions-failure-watch.yml",
    "actions-health.yml",
    "all-bot-sandbox-campaign.yml",
    "buddy-actions-test-lab.yml",
    "builder-issue-reconciler.yml",
    "ci.yml",
    "ci-automation.yml",
    "code-trust-gate.yml",
    "deploy-buddy-pages.yml",
    "dreamco-build.yml",
    "dreamco.yml",
    "dreamco-live-dashboard.yml",
    "repository-system-watch.yml",
}


def api(path: str) -> dict:
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if not token:
        raise RuntimeError("GITHUB_TOKEN/GH_TOKEN is required for live Actions audit")
    request = urllib.request.Request(
        "https://api.github.com" + path,
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "DreamCo-Actions-Health",
        },
    )
    with urllib.request.urlopen(request, timeout=20) as response:
        return json.loads(response.read().decode("utf-8"))


def main() -> int:
    repo = os.environ.get("GITHUB_REPOSITORY", "DreamCo-Technologies/Dreamcobots")
    workflows = api(f"/repos/{repo}/actions/workflows?per_page=100").get("workflows", [])
    local = {p.name for p in (ROOT / ".github" / "workflows").glob("*.yml")} | {p.name for p in (ROOT / ".github" / "workflows").glob("*.yaml")}
    cutoff = datetime.now(timezone.utc) - timedelta(days=30)
    rows = []
    for workflow in workflows:
        wid = workflow["id"]
        runs = api(f"/repos/{repo}/actions/workflows/{wid}/runs?per_page=10").get("workflow_runs", [])
        recent = []
        for run in runs:
            try:
                dt = datetime.fromisoformat(run["created_at"].replace("Z", "+00:00"))
            except Exception:
                dt = cutoff
            if dt >= cutoff:
                recent.append(run)
        failures = [r for r in recent if r.get("conclusion") in {"failure", "timed_out", "action_required", "stale"}]
        latest = runs[0] if runs else None
        path = workflow.get("path", "")
        filename = Path(path).name
        rows.append({
            "id": wid,
            "name": workflow.get("name"),
            "path": path,
            "state": workflow.get("state"),
            "local_file_present": filename in local,
            "targeted": filename in TARGETS,
            "latest_run": {
                "id": latest.get("id"),
                "status": latest.get("status"),
                "conclusion": latest.get("conclusion"),
                "created_at": latest.get("created_at"),
                "url": latest.get("html_url"),
                "head_sha": latest.get("head_sha"),
            } if latest else None,
            "recent_30d_runs": len(recent),
            "recent_30d_failures": len(failures),
            "recent_failure_urls": [r.get("html_url") for r in failures[:5]],
        })

    target_rows = [r for r in rows if r["targeted"]]
    missing_targets = sorted(name for name in TARGETS if name not in local)
    orphan_active = sorted(r["path"] for r in rows if r["state"] == "active" and not r["local_file_present"])
    failing = [r for r in rows if r["recent_30d_failures"]]

    payload = {
        "schema": "dreamco.actions_live_health.v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "repository": repo,
        "workflow_count_from_github": len(rows),
        "target_count": len(TARGETS),
        "target_rows_found": len(target_rows),
        "target_files_missing_from_review_branch": missing_targets,
        "active_github_workflows_without_local_file": orphan_active,
        "workflows_with_recent_failures": len(failing),
        "target_workflows": target_rows,
        "all_workflows": rows,
        "truth_boundary": "Live run state proves observed GitHub execution status only. It does not prove application correctness, benchmark mastery, or production readiness.",
    }
    for output in (OUT_JSON, PUBLIC_JSON):
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# GitHub Actions Live Health",
        "",
        f"GitHub-reported workflows: **{len(rows)}**",
        f"Requested target workflows: **{len(TARGETS)}**",
        f"Target workflow records found: **{len(target_rows)}**",
        f"Target files missing on review branch: **{len(missing_targets)}**",
        f"Active GitHub workflows without a local workflow file: **{len(orphan_active)}**",
        f"Workflows with failures in the last 30 days: **{len(failing)}**",
        "",
        "## Target workflows",
    ]
    for row in target_rows:
        latest = row["latest_run"] or {}
        lines.append(f"- **{row['name']}** — state={row['state']} — local={row['local_file_present']} — latest={latest.get('conclusion') or latest.get('status') or 'never observed'} — recent failures={row['recent_30d_failures']}")
    if missing_targets:
        lines += ["", "## Target files missing from review branch"] + [f"- `{x}`" for x in missing_targets]
    if orphan_active:
        lines += ["", "## Active GitHub workflows with no local file"] + [f"- `{x}`" for x in orphan_active]
    lines += ["", "## Evidence boundary", payload["truth_boundary"]]
    OUT_MD.parent.mkdir(parents=True, exist_ok=True)
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({"ok": True, "workflows": len(rows), "targets": len(target_rows), "recent_failure_workflows": len(failing)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
