#!/usr/bin/env python3
"""Keyless Stage 06: plan deterministic generated-artifact repairs only."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from tools.buddy_safe_repair import repair_plan
from tools.ci_failure_report import sanitize

MAX_ATTEMPTS = 3
MAX_REPORT_BYTES = 5 * 1024 * 1024
MAX_PATCH_BYTES = 5 * 1024 * 1024
MAX_REPAIR_FILES = 20
MAX_CHANGED_LINES = 1500
BLOCKED_BASENAMES = {".env", ".env.local", ".env.production", "credentials.json", "secrets.json"}
BLOCKED_SUFFIXES = {".pem", ".key", ".p12", ".pfx"}
ALLOWED_COMMAND_PATHS = {
    "tools/build_buddy_dataset_routes.py",
    "tools/build_division_model_fleet.py",
    "tools/build_pages_connection_index.py",
    "tools/generate_bot_manifests.py",
    "tools/refresh_repository_evidence.py",
    "tools/generate_command_center_data.py",
    "tools/build_actions_prospectus.py",
    "tools/build_file_prospectus.py",
}
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
    source = Path(path)
    if source.stat().st_size > MAX_REPORT_BYTES:
        raise ValueError("Input JSON exceeds the 5 MiB safety limit.")
    value = json.loads(source.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("Input JSON must be an object.")
    return value


def observation_from_report(report: dict, commit: str = "") -> dict:
    tests = report.get("tests")
    if not isinstance(tests, list) or len(tests) > 10000:
        raise ValueError("pytest-json-report must contain a bounded tests array.")
    failed = sorted({
        re.sub(r"\[[^\]]{1,200}\]", "[parameterized]", sanitize(str(item.get("nodeid", ""))))[:500]
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
    if (not item.parts or item.is_absolute() or "\\" in path
            or any(part in {"", ".", ".."} for part in item.parts)):
        return False
    if item.name.lower() in BLOCKED_BASENAMES or item.suffix.lower() in BLOCKED_SUFFIXES:
        return False
    return any(item.as_posix().startswith(prefix) for prefix in prefixes)


def safe_generated_path(root: Path, value: str, prefixes: tuple[str, ...], label: str) -> Path:
    item = PurePosixPath(str(value))
    if not path_is_allowed(item.as_posix(), prefixes):
        raise ValueError(f"{label} path must stay inside the fixed generated-artifact allowlist.")
    resolved = (root / Path(*item.parts)).resolve()
    try:
        relative = resolved.relative_to(root.resolve()).as_posix()
    except ValueError:
        raise ValueError(f"{label} path resolves outside the repository.")
    if not path_is_allowed(relative, prefixes):
        raise ValueError(f"{label} path resolves outside the fixed generated-artifact allowlist.")
    return resolved


def git(root: Path, *args: str) -> str:
    proc = subprocess.run(["git", *args], cwd=root, text=True, capture_output=True, timeout=20)
    if proc.returncode:
        raise RuntimeError(sanitize(proc.stderr)[-500:])
    return proc.stdout.strip()


def validate_candidate(changed: list[str], patch: str, prefixes: tuple[str, ...]) -> str | None:
    if len(changed) > MAX_REPAIR_FILES:
        return "BLOCKED_FILE_LIMIT"
    if len(patch.encode("utf-8")) > MAX_PATCH_BYTES:
        return "BLOCKED_PATCH_SIZE"
    if any(not path_is_allowed(path, prefixes) for path in changed):
        return "BLOCKED_UNEXPECTED_PATH"
    if "GIT binary patch" in patch or re.search(r"(?m)^Binary files .+ differ$", patch):
        return "BLOCKED_BINARY_CHANGE"
    if re.search(r"(?m)^(?:old|new) mode [0-7]{6}$", patch) or re.search(
        r"(?m)^new file mode (?!100644$)[0-7]{6}$", patch
    ):
        return "BLOCKED_FILE_MODE_CHANGE"
    changed_lines = 0
    in_hunk = False
    for line in patch.splitlines():
        if line.startswith("diff --git "):
            in_hunk = False
        elif line.startswith("@@"):
            in_hunk = True
        elif in_hunk and line.startswith(("+", "-")):
            changed_lines += 1
    if changed_lines > MAX_CHANGED_LINES:
        return "BLOCKED_CHANGE_LIMIT"
    return None


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
            command_results = []
            for command in repair_plan(obs):
                if len(command) != 2 or command[0] != sys.executable or command[1] not in ALLOWED_COMMAND_PATHS:
                    return {"status": "BLOCKED_UNSAFE_COMMAND", "success": False}
                proc = subprocess.run(
                    [sys.executable, command[1]], cwd=worktree, text=True,
                    capture_output=True, timeout=300, check=False,
                )
                command_results.append({"script": command[1], "returncode": proc.returncode})
                if proc.returncode:
                    return {"status": "REPAIR_COMMAND_FAILED", "success": False, "command_results": command_results}
            status = git(worktree, "status", "--porcelain", "--untracked-files=all")
            status_lines = status.splitlines()
            if not status_lines:
                return {"status": "REPAIR_RAN_NO_CHANGES",
                        "success": True, "changed_files": [], "command_results": command_results}
            changed = []
            for line in status_lines:
                if len(line) < 4 or line[:2] not in {" M", "??"}:
                    return {"status": "BLOCKED_UNSUPPORTED_CHANGE", "success": False}
                changed.append(line[3:])
            changed = sorted(set(changed))
            if len(changed) > MAX_REPAIR_FILES:
                return {"status": "BLOCKED_FILE_LIMIT", "success": False}
            blocked_paths = [
                path for path in changed
                if (not path_is_allowed(path, prefixes)
                    or (worktree / path).is_symlink()
                    or not (worktree / path).is_file())
            ]
            if blocked_paths:
                return {"status": "BLOCKED_UNEXPECTED_PATH", "success": False, "blocked_paths": blocked_paths}
            total_bytes = sum((worktree / path).stat().st_size for path in changed)
            if total_bytes > MAX_PATCH_BYTES:
                return {"status": "BLOCKED_PATCH_SIZE", "success": False, "changed_bytes": total_bytes}
            git(worktree, "add", "-N", "--", *changed)
            patch = git(worktree, "diff", "--binary", "--")
            blocked_status = validate_candidate(changed, patch, prefixes)
            if blocked_status:
                return {"status": blocked_status, "success": False}
            output.parent.mkdir(parents=True, exist_ok=True)
            patch_path = output.with_suffix(".patch")
            patch_path.write_text(patch + ("\n" if patch and not patch.endswith("\n") else ""), encoding="utf-8")
            return {
                "status": "REPAIR_CANDIDATE_READY_FOR_REVIEW",
                "success": True,
                "changed_files": changed,
                "patch_file": str(patch_path.relative_to(root)),
                "command_results": command_results,
            }
        finally:
            subprocess.run(
                ["git", "worktree", "remove", "--force", str(worktree)],
                cwd=root, text=True, capture_output=True, timeout=20, check=False,
            )


def run(args: argparse.Namespace) -> dict:
    root = Path(args.repo_root).resolve()
    prefixes = allowed_prefixes(args.allowed_paths)
    output_path = safe_generated_path(root, args.output, prefixes, "Output")
    if bool(args.report) == bool(args.observation):
        raise ValueError("Provide exactly one of --report or --observation.")
    input_path = (root / (args.report or args.observation)).resolve()
    if root not in input_path.parents:
        raise ValueError("Input report or observation must remain inside the repository.")
    source = read_object(input_path)
    obs = observation_from_report(source) if args.report else source
    commands = repair_plan(obs)
    if any(
        len(command) != 2 or command[0] != sys.executable or command[1] not in ALLOWED_COMMAND_PATHS
        for command in commands
    ):
        raise ValueError("Repair plan contains a command outside the fixed command allowlist.")
    fingerprint_data = {
        "commit": str(obs.get("commit", ""))[:40],
        "workflow": str(obs.get("workflow", ""))[:160],
        "job": str(obs.get("job", ""))[:160],
        "failed_step": str(obs.get("failed_step", ""))[:160],
        "failure_class": str(obs.get("failure_class", "unknown"))[:80],
        "failed_test_ids": obs.get("failed_test_ids", [])[:100],
    }
    fingerprint = hashlib.sha256(json.dumps(fingerprint_data, sort_keys=True).encode()).hexdigest()[:24]
    history_dir = safe_generated_path(root, args.trajectory_dir, prefixes, "Trajectory")
    history_path = safe_generated_path(
        root, str(PurePosixPath(args.trajectory_dir) / (fingerprint + ".json")), prefixes, "Trajectory record"
    )
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
        result.update(apply_isolated(root, obs, prefixes, output_path))
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
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
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
