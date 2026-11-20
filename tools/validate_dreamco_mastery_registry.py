#!/usr/bin/env python3
"""Validate the DreamCo mastery registry and emit a deterministic daily queue."""
from __future__ import annotations

import json
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "config/dreamco-mastery-continuity-registry.json"
REPORT_JSON = ROOT / "reports/DREAMCO_MASTERY_DAILY_QUEUE.json"
REPORT_MD = ROOT / "reports/DREAMCO_MASTERY_DAILY_QUEUE.md"
STAGES = [
    "catalogued", "specified", "implemented", "sandbox_verified",
    "benchmark_verified", "regression_verified", "production_verified", "mastered",
]
REQUIRED = {"id", "name", "scope", "priority", "status", "acceptance", "continuous"}


def main() -> int:
    data = json.loads(REGISTRY.read_text(encoding="utf-8"))
    errors: list[str] = []
    goals = data.get("workstreams")
    if not isinstance(goals, list) or not goals:
        errors.append("workstreams must be a non-empty list")
        goals = []
    seen: set[str] = set()
    for index, goal in enumerate(goals):
        missing = REQUIRED - set(goal)
        if missing:
            errors.append(f"workstreams[{index}] missing fields: {sorted(missing)}")
        goal_id = goal.get("id")
        if not isinstance(goal_id, str) or not goal_id.strip():
            errors.append(f"workstreams[{index}] has invalid id")
        elif goal_id in seen:
            errors.append(f"duplicate goal id: {goal_id}")
        else:
            seen.add(goal_id)
        if goal.get("status") not in STAGES:
            errors.append(f"{goal_id}: invalid lifecycle status {goal.get('status')!r}")
        if not isinstance(goal.get("acceptance"), list) or not goal.get("acceptance"):
            errors.append(f"{goal_id}: acceptance criteria must be non-empty")
        if goal.get("continuous") is not True:
            errors.append(f"{goal_id}: continuous must be true")
    lifecycle = data.get("mastery_lifecycle")
    if lifecycle != STAGES:
        errors.append("mastery_lifecycle does not match the required ordered stages")
    if data.get("defaults", {}).get("production_safety_hold") is not True:
        errors.append("production safety hold must remain enabled")
    for forbidden in ("auto_merge", "auto_deploy", "auto_spend", "auto_change_credentials", "bypass_protections"):
        if data.get("defaults", {}).get(forbidden) is not False:
            errors.append(f"{forbidden} must remain false")

    counts = {stage: 0 for stage in STAGES}
    for goal in goals:
        if goal.get("status") in counts:
            counts[goal["status"]] += 1
    queue = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "registry_id": data.get("registry_id"),
        "goal_count": len(goals),
        "continuous_goal_count": sum(1 for g in goals if g.get("continuous") is True),
        "lifecycle_counts": counts,
        "historical_reconciliation_status": data.get("historical_reconciliation", {}).get("status", "unknown"),
        "validation": {"passed": not errors, "errors": errors},
        "next_actions": [
            "Complete historical conversation, branch, PR, issue, workflow, and documentation reconciliation.",
            "Attach implementation, test, runtime-route, benchmark, and regression evidence to each canonical goal.",
            "Prioritize security and production-isolation blockers before expansion.",
            "Keep blocked work visible; do not promote status without its required evidence.",
        ],
        "workstreams": goals,
    }
    REPORT_JSON.parent.mkdir(parents=True, exist_ok=True)
    REPORT_JSON.write_text(json.dumps(queue, indent=2) + "\n", encoding="utf-8")
    lines = [
        "# DreamCo Daily Mastery Queue", "",
        f"- Generated: {queue['generated_at']}",
        f"- Workstreams: {queue['goal_count']}",
        f"- Continuous: {queue['continuous_goal_count']}",
        f"- Historical reconciliation: {queue['historical_reconciliation_status']}",
        f"- Registry validation: {'PASS' if not errors else 'FAIL'}", "",
        "## Lifecycle counts", "",
    ]
    lines.extend(f"- {stage}: {counts[stage]}" for stage in STAGES)
    lines += ["", "## Next actions", ""]
    lines.extend(f"{i}. {action}" for i, action in enumerate(queue["next_actions"], 1))
    lines += ["", "## Workstreams", ""]
    lines.extend(f"- **{g.get('id')} — {g.get('name')}** [{g.get('status')}] — {g.get('scope')}" for g in goals)
    if errors:
        lines += ["", "## Validation errors", ""]
        lines.extend(f"- {error}" for error in errors)
    REPORT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"validated={not errors} goals={len(goals)}")
    for error in errors:
        print(f"ERROR: {error}")
    print(f"report={REPORT_MD.relative_to(ROOT)}")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
