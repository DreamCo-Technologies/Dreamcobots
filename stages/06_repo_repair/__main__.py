#!/usr/bin/env python3
"""Keyless Stage 06: plan deterministic generated-artifact repairs only."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from tools.buddy_safe_repair import repair_plan, run_safe_repair
from tools.ci_failure_report import sanitize

MAX_ATTEMPTS = 3
HARD_ALLOWED = (
    "artifacts/", "command-center/data/", "config/bots/",
    "config/generated/", "reports/", "website/data/",
)
FAMILIES = (
    (("dataset_route", "dataset-routes", "dataset_routes"), "dataset route index", "dataset-route"),
    (("division_model_fleet", "division-model-fleet"), "division model fleet", "division-fleet"),
    (("pages_connection_index", "pages-connection-index"), "pages connection index", "pages-connection"),
    (("actions_prospectus", "actions-prospectus"), "actions prospectus", "actions-prospectus"),
    (("file_prospectus", "file-prospectus"), "file prospectus", "file-prospectus"),
)


def read_object(path: str | Path) -> dict:
    value = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("Input JSON must be an object.")
    return value


def observation_from_report(report: dict, commit: str = "") -> dict:
    tests = report.get("tests")
    if not isinstance(tests, list) or len(tests) > 10000:
        raise ValueError("pytest-json-report must contain a bounded tests array.")
    failed = sorted({
        str(item.get("nodeid", ""))[:500]
        for item in tests
        if isinstance(item, dict) and item.get("outcome") in {"failed", "error"} and item.get("nodeid")
    })
    summary = report.get("summary") if isinstance(report.get("summary"), dict) else {}
    obs = {
        "repository": os.getenv("GITHUB_REPOSITORY", "local"),
        "workflow": "pytest report",
        "job": "pytest",
        "failed_step": "test suite",
        "error_signature": "pytest failure without an allowlisted generated-index match",
        "failure_class": "unknown",
        "commit": (commit or os.getenv("GITHUB_SHA", ""))[:40],
        "failed_test_count": max(len(failed), int(summary.get("failed", 0) or 0)),
        "failed_test_ids": failed[:100],
        "summary": {
            "passed": int(summary.get("passed", 0) or 0),
            "failed": int(summary.get("failed", len(failed)) or 0),
            "skipped": int(summary.get("skipped", 0) or 0),
        },
    }
    matches = []
    for needles, workflow, family in FAMILIES:
        if any(any(needle in node.lower() for needle in needles) for node in failed):
            matches.append((workflow, family))
    if len(matches) == 1:
        workflow, family = matches[0]
        obs.update({
            "workflow": workflow,
            "failed_step": workflow + " mismatch",
            "error_signature": "deterministic generated-index regression failed",
            "failure_class": "generated-index",
            "repair_family": family,
        })
    elif len(matches) > 1:
        obs["error_signature"] = "multiple generated-index families failed; manual triage required"
    return obs


def allowed_prefixes(value: str | None) -> tuple[str, ...]:
    requested = tuple(
        item.strip().rstrip("/") + "/"
        for item in (value.split(",") if value else HARD_ALLOWED)
        if item.strip()
    )
    if not requested or any(item not in HARD_ALLOWED for item in requested):
        raise ValueError("Allowed paths must be a subset of the fixed generated-artifact allowlist.")
    return tuple(dict.fromkeys(requested))


def path_is_allowed(path: str, prefixes: tuple[str, ...]) -> bool:
    item = PurePosixPath(path)
    return bool(item.parts) and not item.is_absolute() and ".." not in item.parts and any(
        item.as_posix().startswith(prefix) for prefix in prefixes
    )


def git(root: Path, *args: str) -> str:
    proc = subprocess.run(["git", *args], cwd=root, text=True, capture_output=True, timeout=20)
    if proc.returncode:
        raise RuntimeError(sanitize(proc.stderr)[-500:])
    return proc.stdout.strip()


def assert_trusted_main(root: Path, local_ok: bool) -> str:
    event, ref = os.getenv("GITHUB_EVENT_NAME", ""), os.getenv("GITHUB_REF", "")
    if event:
        if event in {"pull_request", "pull_request_target"} or ref != "refs/heads/main":
            raise PermissionError("Repair execution is disabled outside trusted main workflow runs.")
    elif not local_ok:
        raise PermissionError("Local execution requires --allow-local-apply.")
    if git(root, "branch", "--show-current") != "main":
        raise PermissionError("Repair execution requires the main branch.")
    if git(root, "status", "--porcelain", "--untracked-files=all"):
        raise PermissionError("Repair execution requires a clean working tree.")
    return git(root, "rev-parse", "HEAD")


def apply_isolated(root: Path, obs: dict, prefixes: tuple[str, ...], output: Path) -> dict:
    head = git(root, "rev-parse", "HEAD")
    with tempfile.TemporaryDirectory(prefix="dreamco-stage06-") as temp:
        worktree = Path(temp) / "repo"
        git(root, "worktree", "add", "--detach", str(worktree), head)
        try:
            repair = run_safe_repair(obs, worktree)
            status = git(worktree, "status", "--porcelain", "--untracked-files=all")
            changed = sorted({line[3:] for line in status.splitlines() if len(line) > 3})
            blocked = [path for path in changed if not path_is_allowed(path, prefixes)]
            if blocked:
                return {"status": "BLOCKED_UNEXPECTED_PATH", "success": False, "blocked_paths": blocked}
            if not changed:
                return {"status": repair.get("status", "REPAIR_RAN_NO_CHANGES"),
                        "success": bool(repair.get("success")), "changed_files": []}
            git(worktree, "add", "-N", "--", *changed)
            patch = git(worktree, "diff", "--binary", "--")
            output.parent.mkdir(parents=True, exist_ok=True)
            patch_path = output.with_suffix(".patch")
            patch_path.write_text(patch + ("\n" if patch and not patch.endswith("\n") else ""), encoding="utf-8")
            return {
                "status": "REPAIR_CANDIDATE_READY_FOR_REVIEW",
                "success": True,
                "changed_files": changed,
                "patch_file": str(patch_path.relative_to(root)),
                "commands": repair.get("commands", []),
            }
        finally:
            subprocess.run(
                ["git", "worktree", "remove", "--force", str(worktree)],
                cwd=root, text=True, capture_output=True, timeout=20, check=False,
            )


def run(args: argparse.Namespace) -> dict:
    root = Path(args.repo_root).resolve()
    prefixes = allowed_prefixes(args.allowed_paths)
    if bool(args.report) == bool(args.observation):
        raise ValueError("Provide exactly one of --report or --observation.")
    source = read_object(args.report or args.observation)
    obs = observation_from_report(source) if args.report else source
    commands = repair_plan(obs)
    fingerprint_data = {
        "commit": str(obs.get("commit", ""))[:40],
        "workflow": str(obs.get("workflow", ""))[:160],
        "job": str(obs.get("job", ""))[:160],
        "failed_step": str(obs.get("failed_step", ""))[:160],
        "failure_class": str(obs.get("failure_class", "unknown"))[:80],
        "failed_test_ids": obs.get("failed_test_ids", [])[:100],
    }
    fingerprint = hashlib.sha256(json.dumps(fingerprint_data, sort_keys=True).encode()).hexdigest()[:24]
    history_dir = (root / args.trajectory_dir).resolve()
    if root not in history_dir.parents:
        raise ValueError("Trajectory directory must remain inside the repository.")
    history_path = history_dir / (fingerprint + ".json")
    history = read_object(history_path) if history_path.exists() else {"schema": "dreamco.repo_repair_trajectory.v1", "attempts": []}
    result = {
        "schema": "dreamco.repo_repair_result.v1",
        "repair_mode": "deterministic_allowlist_only",
        "model_calls": 0,
        "api_key_required": False,
        "fingerprint": fingerprint,
        "failure_class": str(obs.get("failure_class", "unknown")),
        "failed_test_count": int(obs.get("failed_test_count", 0) or 0),
        "failed_test_ids": list(obs.get("failed_test_ids", []))[:100],
        "commands": commands,
        "attempts_used": len(history.get("attempts", [])),
        "max_attempts": args.max_attempts,
        "changed_files": [],
        "requires_human_review": True,
    }
    if args.report and not result["failed_test_count"]:
        result["status"] = "NO_FAILURES"
    elif not commands:
        result["status"] = "NO_ALLOWLISTED_AUTOMATIC_REPAIR"
    elif not args.apply:
        result["status"] = "DRY_RUN_REPAIR_PLAN"
    elif len(history.get("attempts", [])) >= args.max_attempts:
        result["status"] = "MAX_ATTEMPTS_REACHED"
    else:
        head = assert_trusted_main(root, args.allow_local_apply)
        result.update(apply_isolated(root, obs, prefixes, root / args.output))
        result["source_commit"] = head
        result["attempts_used"] = len(history.get("attempts", [])) + 1
        history.setdefault("attempts", []).append({
            "attempt": result["attempts_used"],
            "source_commit": head,
            "status": result["status"],
            "changed_files": result.get("changed_files", []),
            "recorded_at": datetime.now(timezone.utc).isoformat(),
        })
        history_dir.mkdir(parents=True, exist_ok=True)
        history_path.write_text(json.dumps(history, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    output = (root / args.output).resolve()
    if root not in output.parents:
        raise ValueError("Output path must remain inside the repository.")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--report", help="pytest-json-report file")
    group.add_argument("--observation", help="trusted workflow failure observation")
    parser.add_argument("--max-attempts", type=int, default=3)
    parser.add_argument("--allowed-paths", help="comma-separated subset of generated-artifact allowlist")
    parser.add_argument("--trajectory-dir", default="artifacts/repo-repair/trajectories")
    parser.add_argument("--output", default="artifacts/repo-repair/result.json")
    parser.add_argument("--repo-root", default=str(ROOT))
    parser.add_argument("--apply", action="store_true", help="execute deterministic repair in a detached worktree")
    parser.add_argument("--allow-local-apply", action="store_true", help="explicit local opt-in on clean main")
    args = parser.parse_args()
    if not 1 <= args.max_attempts <= MAX_ATTEMPTS:
        parser.error(f"--max-attempts must be between 1 and {MAX_ATTEMPTS}")
    try:
        result = run(args)
    except (OSError, ValueError, RuntimeError, PermissionError, subprocess.TimeoutExpired) as exc:
        print(json.dumps({"status": "BLOCKED", "reason": sanitize(str(exc))[:500]}), file=sys.stderr)
        return 2
    print(json.dumps(result, sort_keys=True))
    return 0 if result["status"] in {
        "NO_FAILURES", "NO_ALLOWLISTED_AUTOMATIC_REPAIR", "DRY_RUN_REPAIR_PLAN",
        "REPAIR_CANDIDATE_READY_FOR_REVIEW", "REPAIR_RAN_NO_CHANGES",
    } else 2


if __name__ == "__main__":
    raise SystemExit(main())
