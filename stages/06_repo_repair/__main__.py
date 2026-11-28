#!/usr/bin/env python3
"""Keyless, deterministic Stage 06 repository repair planner.

This stage never asks a model to rewrite source files. It recognizes a small
set of generated-index test failures and delegates only to the repository's
existing deterministic repair command registry. PR runs are diagnostic-only;
applying repairs requires a clean, trusted main checkout.
"""
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
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.buddy_safe_repair import repair_plan, run_safe_repair
from tools.ci_failure_report import sanitize

MAX_ATTEMPTS = 3
HARD_ALLOWED_PREFIXES = (
    "artifacts/",
    "command-center/data/",
    "config/bots/",
    "config/generated/",
    "reports/",
    "website/data/",
)
FAMILY_RULES = (
    ("dataset-route", ("dataset_route", "dataset-routes", "dataset_routes"), "dataset route index", "dataset route index mismatch"),
    ("division-fleet", ("division_model_fleet", "division-model-fleet"), "division model fleet", "division model fleet index mismatch"),
    ("pages-connection", ("pages_connection_index", "pages-connection-index"), "pages connection index", "pages connection index mismatch"),
    ("actions-prospectus", ("actions_prospectus", "actions-prospectus"), "actions prospectus", "actions prospectus index mismatch"),
    ("file-prospectus", ("file_prospectus", "file-prospectus"), "file prospectus", "file prospectus index mismatch"),
)


def _read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("Input JSON must contain an object.")
    return value


def _failed_tests(report: dict[str, Any]) -> list[str]:
    tests = report.get("tests")
    if not isinstance(tests, list):
        raise ValueError("pytest-json-report must contain a tests array.")
    if len(tests) > 10000:
        raise ValueError("Test report exceeds the 10,000-test safety limit.")
    failed = []
    for item in tests:
        if not isinstance(item, dict):
            continue
        if str(item.get("outcome", "")).lower() in {"failed", "error"}:
            nodeid = str(item.get("nodeid", "")).strip()
            if nodeid:
                failed.append(nodeid[:500])
    return sorted(set(failed))


def observation_from_report(report: dict[str, Any], commit: str = "") -> dict[str, Any]:
    failed = _failed_tests(report)
    summary = report.get("summary") if isinstance(report.get("summary"), dict) else {}
    observation: dict[str, Any] = {
        "repository": os.environ.get("GITHUB_REPOSITORY", "local"),
        "workflow": "pytest report",
        "job": "pytest",
        "failed_step": "test suite",
        "error_signature": "pytest failure without an allowlisted generated-index match",
        "commit": (commit or os.environ.get("GITHUB_SHA", ""))[:40],
        "failure_class": "unknown",
        "failed_test_count": len(failed),
        "failed_test_ids": failed[:100],
        "summary": {
            "passed": int(summary.get("passed", 0) or 0),
            "failed": int(summary.get("failed", len(failed)) or 0),
            "skipped": int(summary.get("skipped", 0) or 0),
            "error": int(summary.get("error", 0) or 0),
        },
    }
    if not failed:
        return observation

    matches = []
    lowered = [nodeid.lower() for nodeid in failed]
    for family, needles, workflow, step in FAMILY_RULES:
        if any(any(needle in nodeid for needle in needles) for nodeid in lowered):
            matches.append((family, workflow, step))
    if len(matches) == 1:
        family, workflow, step = matches[0]
        observation.update({
            "workflow": workflow,
            "failed_step": step,
            "error_signature": "deterministic generated-index regression failed",
            "failure_class": "generated-index",
            "repair_family": family,
        })
    elif len(matches) > 1:
        observation["error_signature"] = "multiple generated-index repair families failed; manual triage required"
    return observation


