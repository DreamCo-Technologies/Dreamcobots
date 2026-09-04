#!/usr/bin/env python3
"""Inventory stale/unmergeable PRs for safe replay onto current main."""
from __future__ import annotations

import argparse
import json
import os
import subprocess
from dataclasses import asdict, dataclass
from typing import Any


@dataclass
class PullRequestRecord:
    number: int
    title: str
    head: str
    head_sha: str
    base: str
    base_sha: str
    mergeable: bool | None
    draft: bool
    changed_files: int
    state: str
    source_repo: str
    status: str = "candidate"
    reason: str = ""


def gh_json(args: list[str]) -> Any:
    return json.loads(subprocess.check_output(["gh", *args], text=True))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", default=os.environ.get("GITHUB_REPOSITORY", "DreamCo-Technologies/Dreamcobots"))
    parser.add_argument("--limit", type=int, default=100)
    parser.add_argument("--output", default="pr-recovery-queue.json")
    args = parser.parse_args()

    prs = gh_json(["pr", "list", "--repo", args.repo, "--state", "open", "--limit", str(args.limit), "--json", "number,title,headRefName,headRefOid,baseRefName,baseRefOid,mergeable,isDraft,changedFiles,state,headRepository"])
    queue = []
    for item in prs:
        mergeable = item.get("mergeable")
        candidate = mergeable is False or bool(item.get("isDraft")) or item.get("baseRefName") != "main"
        if not candidate:
            continue
        reasons = []
        if mergeable is False: reasons.append("github reports merge conflict")
        if item.get("isDraft"): reasons.append("draft")
        if item.get("baseRefName") != "main": reasons.append(f"stale/non-main base: {item.get('baseRefName')}")
        queue.append(PullRequestRecord(
            number=item["number"], title=item["title"], head=item.get("headRefName") or "",
            head_sha=item.get("headRefOid") or "", base=item.get("baseRefName") or "",
            base_sha=item.get("baseRefOid") or "", mergeable=mergeable, draft=bool(item.get("isDraft")),
            changed_files=int(item.get("changedFiles") or 0), state=item.get("state") or "OPEN",
            source_repo=(item.get("headRepository") or {}).get("nameWithOwner") or args.repo,
            reason="; ".join(reasons)))

    payload = {
        "schema_version": "1.0.0", "repository": args.repo, "base": "main",
        "generated_by": "tools/pr_recovery.py",
        "policy": {"preserve_main": True, "never_force_resolve": True, "never_discard_conflicting_changes": True, "replacement_pr_target": "main"},
        "candidates": [asdict(x) for x in queue],
    }
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, sort_keys=True)
        f.write("\n")
    print(json.dumps({"candidates": len(queue), "output": args.output}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
