#!/usr/bin/env python3
"""Five-minute rotating DreamCo operations scheduler.

Every tick inventories every tracked Markdown specification, then executes one
bounded workstream selected deterministically from the UTC five-minute slot.
It never trains, spends money, calls external providers, deploys, or promotes.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "artifacts" / "dreamco-rotation"
LANES: list[dict[str, Any]] = [
    {"id": "specifications", "title": "Markdown specifications and master goals", "commands": [
        ["python3", "tools/generate_master_directive_status.py"],
        ["python3", "tools/generate_dreamco_repository_master_map.py"],
    ]},
    {"id": "buddy-core", "title": "Buddy OS and Dream Brain learning architecture", "commands": [
        ["python3", "tools/build_buddy_learning_os_connection_graph.py"],
        ["python3", "tools/generate_buddy_learning_strategies.py"],
    ]},
    {"id": "model-evaluation", "title": "Model catalog, routing and benchmark integrity", "commands": [
        ["python3", "tools/generate_buddy_model_router.py", "--check"],
        ["node", "tools/check_buddy_model_benchmarks.mjs"],
        ["python3", "tools/generate_buddy_benchmark_index.py"],
    ]},
    {"id": "training-governance", "title": "Training queues, dataset governance and distillation readiness", "commands": [
        ["python3", "-m", "py_compile", "tools/build_benchmark_training_queue.py"],
        ["python3", "-m", "py_compile", "tools/execute_benchmark_training_queue.py"],
        ["python3", "-m", "py_compile", "tools/buddy_masterbot_training_lane.py"],
    ]},
    {"id": "user-learning", "title": "User bootcamp, learning paths and model-lab education", "commands": [
        ["python3", "-m", "py_compile", "buddy/bootcamp/professional_training.py"],
        ["python3", "-m", "py_compile", "buddy/builder/self_training.py"],
        ["node", "--check", "website/open-model-lab.js"],
        ["node", "--check", "website/buddy-learning-lab.js"],
    ]},
    {"id": "division-fleet", "title": "Divisions, bot fleet, profiles and capability contracts", "commands": [
        ["python3", "tools/build_bot_profile_pages.py"],
        ["python3", "tools/build_invention_hub.py"],
        ["node", "--test", "tests/invention-hub.test.mjs"],
    ]},
    {"id": "test-registry", "title": "Repository-wide tests, suite registration and regressions", "commands": [
        ["python3", "tools/generate_repository_test_registry.py"],
        ["python3", "-m", "unittest", "tests/test_invention_branding_provenance.py", "tests/test_repository_library.py"],
    ]},
    {"id": "integrations", "title": "Provider adapters, integrations and connection graph", "commands": [
        ["python3", "tools/build_buddy_learning_os_connection_graph.py"],
        ["python3", "tools/generate_resource_connection_catalog.py"],
    ]},
    {"id": "security-governance", "title": "Security, approvals, privacy and release safeguards", "commands": [
        ["python3", "tools/generate_buddy_distribution_catalog.py", "--check"],
        ["python3", "tools/generate_buddy_open_model_lab.py", "--check"],
    ]},
    {"id": "command-center", "title": "Command center, operational telemetry and status surfaces", "commands": [
        ["python3", "tools/generate_command_center_data.py"],
        ["python3", "tools/generate_master_directive_status.py", "--check"],
    ]},
    {"id": "performance-reliability", "title": "Performance, cost, reliability and regression signals", "commands": [
        ["python3", "tools/check_deployment_cost_policy.py"],
        ["node", "--check", "website/buddy.js"],
        ["node", "--check", "website/command-center.js"],
    ]},
    {"id": "release-readiness", "title": "Release readiness, reproducibility and final evidence reconciliation", "commands": [
        ["python3", "tools/generate_repository_test_registry.py", "--check"],
        ["python3", "tools/generate_buddy_benchmark_index.py", "--check"],
        ["node", "--test", "tests/invention-hub.test.mjs"],
    ]},
]


def tracked_markdown() -> list[Path]:
    result = subprocess.run(
        ["git", "ls-files", "-z"], cwd=ROOT, check=True,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    )
    paths = []
    for raw in result.stdout.decode("utf-8", errors="replace").split("\0"):
        if raw and Path(raw).suffix.lower() in {".md", ".mdx"}:
            path = ROOT / raw
            if path.is_file():
                paths.append(path)
    return sorted(paths, key=lambda p: p.relative_to(ROOT).as_posix().lower())


def specification_manifest() -> dict[str, Any]:
    rows = []
    for path in tracked_markdown():
        relative = path.relative_to(ROOT).as_posix()
        data = path.read_bytes()
        rows.append({
            "path": relative,
            "sha256": hashlib.sha256(data).hexdigest(),
            "bytes": len(data),
        })
    return {
        "count": len(rows),
        "files": rows,
        "policy": "Every tracked Markdown/MDX file is inventoried on every tick; inventory does not imply semantic implementation or runtime verification.",
    }


def rotation_index(now: datetime) -> int:
    utc = now.astimezone(timezone.utc)
    five_minute_slot = int(utc.timestamp() // 300)
    return five_minute_slot % len(LANES)


def run_command(command: list[str]) -> dict[str, Any]:
    missing = [part for part in command[1:] if part.endswith((".py", ".mjs", ".js")) and not (ROOT / part).exists()]
    if missing:
        return {"command": command, "status": "blocked_missing_source", "missing": missing}
    try:
        result = subprocess.run(
            command, cwd=ROOT, text=True, stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT, timeout=150, check=False,
            env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
        )
        output = result.stdout[-12000:]
        return {
            "command": command,
            "status": "passed" if result.returncode == 0 else "failed",
            "returncode": result.returncode,
            "output_tail": output,
        }
    except subprocess.TimeoutExpired as exc:
        output = exc.stdout or ""
        if isinstance(output, bytes):
            output = output.decode("utf-8", errors="replace")
        return {"command": command, "status": "timed_out", "output_tail": str(output)[-12000:]}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--at", help="UTC timestamp for deterministic testing (ISO-8601)")
    parser.add_argument("--output", type=Path, default=OUT / "latest.json")
    args = parser.parse_args()
    now = datetime.fromisoformat(args.at.replace("Z", "+00:00")) if args.at else datetime.now(timezone.utc)
    if now.tzinfo is None:
        raise SystemExit("--at must include a timezone")
    index = rotation_index(now)
    lane = LANES[index]
    manifest = specification_manifest()
    results = [run_command(command) for command in lane["commands"]]
    failures = sum(item["status"] != "passed" for item in results)
    report = {
        "schema": "dreamco.rotating_operations.v1",
        "generated_at": now.astimezone(timezone.utc).isoformat(),
        "repository": os.environ.get("GITHUB_REPOSITORY", "DreamCo-Technologies/Dreamcobots"),
        "commit": os.environ.get("GITHUB_SHA", "local"),
        "rotation_slot": int(now.astimezone(timezone.utc).timestamp() // 300),
        "lane_index": index,
        "lane_count": len(LANES),
        "lane": lane,
        "specification_inventory": manifest,
        "commands": results,
        "summary": {
            "commands": len(results),
            "passed": sum(item["status"] == "passed" for item in results),
            "failed_or_blocked": failures,
            "status": "passed" if failures == 0 else "needs_attention",
        },
        "safety": {
            "model_training_executed": False,
            "paid_services_called": False,
            "credentials_read_or_written": False,
            "production_deployment_performed": False,
            "automatic_model_promotion": False,
            "note": "Training execution, paid compute, external provider calls and production promotion require separate approved, evidenced workflows.",
        },
        "lanes": [{"id": item["id"], "title": item["title"]} for item in LANES],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "lane": lane["id"],
        "markdown_specs": manifest["count"],
        "passed": report["summary"]["passed"],
        "failed_or_blocked": failures,
        "report": str(args.output.relative_to(ROOT)) if args.output.is_relative_to(ROOT) else str(args.output),
    }, indent=2))
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