def validate_allowed_paths(value: str | None) -> tuple[str, ...]:
    requested = tuple(
        part.strip().rstrip("/") + "/"
        for part in (value.split(",") if value else HARD_ALLOWED_PREFIXES)
        if part.strip()
    )
    if not requested:
        raise ValueError("At least one generated-artifact path prefix is required.")
    if any(prefix not in HARD_ALLOWED_PREFIXES for prefix in requested):
        raise ValueError("Allowed paths must be selected from the hard-coded generated-artifact allowlist.")
    return tuple(dict.fromkeys(requested))


def _is_allowed_path(path: str, prefixes: tuple[str, ...]) -> bool:
    candidate = PurePosixPath(path)
    if candidate.is_absolute() or ".." in candidate.parts or not candidate.parts:
        return False
    normalized = candidate.as_posix()
    return any(normalized.startswith(prefix) for prefix in prefixes)


def _git(root: Path, *args: str, timeout: int = 20) -> str:
    proc = subprocess.run(
        ["git", *args], cwd=root, text=True, capture_output=True,
        timeout=timeout, check=False,
    )
    if proc.returncode:
        raise RuntimeError("Git operation failed: " + sanitize(proc.stderr)[-500:])
    return proc.stdout.strip()


def _assert_apply_context(root: Path, allow_local_apply: bool) -> str:
    event = os.environ.get("GITHUB_EVENT_NAME", "")
    ref = os.environ.get("GITHUB_REF", "")
    if event:
        if event in {"pull_request", "pull_request_target"} or ref != "refs/heads/main":
            raise PermissionError("Repair execution is disabled for pull-request and non-main workflow contexts.")
    elif not allow_local_apply:
        raise PermissionError("Local repair execution requires the explicit --allow-local-apply flag.")
    branch = _git(root, "branch", "--show-current")
    if branch != "main":
        raise PermissionError("Repair execution requires the trusted main branch.")
    if _git(root, "status", "--porcelain", "--untracked-files=all"):
        raise PermissionError("Repair execution requires a clean working tree.")
    return _git(root, "rev-parse", "HEAD")


def _apply_in_worktree(
    root: Path,
    observation: dict[str, Any],
    prefixes: tuple[str, ...],
    output_path: Path,
) -> dict[str, Any]:
    head = _git(root, "rev-parse", "HEAD")
    with tempfile.TemporaryDirectory(prefix="dreamco-stage06-") as temp:
        worktree = Path(temp) / "repo"
        _git(root, "worktree", "add", "--detach", str(worktree), head)
        try:
            repair = run_safe_repair(observation, worktree)
            status = _git(worktree, "status", "--porcelain", "--untracked-files=all")
            changed = []
            for line in status.splitlines():
                if len(line) < 4:
                    continue
                path = line[3:]
                if " -> " in path:
                    path = path.split(" -> ", 1)[1]
                changed.append(path)
            changed = sorted(set(changed))
            unsafe = [path for path in changed if not _is_allowed_path(path, prefixes)]
            if unsafe:
                return {
                    "status": "BLOCKED_UNEXPECTED_PATH",
                    "success": False,
                    "changed_files": changed,
                    "blocked_paths": unsafe,
                    "commands": repair.get("commands", []),
                }
            if not changed:
                return {
                    "status": repair.get("status", "REPAIR_RAN_NO_CHANGES"),
                    "success": bool(repair.get("success")),
                    "changed_files": [],
                    "commands": repair.get("commands", []),
                }
            _git(worktree, "add", "-N", "--", *changed)
            patch = _git(worktree, "diff", "--binary", "--")
            output_path.parent.mkdir(parents=True, exist_ok=True)
            patch_path = output_path.with_suffix(".patch")
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


