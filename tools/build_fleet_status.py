#!/usr/bin/env python3
"""Write reports/FLEET_STATUS.md: PR states, CI run states, study-pack counts.

Read-only and best-effort: GitHub API data uses GITHUB_TOKEN/GH_TOKEN when set
(anonymous otherwise, public repo). Any unavailable source is reported as
"unavailable" instead of failing, so the report always exists. Always exits 0.
"""
from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "reports" / "FLEET_STATUS.md"
REPO = os.environ.get("GITHUB_REPOSITORY", "DreamCo-Technologies/Dreamcobots")
API = os.environ.get("GITHUB_API_URL", "https://api.github.com")


def gh_get(path: str):
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    err = None
    for auth in ([token, None] if token else [None]):  # bad token: retry anonymously
        req = urllib.request.Request(f"{API}/repos/{REPO}/{path}", headers={
            "Accept": "application/vnd.github+json", "User-Agent": "dreamco-fleet-status"})
        if auth:
            req.add_header("Authorization", f"Bearer {auth}")
        try:
            with urllib.request.urlopen(req, timeout=20) as resp:
                return json.load(resp), None
        except urllib.error.HTTPError as exc:
            err = f"HTTPError: {exc}"
            if exc.code != 401:
                break
        except Exception as exc:  # network/rate-limit: degrade, never fail
            err = f"{type(exc).__name__}: {exc}"
            break
    return None, err


def pr_section() -> list[str]:
    lines = ["## Pull requests", ""]
    open_prs, err = gh_get("pulls?state=open&per_page=100&sort=updated&direction=desc")
    recent, err2 = gh_get("pulls?state=closed&per_page=50&sort=updated&direction=desc")
    if open_prs is None:
        return lines + [f"- open PRs: unavailable ({err})", ""]
    drafts = sum(1 for p in open_prs if p.get("draft"))
    lines.append(f"- open: **{len(open_prs)}** (draft: {drafts}, ready: {len(open_prs) - drafts})"
                 + (" (first page only)" if len(open_prs) == 100 else ""))
    if recent is None:
        lines.append(f"- recently closed: unavailable ({err2})")
    else:
        merged = sum(1 for p in recent if p.get("merged_at"))
        lines.append(f"- last {len(recent)} closed: merged {merged}, closed unmerged {len(recent) - merged}")
    if open_prs:
        lines += ["", "| # | Title | Draft | Head | Updated (UTC) |", "| ---: | --- | --- | --- | --- |"]
        for p in open_prs[:25]:
            title = (p.get("title") or "").replace("|", "\\|")[:80]
            lines.append(f"| {p['number']} | {title} | {'yes' if p.get('draft') else 'no'} | "
                         f"`{(p.get('head') or {}).get('ref', '?')}` | {p.get('updated_at', '?')} |")
    return lines + [""]


def ci_section() -> list[str]:
    lines = ["## CI (latest run per workflow, from the 100 most recent runs)", ""]
    data, err = gh_get("actions/runs?per_page=100")
    if data is None:
        return lines + [f"- workflow runs: unavailable ({err})", ""]
    latest: dict[str, dict] = {}
    for run in data.get("workflow_runs", []):
        latest.setdefault(run.get("name") or str(run.get("workflow_id")), run)
    states = Counter((r.get("conclusion") or r.get("status") or "unknown") for r in latest.values())
    lines.append("- " + ", ".join(f"{k}: {v}" for k, v in sorted(states.items())) if states else "- no runs returned")
    failing = [(n, r) for n, r in sorted(latest.items()) if r.get("conclusion") in ("failure", "timed_out", "startup_failure")]
    if failing:
        lines += ["", "| Workflow | Conclusion | Branch | Run |", "| --- | --- | --- | --- |"]
        for name, r in failing:
            lines.append(f"| {name} | {r.get('conclusion')} | `{r.get('head_branch')}` | {r.get('html_url')} |")
    return lines + [""]


def pack_section() -> list[str]:
    lines = ["## Study packs", ""]
    packs_dir = ROOT / "study_packs"
    cfg = ROOT / "config" / "huggingface-capability-packs.json"
    try:
        declared = len(json.loads(cfg.read_text(encoding="utf-8")).get("packs", []))
    except Exception:
        declared = "unavailable"
    folders = sorted(p for p in packs_dir.iterdir() if p.is_dir()) if packs_dir.is_dir() else []
    with_card = sum(1 for p in folders if (p / "CARD.md").exists())
    evidence_files = sum(1 for p in packs_dir.glob("**/evidence/*") if p.is_file()) if packs_dir.is_dir() else 0
    lines += [f"- declared capability packs (config): {declared}",
              f"- pack folders in study_packs/: {len(folders)} (with CARD.md: {with_card})",
              f"- evidence files under study_packs/**/evidence: {evidence_files}"]
    return lines + [""]


def main() -> int:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    sha = os.environ.get("GITHUB_SHA", "local")
    lines = ["# Fleet Status", "", f"Generated: {now} · repo `{REPO}` · commit `{sha[:12]}`", "",
             "Read-only snapshot generated by CI so status exists without agents. "
             "Unavailable sources are labeled, not guessed.", ""]
    for section in (pr_section, ci_section, pack_section):
        try:
            lines += section()
        except Exception as exc:
            lines += [f"## {section.__name__}", "", f"- unavailable ({type(exc).__name__}: {exc})", ""]
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    print(f"wrote {REPORT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
