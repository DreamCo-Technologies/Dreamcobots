#!/usr/bin/env python3
"""Audit GitHub Actions live state without changing workflows or runs.

The audit fetches one repository-wide run stream and groups it by workflow ID.
This avoids one API request per workflow, which exhausted the Actions API rate
limit during concurrent PR validation. Coverage is explicitly reported when
the bounded run window cannot reach the full 30-day cutoff.
"""
from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT_JSON = ROOT / "config" / "generated" / "actions-live-health.json"
OUT_MD = ROOT / "reports" / "ACTIONS_LIVE_HEALTH.md"
PUBLIC_JSON = ROOT / "website" / "data" / "actions-live-health.json"
PER_PAGE = 100
MAX_RUN_PAGES = 12

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
    for attempt in range(3):
        try:
            with urllib.request.urlopen(request, timeout=20) as response:
                return json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            if exc.code in {403, 429} and attempt < 2:
                retry_after = exc.headers.get("Retry-After")
                try:
                    delay = max(2, min(20, int(retry_after))) if retry_after else 2 ** (attempt + 1)
                except ValueError:
                    delay = 2 ** (attempt + 1)
                print(f"GitHub API rate/abuse limit ({exc.code}); retrying in {delay}s", flush=True)
                time.sleep(delay)
                continue
            raise RuntimeError(f"GitHub API {exc.code} for {path}: {body[:600]}") from exc
    raise RuntimeError(f"GitHub API retries exhausted for {path}")


def parse_created_at(run: dict, fallback: datetime) -> datetime:
    try:
        return datetime.fromisoformat(run["created_at"].replace("Z", "+00:00"))
    except (KeyError, TypeError, ValueError):
        return fallback


def collect_recent_runs(repo: str, cutoff: datetime) -> tuple[list[dict], int, bool]:
    """Fetch recent runs in bounded pages; return whether the 30-day window is covered."""
    collected: list[dict] = []
    pages = 0
    covered = False
    for page in range(1, MAX_RUN_PAGES + 1):
        payload = api(f"/repos/{repo}/actions/runs?per_page={PER_PAGE}&page={page}")
        batch = payload.get("workflow_runs", [])
        pages += 1
        if not batch:
            covered = True
            break
        collected.extend(batch)
        oldest = parse_created_at(batch[-1], cutoff)
        if len(batch) < PER_PAGE or oldest < cutoff:
            covered = True
            break
    return collected, pages, covered


def build_workflow_rows(workflows: list[dict], runs: list[dict], local: set[str], cutoff: datetime) -> list[dict]:
    by_workflow: dict[int, list[dict]] = defaultdict(list)
    for run in runs:
        workflow_id = run.get("workflow_id")
        if workflow_id is not None and parse_created_at(run, cutoff) >= cutoff:
            by_workflow[workflow_id].append(run)

    rows = []
    for workflow in workflows:
        wid = workflow["id"]
        recent = sorted(by_workflow.get(wid, []), key=lambda item: item.get("created_at", ""), reverse=True)
        failures = [run for run in recent if run.get("conclusion") in {"failure", "timed_out", "action_required", "stale"}]
        latest = recent[0] if recent else None
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
            "recent_failure_urls": [run.get("html_url") for run in failures[:5]],
        })
    return rows


def main() -> int:
    repo = os.environ.get("GITHUB_REPOSITORY", "DreamCo-Technologies/Dreamcobots")
    workflows = api(f"/repos/{repo}/actions/workflows?per_page=100").get("workflows", [])
    local = {p.name for p in (ROOT / ".github" / "workflows").glob("*.yml")} | {p.name for p in (ROOT / ".github" / "workflows").glob("*.yaml")}
    cutoff = datetime.now(timezone.utc) - timedelta(days=30)
    runs, pages, coverage_complete = collect_recent_runs(repo, cutoff)
    rows = build_workflow_rows(workflows, runs, local, cutoff)

    target_rows = [row for row in rows if row["targeted"]]
    missing_targets = sorted(name for name in TARGETS if name not in local)
    orphan_active = sorted(row["path"] for row in rows if row["state"] == "active" and not row["local_file_present"])
    failing = [row for row in rows if row["recent_30d_failures"]]

    payload = {
        "schema": "dreamco.actions_live_health.v2",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "repository": repo,
        "workflow_count_from_github": len(rows),
        "target_count": len(TARGETS),
        "target_rows_found": len(target_rows),
        "target_files_missing_from_review_branch": missing_targets,
        "active_github_workflows_without_local_file": orphan_active,
        "workflows_with_recent_failures": len(failing),
        "run_records_sampled": len(runs),
        "run_pages_sampled": pages,
        "run_window_coverage_complete": coverage_complete,
        "run_window_note": "The 30-day window is complete." if coverage_complete else f"Only the newest {len(runs)} run records across {pages} pages were sampled; older 30-day runs may be omitted.",
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
        f"Run records sampled: **{len(runs)} across {pages} API page(s)**",
        f"30-day run-window coverage complete: **{coverage_complete}**",
        "",
        "## Target workflows",
    ]
    for row in target_rows:
        latest = row["latest_run"] or {}
        lines.append(f"- **{row['name']}** — state={row['state']} — local={row['local_file_present']} — latest={latest.get('conclusion') or latest.get('status') or 'not present in sampled window'} — recent failures={row['recent_30d_failures']}")
    if missing_targets:
        lines += ["", "## Target files missing from review branch"] + [f"- `{name}`" for name in missing_targets]
    if orphan_active:
        lines += ["", "## Active GitHub workflows with no local file"] + [f"- `{name}`" for name in orphan_active]
    lines += ["", "## Run-window coverage", payload["run_window_note"], "", "## Evidence boundary", payload["truth_boundary"]]
    OUT_MD.parent.mkdir(parents=True, exist_ok=True)
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({"ok": True, "workflows": len(rows), "targets": len(target_rows), "recent_failure_workflows": len(failing), "run_records_sampled": len(runs), "run_pages_sampled": pages, "coverage_complete": coverage_complete}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
