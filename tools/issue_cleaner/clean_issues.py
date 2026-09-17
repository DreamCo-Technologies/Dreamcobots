#!/usr/bin/env python3
"""
DreamCo Intelligent Issue Cleaner
---------------------------------
Processes up to BATCH_SIZE open issues per run (default 500).
Designed for repos flooded with auto-filed CI failure issues.

Rules (safe-by-default):
1. CI per-run issues ("Actions run <id> failed: <workflow>")
   - Group by workflow name
   - Keep the newest KEEP_PER_WORKFLOW open issues per workflow
   - Close older ones as not_planned (superseded)
2. Root-cause issues ("DreamCo failure root cause [key]: ...")
   - Keep newest per root-cause key; close older duplicates
3. Never close human issues unless they match explicit CI auto patterns
4. Apply triage labels to survivors when missing

Env:
  GITHUB_REPOSITORY  owner/repo (required)
  GITHUB_TOKEN / GH_TOKEN
  BATCH_SIZE         default 500
  KEEP_PER_WORKFLOW  default 2
  DRY_RUN            1 = no writes
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import time
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

BATCH_SIZE = int(os.environ.get("BATCH_SIZE", "500"))
KEEP_PER_WORKFLOW = int(os.environ.get("KEEP_PER_WORKFLOW", "2"))
DRY_RUN = os.environ.get("DRY_RUN", "0") == "1"
REPO = os.environ.get("GITHUB_REPOSITORY", "")
TOKEN = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN") or ""

CI_RUN_RE = re.compile(
    r"^Actions run (\d+) failed:\s*(.+)$", re.IGNORECASE
)
ROOT_CAUSE_RE = re.compile(
    r"^DreamCo failure root cause \[([0-9a-f]+)\]:\s*(.+)$",
    re.IGNORECASE,
)

AUTO_AUTHORS = {
    "github-actions",
    "github-actions[bot]",
    "dependabot",
    "dependabot[bot]",
}


@dataclass
class Issue:
    number: int
    title: str
    author: str
    created_at: str
    updated_at: str
    labels: list[str] = field(default_factory=list)
    comments: int = 0

    @property
    def created_dt(self) -> datetime:
        try:
            return datetime.fromisoformat(self.created_at.replace("Z", "+00:00"))
        except Exception:
            return datetime.now(timezone.utc)


@dataclass
class Stats:
    scanned: int = 0
    closed_superseded_ci: int = 0
    closed_dup_root: int = 0
    labeled: int = 0
    skipped_human: int = 0
    errors: int = 0
    kept: int = 0


def gh_json(args: list[str]) -> Any:
    cmd = ["gh", *args]
    env = os.environ.copy()
    if TOKEN:
        env["GH_TOKEN"] = TOKEN
    r = subprocess.run(cmd, capture_output=True, text=True, env=env)
    if r.returncode != 0:
        raise RuntimeError(f"gh {' '.join(args)} failed: {r.stderr.strip()}")
    if not r.stdout.strip():
        return None
    return json.loads(r.stdout)


def gh_run(args: list[str]) -> None:
    env = os.environ.copy()
    if TOKEN:
        env["GH_TOKEN"] = TOKEN
    if DRY_RUN:
        print(f"[DRY_RUN] gh {' '.join(args)}")
        return
    r = subprocess.run(["gh", *args], capture_output=True, text=True, env=env)
    if r.returncode != 0:
        raise RuntimeError(f"gh {' '.join(args)} failed: {r.stderr.strip()}")


def fetch_open_issues(limit: int) -> list[Issue]:
    out: list[Issue] = []
    page = 1
    per_page = 100
    while len(out) < limit:
        data = gh_json(
            [
                "api",
                f"repos/{REPO}/issues?state=open&per_page={per_page}&page={page}&sort=created&direction=desc",
            ]
        )
        if not data:
            break
        batch = data if isinstance(data, list) else []
        if not batch:
            break
        for row in batch:
            if "pull_request" in row:
                continue
            labels = [lb.get("name", "") for lb in row.get("labels") or []]
            user = (row.get("user") or {}).get("login") or ""
            out.append(
                Issue(
                    number=int(row["number"]),
                    title=(row.get("title") or "").strip(),
                    author=user,
                    created_at=row.get("created_at") or "",
                    updated_at=row.get("updated_at") or "",
                    labels=labels,
                    comments=int(row.get("comments") or 0),
                )
            )
            if len(out) >= limit:
                break
        if len(batch) < per_page:
            break
        page += 1
        time.sleep(0.2)
    return out


def close_issue(num: int, reason: str, comment: str) -> None:
    body = comment.strip()
    try:
        gh_run(
            [
                "issue",
                "comment",
                str(num),
                "--repo",
                REPO,
                "--body",
                body,
            ]
        )
        gh_run(
            [
                "issue",
                "close",
                str(num),
                "--repo",
                REPO,
                "--reason",
                reason,
            ]
        )
    except RuntimeError as e:
        if "reason" in str(e).lower():
            gh_run(["issue", "close", str(num), "--repo", REPO])
        else:
            raise


def ensure_labels(num: int, current: list[str], wanted: list[str]) -> bool:
    missing = [w for w in wanted if w not in current]
    if not missing:
        return False
    args = ["issue", "edit", str(num), "--repo", REPO]
    for lb in missing:
        args.extend(["--add-label", lb])
    gh_run(args)
    return True


def classify(issue: Issue) -> str:
    if CI_RUN_RE.match(issue.title):
        return "ci_run"
    if ROOT_CAUSE_RE.match(issue.title):
        return "root_cause"
    return "other"


def main() -> int:
    if not REPO:
        print("GITHUB_REPOSITORY is required", file=sys.stderr)
        return 2

    stats = Stats()
    print(
        f"Repo={REPO} BATCH_SIZE={BATCH_SIZE} "
        f"KEEP_PER_WORKFLOW={KEEP_PER_WORKFLOW} DRY_RUN={DRY_RUN}"
    )

    issues = fetch_open_issues(BATCH_SIZE)
    stats.scanned = len(issues)
    print(f"Fetched {len(issues)} open issues for this batch")

    ci_by_workflow: dict[str, list[Issue]] = defaultdict(list)
    root_by_key: dict[str, list[Issue]] = defaultdict(list)
    others: list[Issue] = []

    for issue in issues:
        kind = classify(issue)
        if kind == "ci_run":
            m = CI_RUN_RE.match(issue.title)
            assert m
            ci_by_workflow[m.group(2).strip()].append(issue)
        elif kind == "root_cause":
            m = ROOT_CAUSE_RE.match(issue.title)
            assert m
            root_by_key[m.group(1).lower()].append(issue)
        else:
            others.append(issue)

    for workflow, group in ci_by_workflow.items():
        group.sort(key=lambda i: i.created_dt, reverse=True)
        keep, drop = group[:KEEP_PER_WORKFLOW], group[KEEP_PER_WORKFLOW:]
        for issue in keep:
            stats.kept += 1
            try:
                if ensure_labels(
                    issue.number, issue.labels, ["ci-failure", "ci:workflow"]
                ):
                    stats.labeled += 1
            except Exception as e:
                print(f"label #{issue.number}: {e}", file=sys.stderr)
                stats.errors += 1
        for issue in drop:
            if issue.author not in AUTO_AUTHORS and issue.comments > 2:
                stats.skipped_human += 1
                continue
            newer = keep[0].number if keep else issue.number
            comment = (
                "**Intelligent Issue Cleaner** — superseded CI failure ticket.\n\n"
                f"Workflow **{workflow}** has newer open failure issue(s); "
                f"keeping the latest {KEEP_PER_WORKFLOW}. "
                f"See #{newer} for the current signal.\n\n"
                "_Closed automatically to reduce noise. "
                "Reopen if this run still needs a unique repair._"
            )
            try:
                close_issue(issue.number, "not_planned", comment)
                stats.closed_superseded_ci += 1
                print(f"Closed superseded CI #{issue.number} ({workflow})")
            except Exception as e:
                print(f"close #{issue.number}: {e}", file=sys.stderr)
                stats.errors += 1
            time.sleep(0.15)

    for key, group in root_by_key.items():
        group.sort(key=lambda i: i.created_dt, reverse=True)
        keep, drop = group[:1], group[1:]
        for issue in keep:
            stats.kept += 1
            try:
                if ensure_labels(issue.number, issue.labels, ["ci-failure"]):
                    stats.labeled += 1
            except Exception as e:
                print(f"label #{issue.number}: {e}", file=sys.stderr)
                stats.errors += 1
        for issue in drop:
            comment = (
                "**Intelligent Issue Cleaner** — duplicate root-cause key "
                f"`{key}`.\n\nCanonical issue: #{keep[0].number}. "
                "Closing this duplicate."
            )
            try:
                close_issue(issue.number, "duplicate", comment)
                stats.closed_dup_root += 1
                print(f"Closed dup root-cause #{issue.number}")
            except Exception as e:
                print(f"close #{issue.number}: {e}", file=sys.stderr)
                stats.errors += 1
            time.sleep(0.15)

    for issue in others:
        stats.kept += 1
        if issue.author in AUTO_AUTHORS and not issue.labels:
            try:
                if ensure_labels(issue.number, issue.labels, ["automation"]):
                    stats.labeled += 1
            except Exception:
                pass

    summary = {
        "scanned": stats.scanned,
        "closed_superseded_ci": stats.closed_superseded_ci,
        "closed_dup_root": stats.closed_dup_root,
        "labeled": stats.labeled,
        "skipped_human": stats.skipped_human,
        "kept": stats.kept,
        "errors": stats.errors,
        "dry_run": DRY_RUN,
        "workflows_seen": len(ci_by_workflow),
        "root_keys_seen": len(root_by_key),
    }
    print(json.dumps(summary, indent=2))

    summary_path = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary_path:
        lines = [
            "# Intelligent Issue Cleaner",
            "",
            f"- Scanned: **{stats.scanned}**",
            f"- Closed superseded CI: **{stats.closed_superseded_ci}**",
            f"- Closed duplicate root-cause: **{stats.closed_dup_root}**",
            f"- Labeled: **{stats.labeled}**",
            f"- Kept open: **{stats.kept}**",
            f"- Skipped (human signal): **{stats.skipped_human}**",
            f"- Errors: **{stats.errors}**",
            f"- Dry run: **{DRY_RUN}**",
            f"- CI workflows in batch: **{len(ci_by_workflow)}**",
            "",
            f"Keeps the newest {KEEP_PER_WORKFLOW} open CI-failure issues "
            "per workflow; closes older auto-filed tickets as superseded.",
        ]
        with open(summary_path, "a", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")

    return 0 if stats.errors == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
