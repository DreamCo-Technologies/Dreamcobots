#!/usr/bin/env python3
"""Build an evidence-backed queue for PRs that need recovery onto current main."""
from __future__ import annotations

import argparse
import json
import os
import subprocess
from dataclasses import asdict, dataclass
from typing import Any

SENSITIVE_PREFIXES = (".github/workflows/", ".github/actions/")
SENSITIVE_EXACT = (".github/dependabot.yml", "CODEOWNERS")

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
    sensitive_paths: list[str] | None = None


def run(args: list[str], check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, text=True, capture_output=True, check=check)


def gh_json(args: list[str]) -> Any:
    return json.loads(run(["gh", *args]).stdout or "null")


def sensitive(paths: list[str]) -> list[str]:
    return [p for p in paths if p.startswith(SENSITIVE_PREFIXES) or p in SENSITIVE_EXACT]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", default=os.environ.get("GITHUB_REPOSITORY", "DreamCo-Technologies/Dreamcobots"))
    parser.add_argument("--limit", type=int, default=1000)
    parser.add_argument("--output", default="pr-recovery-queue.json")
    args = parser.parse_args()

    prs = gh_json(["pr", "list", "--repo", args.repo, "--state", "open", "--limit", str(args.limit), "--json", "number,title,headRefName,headRefOid,baseRefName,baseRefOid,mergeable,isDraft,changedFiles,state,headRepository,url"]) or []
    candidates: list[Candidate] = []
    for item in prs:
        mergeable = item.get("mergeable")
        draft = bool(item.get("isDraft"))
        base_branch = item.get("baseRefName") or ""
        if mergeable is not False and not draft and base_branch == "main":
            continue
        reasons: list[str] = []
        if mergeable is False: reasons.append("github reports merge conflict")
        if draft: reasons.append("draft")
        if base_branch != "main": reasons.append(f"base is {base_branch or 'unknown'}, not main")
        source = (item.get("headRepository") or {}).get("nameWithOwner") or args.repo
        candidate = Candidate(item["number"], item["title"], source, item.get("headRefName") or "", item.get("headRefOid") or "", base_branch, item.get("baseRefOid") or "", mergeable, draft, int(item.get("changedFiles") or 0), reasons, "queued")
        if not candidate.head_sha:
            candidate.status, candidate.details = "blocked", "missing head SHA"; candidates.append(candidate); continue
        fetched = run(["git", "fetch", "--no-tags", f"https://github.com/{source}.git", candidate.head_sha], check=False)
        if fetched.returncode != 0:
            candidate.status, candidate.details = "blocked", "source head could not be fetched"; candidates.append(candidate); continue
        contained = run(["git", "merge-base", "--is-ancestor", candidate.head_sha, "main"], check=False)
        if contained.returncode == 0:
            candidate.status, candidate.already_present, candidate.conflict_check, candidate.details = "already_present", True, "not_needed", "head commit is already an ancestor of main"; candidates.append(candidate); continue
        names = run(["git", "diff", "--name-only", f"main...{candidate.head_sha}"], check=False)
        paths = [p for p in names.stdout.splitlines() if p.strip()]
        candidate.sensitive_paths = sensitive(paths)
        if candidate.sensitive_paths:
            candidate.status = "blocked_sensitive"
            candidate.details = "automatic replay is disabled for workflow/ownership configuration changes; require explicit human review"
            candidates.append(candidate); continue
        diff = run(["git", "diff", "--stat", f"main...{candidate.head_sha}"], check=False)
        candidate.diff_stat = (diff.stdout or "").strip()
        if diff.returncode != 0:
            candidate.status, candidate.details = "blocked", (diff.stderr or "unable to compute diff")[-4000:]; candidates.append(candidate); continue
        patch = run(["git", "diff", "--binary", f"main...{candidate.head_sha}"], check=False)
        if patch.returncode != 0 or not patch.stdout:
            candidate.status, candidate.conflict_check, candidate.details = "blocked", "no_diff", "no replayable diff was produced"; candidates.append(candidate); continue
        applied = subprocess.run(["git", "apply", "--3way", "--check"], input=patch.stdout, text=True, capture_output=True, check=False)
        if applied.returncode == 0:
            candidate.status, candidate.conflict_check = "replayable", "clean"
        else:
            candidate.status, candidate.conflict_check, candidate.details = "blocked_conflict", "conflict", (applied.stderr or applied.stdout or "patch conflict")[-4000:]
        candidates.append(candidate)

    payload = {
        "schema_version": "2.1.0", "repository": args.repo, "base": "main", "generated_by": "tools/pr_recovery_engine.py",
        "policy": {"preserve_main": True, "preserve_all_source_changes": True, "never_force_resolve": True, "never_discard_conflicting_changes": True, "never_close_source_pr_automatically": True, "skip_exactly_present_heads": True, "block_sensitive_paths": True, "replacement_target": "main"},
        "summary": {"open_prs_scanned": len(prs), "candidates": len(candidates), "replayable": sum(c.status == "replayable" for c in candidates), "blocked_conflict": sum(c.status == "blocked_conflict" for c in candidates), "blocked_sensitive": sum(c.status == "blocked_sensitive" for c in candidates), "already_present": sum(c.status == "already_present" for c in candidates), "blocked": sum(c.status == "blocked" for c in candidates)},
        "candidates": [asdict(c) for c in candidates],
    }
    with open(args.output, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=2, sort_keys=True); fh.write("\n")
    print(json.dumps(payload["summary"], sort_keys=True))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