def run(args: argparse.Namespace) -> dict[str, Any]:
    root = Path(args.repo_root).resolve()
    if not root.is_dir():
        raise ValueError("Repository root does not exist.")
    prefixes = validate_allowed_paths(args.allowed_paths)
    if bool(args.report) == bool(args.observation):
        raise ValueError("Provide exactly one of --report or --observation.")
    source = _read_json(Path(args.report).resolve()) if args.report else _read_json(Path(args.observation).resolve())
    observation = observation_from_report(source) if args.report else source
    if not isinstance(observation, dict):
        raise ValueError("Observation must be a JSON object.")
    commands = repair_plan(observation)
    fingerprint_input = {
        "commit": str(observation.get("commit", ""))[:40],
        "workflow": str(observation.get("workflow", ""))[:160],
        "job": str(observation.get("job", ""))[:160],
        "failed_step": str(observation.get("failed_step", ""))[:160],
        "failure_class": str(observation.get("failure_class", "unknown"))[:80],
        "failed_test_ids": observation.get("failed_test_ids", [])[:100],
    }
    fingerprint = hashlib.sha256(
        json.dumps(fingerprint_input, sort_keys=True).encode("utf-8")
    ).hexdigest()[:24]
    trajectory_dir = (root / args.trajectory_dir).resolve()
    if root not in trajectory_dir.parents:
        raise ValueError("Trajectory directory must remain inside the repository.")
    history_path = trajectory_dir / f"{fingerprint}.json"
    history = _read_json(history_path) if history_path.exists() else {
        "schema": "dreamco.repo_repair_trajectory.v1",
        "fingerprint": fingerprint,
        "attempts": [],
    }
    result: dict[str, Any] = {
        "schema": "dreamco.repo_repair_result.v1",
        "repair_mode": "deterministic_allowlist_only",
        "model_calls": 0,
        "api_key_required": False,
        "fingerprint": fingerprint,
        "failure_class": str(observation.get("failure_class", "unknown")),
        "failed_test_count": int(observation.get("failed_test_count", 0) or 0),
        "failed_test_ids": list(observation.get("failed_test_ids", []))[:100],
        "commands": commands,
        "attempts_used": len(history.get("attempts", [])),
        "max_attempts": args.max_attempts,
        "changed_files": [],
        "requires_human_review": True,
    }
    if not result["failed_test_count"] and not args.observation:
        result["status"] = "NO_FAILURES"
    elif not commands:
        result["status"] = "NO_ALLOWLISTED_AUTOMATIC_REPAIR"
    elif not args.apply:
        result["status"] = "DRY_RUN_REPAIR_PLAN"
    elif len(history.get("attempts", [])) >= args.max_attempts:
        result["status"] = "MAX_ATTEMPTS_REACHED"
    else:
        head = _assert_apply_context(root, args.allow_local_apply)
        repair_result = _apply_in_worktree(root, observation, prefixes, root / args.output)
        result.update(repair_result)
        result["source_commit"] = head
        result["attempts_used"] = len(history.get("attempts", [])) + 1
        history.setdefault("attempts", []).append({
            "attempt": result["attempts_used"],
            "source_commit": head,
            "status": result["status"],
            "changed_files": result.get("changed_files", []),
            "recorded_at": datetime.now(timezone.utc).isoformat(),
        })
        trajectory_dir.mkdir(parents=True, exist_ok=True)
        history_path.write_text(json.dumps(history, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    output_path = (root / args.output).resolve()
    if root not in output_path.parents:
        raise ValueError("Output path must remain inside the repository.")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--report", help="pytest-json-report JSON file")
    source.add_argument("--observation", help="trusted failure observation JSON file")
    parser.add_argument("--max-attempts", type=int, default=3)
    parser.add_argument("--allowed-paths", help="comma-separated subset of the generated-artifact allowlist")
    parser.add_argument("--trajectory-dir", default="artifacts/repo-repair/trajectories")
    parser.add_argument("--output", default="artifacts/repo-repair/result.json")
    parser.add_argument("--repo-root", default=str(ROOT))
    parser.add_argument("--apply", action="store_true", help="run only a deterministic allowlisted repair in a detached worktree")
    parser.add_argument("--allow-local-apply", action="store_true", help="explicitly permit local execution on a clean main checkout")
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
