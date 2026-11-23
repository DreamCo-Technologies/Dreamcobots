#!/usr/bin/env python3
"""Build a conservative, searchable index of historical repository repair commits.

This is a study/indexing step only. Git history does not prove that a change
fixed its original failure, so every record remains an unverified candidate.
No patches, logs, secrets, user data, or model-training examples are exported.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path
from typing import Sequence

ROOT = Path(__file__).resolve().parents[1]
TEST_PATTERN = re.compile(r"(^|/)(tests?/|test_[^/]+|[^/]+_test\.)")
CLASS_RULES = {
    "python": (".py",),
    "javascript": (".js", ".jsx", ".ts", ".tsx"),
    "workflow": (".yml", ".yaml"),
    "documentation": (".md", ".rst"),
    "configuration": (".json", ".toml", ".ini", ".cfg"),
}

def run_git(args: Sequence[str], cwd: Path = ROOT) -> str:
    result = subprocess.run(["git", *args], cwd=cwd, text=True,
                            capture_output=True, check=True, timeout=60)
    return result.stdout

def classify_paths(paths: list[str]) -> list[str]:
    found = []
    for label, suffixes in CLASS_RULES.items():
        if any(path.endswith(suffixes) for path in paths):
            found.append(label)
    return found or ["other"]

def build_index(limit: int = 500) -> dict:
    raw = run_git(["log", "--first-parent", f"-n{limit}",
                   "--format=%H%x1f%s"])
    records = []
    for line in raw.splitlines():
        if "\x1f" not in line:
            continue
        sha, subject = line.split("\x1f", 1)
        if not re.fullmatch(r"[0-9a-f]{40}", sha):
            continue
        files_raw = run_git(["diff-tree", "--no-commit-id", "--name-only",
                             "-r", sha])
        paths = sorted({p.strip() for p in files_raw.splitlines() if p.strip()})
        if not paths:
            continue
        tests = [p for p in paths if TEST_PATTERN.search(p)]
        subject_clean = re.sub(r"\s+", " ", subject).strip()[:240]
        records.append({
            "commit": sha,
            "subject": subject_clean,
            "changed_paths": paths,
            "test_paths": tests,
            "areas": classify_paths(paths),
            "search_terms": sorted(set(
                re.findall(r"[a-z0-9][a-z0-9_.-]{2,}",
                           (subject_clean + " " + " ".join(paths)).lower()
                ))),
            "learning_state": "HISTORICAL_CANDIDATE_REQUIRES_VERIFICATION",
            "verified_fix": False,
            "training_eligible": False,
        })
    return {
        "schema": "dreamco.buddy.historical_repair_index.v1",
        "source": "git_first_parent_history",
        "limit": limit,
        "record_count": len(records),
        "records": records,
        "policy": {
            "commit_history_is_not_proof_of_repair": True,
            "require_original_failure_and_regression_evidence": True,
            "require_human_review_and_rights_review_before_training": True,
            "include_raw_logs_or_patches": False,
        },
    }

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=500)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.limit < 1 or args.limit > 5000:
        parser.error("--limit must be between 1 and 5000")
    payload = build_index(args.limit)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"ok": True, "records": payload["record_count"],
                      "output": str(args.output)}, sort_keys=True))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
