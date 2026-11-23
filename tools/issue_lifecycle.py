#!/usr/bin/env python3
"""Move a CI issue through explicit, evidence-backed lifecycle states."""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys

STATUSES = {"new", "investigating", "fixing", "retest", "blocked", "resolved"}
ACTIVE_RUN_STATES = {"queued", "pending", "in_progress", "waiting", "requested"}


def gh_api(path: str, method: str = "GET", payload: dict | None = None):
    command = ["gh", "api", path]
    if method != "GET":
        command += ["--method", method]
    if payload is not None:
        command += ["--input", "-"]
    result = subprocess.run(
        command,
        input=json.dumps(payload) if payload is not None else None,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode:
        raise RuntimeError(result.stderr.strip() or f"GitHub API request failed: {path}")
    return json.loads(result.stdout) if result.stdout.strip() else {}


def transition_labels(existing: list[str], status: str) -> list[str]:
    if status not in STATUSES:
        raise ValueError(f"Unsupported issue status: {status}")
    return sorted({label for label in existing if not label.startswith("status:")} | {f"status:{status}"})


def validate_evidence(status: str, issue_body: str, original_run: dict | None, candidate_run: dict | None) -> None:
    if status not in {"retest", "resolved"}:
        return
    if not original_run or not candidate_run:
        raise ValueError(f"Status {status} requires the original failed run and replacement run metadata.")
    if candidate_run.get("workflow_id") != original_run.get("workflow_id"):
        raise ValueError("Replacement evidence must come from the same workflow as the original failure.")
    if candidate_run.get("head_branch") != original_run.get("head_branch"):
        raise ValueError("Replacement evidence must come from the same branch as the original failure.")
    if status == "retest" and candidate_run.get("status") not in ACTIVE_RUN_STATES:
        raise ValueError("Retest status requires a matching workflow run that is still active or queued.")
    if status == "resolved" and not (
        candidate_run.get("status") == "completed" and candidate_run.get("conclusion") == "success"
    ):
        raise ValueError("Resolved status requires a completed, successful replacement run.")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--issue-number", type=int, required=True)
    parser.add_argument("--status", choices=sorted(STATUSES), required=True)
    parser.add_argument("--evidence-run-id")
    args = parser.parse_args()
    repo = os.environ["GITHUB_REPOSITORY"]
    issue = gh_api(f"repos/{repo}/issues/{args.issue_number}")
    if "pull_request" in issue:
        raise ValueError("This lifecycle command accepts Issues, not pull requests.")
    original_ids = re.findall(r"/actions/runs/(\d+)", issue.get("body") or "")
    original_run = gh_api(f"repos/{repo}/actions/runs/{original_ids[0]}") if original_ids else None
    candidate_run = gh_api(f"repos/{repo}/actions/runs/{args.evidence_run_id}") if args.evidence_run_id else None
    validate_evidence(args.status, issue.get("body") or "", original_run, candidate_run)
    existing = [label["name"] for label in issue.get("labels", [])]
    labels = transition_labels(existing, args.status)
    gh_api(f"repos/{repo}/issues/{args.issue_number}", "PATCH", {"labels": labels})
    if candidate_run:
        note = (
            f"Lifecycle status set to **{args.status}** using verified workflow evidence: "
            f"{candidate_run.get('html_url', '')} (\u0060{candidate_run.get('conclusion') or candidate_run.get('status')}\u0060). "
            "This action does not close the issue or bypass any required review."
        )
        gh_api(f"repos/{repo}/issues/{args.issue_number}/comments", "POST", {"body": note})
    print(json.dumps({"issue": args.issue_number, "status": args.status, "labels": labels}, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(1)
