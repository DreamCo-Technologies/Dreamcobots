#!/usr/bin/env python3
"""Build an evidence-preserving 65-division benchmark work queue.

Invalid or untrusted measurements are never treated as passing. This planner
is not a benchmark executor or a mastery certifier.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path


def finite_score(value):
    return type(value) in (int, float) and math.isfinite(value)


def build_queue(data, registry):
    if not isinstance(data, dict):
        raise ValueError("scorecard must be an object")
    results = data.get("results", data.get("divisionResults", []))
    if not isinstance(results, list):
        raise ValueError("results must be a list")
    if not isinstance(registry, dict) or not isinstance(registry.get("divisions"), list):
        raise ValueError("canonical division registry is malformed")
    names = {}
    ids = set()
    for entry in registry["divisions"]:
        if (not isinstance(entry, dict) or not isinstance(entry.get("name"), str)
                or type(entry.get("id")) is not int or entry["id"] in ids
                or entry["name"] in names):
            raise ValueError("canonical division registry contains invalid or duplicate identities")
        names[entry["name"]] = entry["id"]
        ids.add(entry["id"])
    if ids != set(range(1, 66)):
        raise ValueError("canonical division registry must contain exactly IDs 1..65")

    by = {}
    rejected = []
    seen = set()
    for index, record in enumerate(results):
        if not isinstance(record, dict):
            rejected.append({"index": index, "reason": "measurement must be an object"})
            continue
        value = record.get("division_id", record.get("division"))
        division = names.get(value) if isinstance(value, str) else value
        if isinstance(division, str) and division.isdigit():
            division = int(division)
        if type(division) is not int or division not in ids:
            rejected.append({"index": index, "division": value, "reason": "unknown division identity"})
            continue
        benchmark = record.get("benchmark", "buddy-division-contract")
        if not isinstance(benchmark, str) or not benchmark.strip():
            rejected.append({"index": index, "division": value, "reason": "invalid benchmark identity"})
            continue
        identity = (division, benchmark)
        if identity in seen:
            rejected.append({"index": index, "division": value, "benchmark": benchmark, "reason": "duplicate measurement identity"})
            continue
        score, target = record.get("score"), record.get("target")
        if score is not None and not finite_score(score):
            rejected.append({"index": index, "division": value, "benchmark": benchmark, "reason": "non-finite or nonnumeric score"})
            continue
        if target is not None and not finite_score(target):
            rejected.append({"index": index, "division": value, "benchmark": benchmark, "reason": "non-finite or nonnumeric target"})
            continue
        seen.add(identity)
        by.setdefault(division, []).append(record)

    queue = []
    for division in range(1, 66):
        records = by.get(division, [])
        if not records:
            queue.append({"division": division, "priority": 0, "action": "RUN_BENCHMARKS", "reason": "no valid measured evidence"})
            continue
        for record in records:
            score, target = record.get("score"), record.get("target")
            if score is None or target is None:
                priority, action, reason = 0, "RUN_BENCHMARKS", "incomplete measurement"
            elif score < target:
                gap = target - score
                priority = 1 if record.get("status") == "failed" else 2
                action, reason = "CLOSE_GAPS", f"gap={gap:g}"
            else:
                if record.get("status") in ("failed", "regression"):
                    priority, action = 1, "RETEST_FAILURES"
                    reason = "failed or regressed despite score at/above target"
                else:
                    priority, action = 3, "RUN_SANDBOX"
                    reason = "at/above target; verify repeatability"
            queue.append({"division": division, "benchmark": record.get("benchmark"), "priority": priority, "action": action, "reason": reason})
    queue.sort(key=lambda item: (item["priority"], item["division"], item.get("benchmark") or ""))
    # A successfully constructed queue is not complete measurement coverage.
    # A single valid division score must not hide 64 unmeasured divisions, and
    # an incomplete score/target pair must not be counted as measured.
    unmeasured = sorted({item["division"] for item in queue if item["action"] == "RUN_BENCHMARKS"})
    return {"rejected": rejected, "complete": not rejected and not unmeasured,
            "schema": "dreamco.benchmark_gap_queue.v1", "divisions": 65,
            "measured_divisions": 65 - len(unmeasured), "unmeasured_division_ids": unmeasured,
            "coverage_scope": "division_measurement_presence_only; not suite coverage or mastery",
            "queue": queue, "measurement_policy": "unknown is not failure", "mastery_policy": "repeatable evidence required"}


def load_queue_from_scores(source: Path, registry: dict) -> dict:
    """Preserve an honest incomplete state when no measured scorecard exists.

    This is a planning queue, not passing benchmark or mastery evidence.
    """
    if not source.is_file():
        result = build_queue({"results": []}, registry)
        result["complete"] = False
        result["score_source_status"] = "missing"
        return result
    data = json.loads(source.read_text())
    result = build_queue(data, registry)
    measurements = data.get("results", data.get("divisionResults", []))
    if not measurements:
        result["complete"] = False
        result["score_source_status"] = "empty"
    else:
        result["score_source_status"] = "present"
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--scores", default="benchmark-scores.json")
    parser.add_argument("--out", default="benchmark-gap-queue.json")
    args = parser.parse_args()
    source = Path(args.scores)
    registry = json.loads((Path(__file__).resolve().parents[1] / "config/masterbot-65-registry.json").read_text())
    result = load_queue_from_scores(source, registry)
    Path(args.out).write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"divisions": 65, "queue_items": len(result["queue"]),
                      "unmeasured_divisions": sum(row["action"] == "RUN_BENCHMARKS" for row in result["queue"]),
                      "rejected": len(result["rejected"]),
                      "score_source_status": result["score_source_status"],
                      "complete": result["complete"]}, indent=2))
    return 2 if result["rejected"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
