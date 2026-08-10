#!/usr/bin/env python3
from __future__ import annotations

import json
import math
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POLICY = json.loads((ROOT / "config/benchmark-gap-acceleration-policy.json").read_text(encoding="utf-8"))
GEN = ROOT / "config/generated"
OUT = GEN / "benchmark-gap-velocity.json"
REPORT = ROOT / "reports/BENCHMARK_GAP_VELOCITY.md"

OPEN_STATES = {"unknown", "unmeasured", "needs_runtime_baseline", "sandbox_backlog", "planned_not_run", "measured_gap", "assigned", "in_progress", "fix_ready", "retest_required", "blocked", "regressed"}
CLOSED_STATES = {"passed", "complete", "verified", "exception_approved", "repository_evidence_present"}


def parse_time(value):
    if not value or not isinstance(value, str):
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)
    except Exception:
        return None


def age_hours(row, now):
    for key in ("updated_at", "last_measured_at", "last_progress_at", "measured_at", "generated_at"):
        dt = parse_time(row.get(key))
        if dt:
            return max(0.0, (now - dt).total_seconds() / 3600)
    return None


def normalize_status(row):
    value = str(row.get("status") or row.get("gap_state") or row.get("state") or "unknown").lower().strip()
    aliases = {
        "not_run": "unmeasured", "not measured": "unmeasured", "planned": "planned_not_run", "sandbox_only": "sandbox_backlog",
        "failed": "measured_gap", "behind": "measured_gap", "missing": "measured_gap", "partial": "measured_gap",
        "ok": "passed", "pass": "passed", "closed": "passed", "done": "passed"
    }
    return aliases.get(value, value)


def row_id(row, source, index):
    for key in ("gap_id", "gap_worker_id", "worker_id", "case_id", "benchmark_id", "id", "slug"):
        if row.get(key):
            return str(row[key])
    return f"{Path(source).stem}:{index}"


def discover_rows():
    rows = []
    sources = []
    if not GEN.exists():
        return rows, sources
    for path in sorted(GEN.glob("*.json")):
        lower = path.name.lower()
        if not any(token in lower for token in ("benchmark", "gap", "sandbox", "parity", "readiness", "certification")):
            continue
        if path.name == OUT.name:
            continue
        try:
            doc = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        source = str(path.relative_to(ROOT))
        sources.append(source)
        arrays = []
        for key in ("entries", "gaps", "workers", "cases", "benchmarks", "capabilities", "tasks", "gauges"):
            value = doc.get(key) if isinstance(doc, dict) else None
            if isinstance(value, list):
                arrays.extend((key, item) for item in value if isinstance(item, dict))
        for index, (array_name, row) in enumerate(arrays):
            status = normalize_status(row)
            if status not in OPEN_STATES and status not in CLOSED_STATES:
                status = "unknown"
            rows.append({
                "gap_id": row_id(row, source, index),
                "source": source,
                "source_array": array_name,
                "status": status,
                "risk": row.get("risk") or row.get("severity") or "unknown",
                "owner": row.get("owner_bot") or row.get("primary_owner") or row.get("builder_lane") or row.get("owner") or None,
                "age_hours": None,
                "blocked_reason": row.get("blocked_reason") or row.get("blocker") or None,
            })
    # De-duplicate exact source/gap pairs while preserving cross-source evidence.
    unique = {}
    for row in rows:
        unique[(row["source"], row["gap_id"])] = row
    return list(unique.values()), sorted(set(sources))


def stagnant_reason(status, age):
    cfg = POLICY["stagnation_policy"]
    if age is None:
        if status in OPEN_STATES:
            return "missing_progress_timestamp"
        return None
    thresholds = {
        "unknown": cfg["unmeasured_warning_hours"],
        "unmeasured": cfg["unmeasured_warning_hours"],
        "planned_not_run": cfg["unmeasured_warning_hours"],
        "needs_runtime_baseline": cfg["unmeasured_warning_hours"],
        "sandbox_backlog": cfg["unassigned_warning_hours"],
        "measured_gap": cfg["unassigned_warning_hours"],
        "assigned": cfg["assigned_no_progress_warning_hours"],
        "in_progress": cfg["in_progress_no_evidence_warning_hours"],
        "fix_ready": cfg["retest_required_warning_hours"],
        "retest_required": cfg["retest_required_warning_hours"],
        "blocked": cfg["blocked_recheck_hours"],
        "regressed": 1,
    }
    threshold = thresholds.get(status)
    return f"{status}_older_than_{threshold}h" if threshold is not None and age > threshold else None


