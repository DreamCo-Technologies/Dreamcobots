#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shlex
import subprocess
import sys
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass
class StepResult:
    name: str
    command: str
    return_code: int
    stdout: str
    stderr: str


def _run(command: str) -> StepResult:
    completed = subprocess.run(
        shlex.split(command),
        capture_output=True,
        text=True,
        check=False,
    )
    return StepResult(
        name=command,
        command=command,
        return_code=completed.returncode,
        stdout=completed.stdout,
        stderr=completed.stderr,
    )


def _fix_plan(detect_output: str) -> list[str]:
    plan: list[str] = []
    lowered = detect_output.lower()
    if "duplicate bot id" in lowered or "duplicate slug" in lowered:
        plan.append("Deduplicate bot IDs/slugs in master registry.")
    if "missing capabilities" in lowered or "empty capability list" in lowered:
        plan.append("Add or restore bot capability manifests.")
    if "unregistered capability" in lowered:
        plan.append("Register missing capabilities in bot library.")
    if not plan:
        plan.append("Investigate failing checks and generate targeted patch.")
    return plan


def main() -> int:
    parser = argparse.ArgumentParser(description="Run DreamCo autonomous self-repair workflow.")
    parser.add_argument(
        "--detect-cmd",
        default="python3 tools/validate_bot_registry.py",
        help="Issue detection command.",
    )
    parser.add_argument("--fix-cmd", default="", help="Optional fix command.")
    parser.add_argument(
        "--test-cmd",
        default="npm run test -- --passWithNoTests",
        help="Validation test command after fix.",
    )
    parser.add_argument(
        "--owner",
        default="repository-owner",
        help="Owner who must approve generated pull request.",
    )
    parser.add_argument("--dry-run", action="store_true", help="Simulate fixes only.")
    parser.add_argument("--output", type=Path, default=None, help="Optional output JSON path.")
    args = parser.parse_args()

    detect = _run(args.detect_cmd)
    issues_detected = detect.return_code != 0
    fix_steps = _fix_plan(f"{detect.stdout}\n{detect.stderr}") if issues_detected else []

    fix_result = None
    if issues_detected and args.fix_cmd:
        if args.dry_run:
            fix_result = StepResult("fix", args.fix_cmd, 0, "dry-run: fix skipped", "")
        else:
            fix_result = _run(args.fix_cmd)

    tests_result = None
    if issues_detected and args.fix_cmd and (not fix_result or fix_result.return_code == 0):
        if args.dry_run:
            tests_result = StepResult("tests", args.test_cmd, 0, "dry-run: tests skipped", "")
        else:
            tests_result = _run(args.test_cmd)

    pr_ready = bool(
        issues_detected
        and args.fix_cmd
        and fix_result
        and fix_result.return_code == 0
        and tests_result
        and tests_result.return_code == 0
    )
    payload = {
        "schema": "dreamco.self_repair.v1",
        "workflow": [
            "detect_issue",
            "generate_fix",
            "run_tests",
            "open_pull_request",
            "owner_approval",
        ],
        "issues_detected": issues_detected,
        "fix_plan": fix_steps,
        "detection": asdict(detect),
        "fix": asdict(fix_result) if fix_result else None,
        "tests": asdict(tests_result) if tests_result else None,
        "pr_recommendation": (
            "Open pull request with generated fix and request owner approval."
            if pr_ready
            else "Do not open pull request until fix and tests succeed."
        ),
        "owner_approval_required": args.owner,
    }

    print(json.dumps(payload, indent=2))
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    if not issues_detected:
        return 0
    return 0 if pr_ready else 1


if __name__ == "__main__":
    sys.exit(main())
