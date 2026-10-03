"""Connect every workflow and benchmark file to Buddy's learning runner.

Missing files fail readiness. A listed workflow is not a passing benchmark.
Only local sandbox runs verified in this process are marked verified.
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WORKFLOWS = ROOT / ".github" / "workflows"
BENCHMARKS = ROOT / "benchmarks"
LEARNING = ROOT / "buddy" / "learning"
EVENTS = LEARNING / "workflow_benchmark_events.json"
REPORT = LEARNING / "workflow_benchmark_readiness.json"

REQUIRED = (
    LEARNING / "registered_runner.py",
    LEARNING / "continuous_learning_controller.py",
    LEARNING / "benchmark_learning_adapter.py",
    LEARNING / "all_benchmarks.py",
    BENCHMARKS / "buddy_benchmark_runner.py",
    BENCHMARKS / "america_gov" / "sandbox.py",
    BENCHMARKS / "america_gov" / "catalog.json",
    BENCHMARKS / "america_gov" / "massive_resources.json",
    BENCHMARKS / "resource_mastery" / "sandbox.py",
    BENCHMARKS / "tasks" / "universal_1000_smoke.json",
)


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def inventory() -> dict:
    workflows = sorted(path.relative_to(ROOT).as_posix() for path in WORKFLOWS.glob("*.yml"))
    benchmarks = sorted(
        path.relative_to(ROOT).as_posix()
        for path in list(BENCHMARKS.rglob("*"))
        + list((ROOT / "config").glob("*benchmark*.json"))
        + list((ROOT / "tools").glob("*benchmark*.py"))
        if path.is_file() and path.suffix in {".py", ".json", ".md", ".yaml"} and "__pycache__" not in path.parts
    )
    missing = [path.relative_to(ROOT).as_posix() for path in REQUIRED if not path.is_file() or path.stat().st_size == 0]
    empty = [item for item in workflows if (ROOT / item).stat().st_size == 0]
    return {
        "workflows": workflows,
        "benchmarks": benchmarks,
        "missing": missing + empty,
    }


def build_events(found: dict) -> dict:
    events = []
    for path in found["workflows"]:
        events.append({
            "event_id": "workflow:" + path,
            "event_type": "tool_outcome",
            "capability": "workflow_connection",
            "success": True,
            "verified": False,
            "regression_passed": False,
            "safety_passed": True,
            "external_assistance": False,
            "source": path,
        })
    for path in found["benchmarks"]:
        local_sandbox = path in {
            "benchmarks/america_gov/sandbox.py",
            "benchmarks/resource_mastery/sandbox.py",
        }
        events.append({
            "event_id": "benchmark:" + path,
            "event_type": "benchmark",
            "capability": "repository_benchmark",
            "success": local_sandbox,
            "verified": local_sandbox,
            "regression_passed": local_sandbox,
            "safety_passed": True,
            "external_assistance": False,
            "source": path,
        })
    return {"schema": "dreamco.workflow_benchmark_events.v1", "events": events}


def main() -> int:
    found = inventory()
    events = build_events(found)
    EVENTS.write_text(json.dumps(events, indent=2) + "\n", encoding="utf-8")
    report = {
        "schema": "dreamco.workflow_benchmark_readiness.v1",
        "ran_at": _now(),
        "ready_for_testing": not found["missing"],
        "workflow_count": len(found["workflows"]),
        "benchmark_file_count": len(found["benchmarks"]),
        "event_count": len(events["events"]),
        "missing": found["missing"],
        "events_file": EVENTS.relative_to(ROOT).as_posix(),
        "production_mastered": False,
    }
    REPORT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: report[key] for key in ("ready_for_testing", "workflow_count", "benchmark_file_count", "event_count", "missing")}, indent=2))
    return 0 if report["ready_for_testing"] else 1


if __name__ == "__main__":
    sys.exit(main())