def estimate(open_rows, blocked_count, owner_counts):
    effective = max(1, min(int(POLICY["parallelism"]["maximum_parallel_lanes"]), max(1, len(open_rows) - blocked_count)))
    actionable = max(0, len(open_rows) - blocked_count)
    waves = math.ceil(actionable / effective) if actionable else 0
    model = POLICY["estimate_model"]
    conflict_ratio = (max(owner_counts.values()) / actionable) if owner_counts and actionable else 0
    conflict_multiplier = model["shared_owner_conflict_multiplier"] if conflict_ratio > 0.20 else 1.0
    integration_multiplier = model["integration_multiplier"]
    hours = {}
    for name, base in model["default_wave_hours"].items():
        hours[name] = round(waves * float(base) * integration_multiplier * conflict_multiplier, 1)
    return {
        "actionable_open_gaps": actionable,
        "blocked_open_gaps": blocked_count,
        "effective_parallel_lanes": effective,
        "estimated_parallel_waves": waves,
        "planning_hours": hours,
        "estimate_is_calendar_promise": False,
        "blocked_completion_date_known": blocked_count == 0,
        "note": "External credentials, vendor approvals, human review, shared-owner conflicts and newly discovered/regressed gaps can extend calendar time. Moving-target benchmarks continue after current gaps reach zero."
    }


def main() -> int:
    now = datetime.now(timezone.utc)
    rows, sources = discover_rows()
    # Existing generated artifacts often omit timestamps on individual rows. Use source mtime as a conservative evidence timestamp.
    for row in rows:
        path = ROOT / row["source"]
        if path.exists():
            dt = datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc)
            row["age_hours"] = round(max(0.0, (now - dt).total_seconds() / 3600), 2)
        row["stagnant_reason"] = stagnant_reason(row["status"], row["age_hours"])
        if row["status"] in OPEN_STATES:
            row["required_action"] = POLICY["anti_stagnation_actions"].get(row["status"], "measure, assign, repair and retest")
    open_rows = [r for r in rows if r["status"] in OPEN_STATES]
    stagnant = [r for r in open_rows if r["stagnant_reason"]]
    blocked = [r for r in open_rows if r["status"] == "blocked"]
    owner_counts = Counter(r["owner"] for r in open_rows if r.get("owner"))
    status_counts = Counter(r["status"] for r in rows)
    payload = {
        "schema": "dreamco.benchmark_gap_velocity.v1",
        "generated_at": now.isoformat(),
        "source_count": len(sources),
        "record_count": len(rows),
        "open_gap_count": len(open_rows),
        "stagnant_gap_count": len(stagnant),
        "blocked_gap_count": len(blocked),
        "status_counts": dict(sorted(status_counts.items())),
        "owner_load": dict(owner_counts.most_common()),
        "parallel_policy": POLICY["parallelism"],
        "closure_estimate": estimate(open_rows, len(blocked), owner_counts),
        "stagnant_gaps": stagnant,
        "open_gaps": open_rows,
        "truth_boundary": POLICY["truth_rule"]
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    est = payload["closure_estimate"]
    lines = [
        "# Benchmark Gap Velocity", "",
        f"- Evidence sources: **{len(sources)}**",
        f"- Open gaps: **{len(open_rows)}**",
        f"- Stagnant gaps: **{len(stagnant)}**",
        f"- Blocked gaps: **{len(blocked)}**",
        f"- Effective parallel lanes: **{est['effective_parallel_lanes']}**",
        f"- Estimated parallel waves: **{est['estimated_parallel_waves']}**",
        f"- Planning hours (optimistic / expected / conservative): **{est['planning_hours']['optimistic']} / {est['planning_hours']['expected']} / {est['planning_hours']['conservative']}**",
        "", "> This is a planning estimate from current evidence, not a delivery promise. Blocked/external gaps do not receive invented completion dates.", ""
    ]
    if stagnant:
        lines += ["## Stagnant gaps", ""]
        for row in stagnant[:500]:
            lines.append(f"- `{row['gap_id']}` — {row['status']} — {row['stagnant_reason']} — action: {row['required_action']}")
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({"ok": len(stagnant) == 0, "open": len(open_rows), "stagnant": len(stagnant), "blocked": len(blocked), "estimate": est, "output": str(OUT.relative_to(ROOT))}, indent=2))
    # Nonzero makes CI surface stagnation; it does not hide or auto-close gaps.
    return 1 if stagnant else 0


if __name__ == "__main__":
    raise SystemExit(main())
