#!/usr/bin/env python3
"""Build an evidence-backed queue for PRs that need recovery onto current main.

The engine is deliberately conservative: it inventories candidates, records exact
source/base/head metadata, detects whether the proposed diff is already present,
and only marks a candidate replayable when Git can apply the full diff cleanly.
Actual PR creation is performed by the workflow after this evidence is generated.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
from dataclasses import asdict, dataclass
from typing import Any


@dataclass
class Candidate:
    number: int
    title: str
    source_repo: str
    head_branch: str
    head_sha: str
    base_branch: str
    base_sha: str
    mergeable: str | None
    draft: bool
    changed_files: int
    reason: list[str]
    status: str
    diff_stat: str = ""
    conflict_check: str = "unknown"
    already_present: bool = False
    details: str = ""


def run(args: list[str], check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, text=True, capture_output=True, check=check)


def gh_json(args: list[str]) -> Any:
    return json.loads(run(["gh", *args]).stdout or "null")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", default=os.environ.get("GITHUB_REPOSITORY", "DreamCo-Technologies/Dreamcobots"))
    parser.add_argument("--limit", type=int, default=1000)
    parser.add_argument("--output", default="pr-recovery-queue.json")
    args = parser.parse_args()

    prs = gh_json([
        "pr", "list", "--repo", args.repo, "--state", "open", "--limit", str(args.limit),
        "--json", "number,title,headRefName,headRefOid,baseRefName,baseRefOid,mergeable,isDraft,changedFiles,state,headRepository,url"
    ]) or []

    candidates: list[Candidate] = []
    for item in prs:
        mergeable = item.get("mergeable")
        draft = bool(item.get("isDraft"))
        base_branch = item.get("baseRefName") or ""
        if mergeable is not False and not draft and base_branch == "main":
            continue

        reasons: list[str] = []
        if mergeable is False:
            reasons.append("github reports merge conflict")
        if draft:
            reasons.append("draft")
        if base_branch != "main":
            reasons.append(f"base is {base_branch or 'unknown'}, not main")

        source = (item.get("headRepository") or {}).get("nameWithOwner") or args.repo
        head_sha = item.get("headRefOid") or ""
        base_sha = item.get("baseRefOid") or ""
        candidate = Candidate(
            number=item["number"], title=item["title"], source_repo=source,
            head_branch=item.get("headRefName") or "", head_sha=head_sha,
            base_branch=base_branch, base_sha=base_sha, mergeable=mergeable,
            draft=draft, changed_files=int(item.get("changedFiles") or 0),
            reason=reasons, status="queued"
        )

        if not head_sha:
            candidate.status = "blocked"
            candidate.details = "missing head SHA"
            candidates.append(candidate)
            continue

        # Fetch the source head. Public repositories can be read anonymously; the
        # workflow token is available to gh for the target repository.
        fetched = run(["git", "fetch", "--no-tags", f"https://github.com/{source}.git", head_sha], check=False)
        if fetched.returncode != 0:
            candidate.status = "blocked"
            candidate.details = "source head could not be fetched"
            candidates.append(candidate)
            continue

        # If main already contains the exact source head, there is nothing to recover.
        contained = run(["git", "merge-base", "--is-ancestor", head_sha, "main"], check=False)
        if contained.returncode == 0:
            candidate.status = "already_present"
            candidate.already_present = True
            candidate.conflict_check = "not_needed"
            candidate.details = "head commit is already an ancestor of main"
            candidates.append(candidate)
            continue

        diff = run(["git", "diff", "--stat", f"main...{head_sha}"], check=False)
        candidate.diff_stat = (diff.stdout or "").strip()
        if diff.returncode != 0:
            candidate.status = "blocked"
            candidate.details = (diff.stderr or "unable to compute diff")[-4000:]
            candidates.append(candidate)
            continue

        # Validate application without committing anything: apply the complete PR
        # diff in a temporary index/worktree check. This prevents silent dropping of
        # conflicting files and avoids mutating main.
        check_patch = run(["git", "diff", "--binary", f"main...{head_sha}"], check=False)
        if check_patch.returncode != 0 or not check_patch.stdout:
            candidate.status = "blocked"
            candidate.conflict_check = "no_diff"
            candidate.details = "no replayable diff was produced"
            candidates.append(candidate)
            continue

        temp_branch = f"recovery-check-{candidate.number}"
        branch_create = run(["git", "branch", "-f", temp_branch, "main"], check=False)
        if branch_create.returncode != 0:
            candidate.status = "blocked"
            candidate.details = (branch_create.stderr or "unable to create temporary validation ref")[-4000:]
            candidates.append(candidate)
            continue

        try:
            # git apply --3way against the current checkout's index is the safest
            # inexpensive compatibility signal available in the runner.
            check = subprocess.run(
                ["git", "diff", "--binary", f"main...{head_sha}"],
                text=True, capture_output=True, check=False,
            )
            applied = subprocess.run(
                ["git", "apply", "--3way", "--check"],
                input=check.stdout, text=True, capture_output=True, check=False,
            )
            if applied.returncode == 0:
                candidate.status = "replayable"
                candidate.conflict_check = "clean"
            else:
                candidate.status = "blocked_conflict"
                candidate.conflict_check = "conflict"
                candidate.details = (applied.stderr or applied.stdout or "patch conflict")[-4000:]
        finally:
            run(["git", "branch", "-D", temp_branch], check=False)

        candidates.append(candidate)

    payload = {
        "schema_version": "2.0.0",
        "repository": args.repo,
        "base": "main",
        "generated_by": "tools/pr_recovery_engine.py",
        "policy": {
            "preserve_main": True,
            "preserve_all_source_changes": True,
            "never_force_resolve": True,
            "never_discard_conflicting_changes": True,
            "never_close_source_pr_automatically": True,
            "skip_exactly_present_heads": True,
            "replacement_target": "main",
        },
        "summary": {
            "open_prs_scanned": len(prs),
            "candidates": len(candidates),
            "replayable": sum(c.status == "replayable" for c in candidates),
            "blocked_conflict": sum(c.status == "blocked_conflict" for c in candidates),
            "already_present": sum(c.status == "already_present" for c in candidates),
            "blocked": sum(c.status == "blocked" for c in candidates),
        },
        "candidates": [asdict(c) for c in candidates],
    }
    with open(args.output, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=2, sort_keys=True)
        fh.write("\n")
    print(json.dumps(payload["summary"], sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
