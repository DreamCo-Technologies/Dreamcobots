#!/usr/bin/env python3
"""Read-only provenance gate for benchmark workflow_run/manual artifact handoffs."""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from urllib.request import Request, urlopen


EXPECTED_WORKFLOW_PATHS = {
    "Benchmark Evidence Loop": ".github/workflows/benchmark-evidence-loop.yml",
    "Benchmark Training Queue": ".github/workflows/benchmark-training-queue.yml",
}


def verify_run(run: object, *, run_id: str, expected_name: str, repository: str, expected_branch: str) -> list[str]:
    """Reject wrong, failed, cross-repository, cross-workflow, or cross-branch runs."""
    if not re.fullmatch(r"[1-9][0-9]{0,19}", run_id):
        return ["source run ID must be a positive decimal integer"]
    if not isinstance(run, dict):
        return ["upstream run metadata must be an object"]
    problems = []
    if str(run.get("id")) != run_id:
        problems.append("source run ID does not match API metadata")
    if run.get("name") != expected_name:
        problems.append("unexpected upstream workflow")
    expected_path = EXPECTED_WORKFLOW_PATHS.get(expected_name)
    actual_path = run.get("path")
    if not expected_path:
        problems.append("upstream workflow has no registered source path")
    elif not isinstance(actual_path, str):
        problems.append("upstream workflow source path is missing or malformed")
    else:
        workflow_path, separator, workflow_ref = actual_path.partition("@")
        if workflow_path != expected_path or not separator or not workflow_ref.strip():
            problems.append("upstream workflow source path does not match registered workflow")
    if run.get("status") != "completed" or run.get("conclusion") != "success":
        problems.append("upstream workflow has no completed passing run")
    for key in ("repository", "head_repository"):
        owner = run.get(key)
        if not isinstance(owner, dict) or owner.get("full_name") != repository:
            problems.append(f"{key} is not the expected repository")
    if not isinstance(expected_branch, str) or not expected_branch.strip():
        problems.append("current workflow branch is missing")
    elif run.get("head_branch") != expected_branch:
        problems.append("source run branch does not match current workflow branch")
    return problems


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--expected", required=True)
    args = parser.parse_args(argv)
    repository = os.environ.get("GITHUB_REPOSITORY", "")
    branch = os.environ.get("GITHUB_REF_NAME", "")
    token = os.environ.get("GITHUB_TOKEN", "")
    if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repository):
        print("Benchmark handoff blocked: invalid repository identity", file=sys.stderr)
        return 2
    if not re.fullmatch(r"[1-9][0-9]{0,19}", args.run_id) or not token:
        print("Benchmark handoff blocked: valid source run ID and read token required", file=sys.stderr)
        return 2
    if not branch or branch.startswith("refs/"):
        print("Benchmark handoff blocked: current workflow branch unavailable", file=sys.stderr)
        return 2
    url = f"https://api.github.com/repos/{repository}/actions/runs/{args.run_id}"
    request = Request(url, headers={
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
        "X-GitHub-Api-Version": "2022-11-28",
    })
    try:
        with urlopen(request, timeout=15) as response:
            metadata = json.load(response)
    except (OSError, ValueError) as exc:
        print(f"Benchmark handoff blocked: source run metadata unavailable ({type(exc).__name__})", file=sys.stderr)
        return 2
    problems = verify_run(metadata, run_id=args.run_id, expected_name=args.expected,
                          repository=repository, expected_branch=branch)
    if problems:
        print("Benchmark handoff blocked: " + "; ".join(problems), file=sys.stderr)
        return 2
    print(f"Verified passing upstream run {args.run_id} from {args.expected} in {repository} on {branch}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
