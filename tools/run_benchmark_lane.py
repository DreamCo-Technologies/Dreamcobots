#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import shlex
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "config" / "generated" / "parallel-benchmark-gap-plan.json"
PACKAGE = json.loads((ROOT / "package.json").read_text(encoding="utf-8"))
PACKAGE_SCRIPTS = set(PACKAGE.get("scripts", {}))


def command_for_test(path: str) -> list[str]:
    if path.startswith("tools/") and path.endswith(".py"):
        return ["python3", path]
    if path.endswith((".ts", ".tsx")):
        return ["node", "--import", "tsx", "--test", path]
    if path.endswith((".mjs", ".js")):
        return ["node", "--test", path]
    if path.endswith(".py"):
        module = path[:-3].replace("/", ".")
        return ["python3", "-m", "unittest", module]
    raise ValueError(f"Unsupported lane test path: {path}")


def load_lane(lane_id: str) -> dict:
    plan = json.loads(PLAN.read_text(encoding="utf-8"))
    for lane in plan.get("lanes", []):
        if lane.get("lane") == lane_id:
            return lane
    raise SystemExit(f"Unknown benchmark lane: {lane_id}")


def build_commands(lane: dict) -> list[list[str]]:
    commands: list[list[str]] = []
    seen: set[tuple[str, ...]] = set()

    explicit_tests: list[str] = []
    scripts: list[str] = []
    for suite in lane.get("suites", []):
        explicit_tests.extend(suite.get("tests", []))
        scripts.extend(suite.get("scripts", []))

    # Explicit tests are more targeted than broad umbrella scripts such as test:governed.
    for test_path in explicit_tests:
        path = ROOT / test_path
        if not path.exists():
            raise SystemExit(f"Lane references missing test: {test_path}")
        cmd = command_for_test(test_path)
        key = tuple(cmd)
        if key not in seen:
            seen.add(key)
            commands.append(cmd)

    # Run build/check/generator scripts only when they add evidence not represented by explicit tests.
    broad_umbrella = {"test:governed", "test:repository"}
    for script in scripts:
        if script in broad_umbrella:
            continue
        if script not in PACKAGE_SCRIPTS:
            raise SystemExit(f"Lane references missing npm script: {script}")
        cmd = ["npm", "run", script]
        key = tuple(cmd)
        if key not in seen:
            seen.add(key)
            commands.append(cmd)

    if not commands:
        commands.append(["npm", "run", "check"])
    return commands


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--lane", default=os.getenv("BENCHMARK_BUILDER_LANE"))
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    if not args.lane:
        raise SystemExit("--lane or BENCHMARK_BUILDER_LANE is required")

    lane = load_lane(args.lane)
    commands = build_commands(lane)
    print(json.dumps({
        "schema": "dreamco.benchmark_lane_execution.v1",
        "lane": args.lane,
        "suite_count": len(lane.get("suites", [])),
        "command_count": len(commands),
        "commands": [shlex.join(command) for command in commands],
        "cost_policy": "targeted_explicit_tests_before_broad_umbrella_suites",
    }, indent=2))
    if args.dry_run:
        return 0

    for command in commands:
        completed = subprocess.run(command, cwd=ROOT, check=False)
        if completed.returncode:
            return completed.returncode
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
