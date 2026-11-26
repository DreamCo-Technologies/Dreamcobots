#!/usr/bin/env python3
"""Build separate, evidence-backed queues for 65 MasterBots and 55 domain divisions."""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def _action_for(result: dict) -> dict:
    score = result.get("score")
    target = result.get("target")
    if score is None or target is None:
        return {"priority": 0, "action": "RUN_BENCHMARKS", "reason": "incomplete measurement"}
    score = float(score)
    target = float(target)
    if score < target:
        gap = target - score
        priority = 1 if result.get("status") == "failed" else 2
        return {"priority": priority, "action": "CLOSE_GAPS", "reason": f"gap={gap:g}"}
    action = "RETEST_FAILURES" if result.get("status") == "regression" else "RUN_SANDBOX"
    return {"priority": 3, "action": action, "reason": "at/above target; verify repeatability"}


def build_gap_queue(scores: dict, registry: dict, crosswalk: dict) -> dict:
    masterbots = registry.get("divisions", [])
    domains = crosswalk.get("domains", [])
    if len(masterbots) != 65:
        raise ValueError("canonical MasterBot registry must contain exactly 65 entries")
    if len(domains) != 55:
        raise ValueError("canonical domain crosswalk must contain exactly 55 entries")
    masterbot_by_id = {int(row["id"]): row for row in masterbots}
    domain_by_id = {row["domain_id"]: row for row in domains}
    if len(masterbot_by_id) != 65 or len(domain_by_id) != 55:
        raise ValueError("canonical MasterBot or domain identifiers are duplicated")

    by_masterbot: dict[int, list[dict]] = {}
    by_domain: dict[str, list[dict]] = {}
    for result in scores.get("results", []):
        scope = result.get("scope")
        if scope == "domain_division":
            domain_id = result.get("domain_id")
            if domain_id not in domain_by_id:
                raise ValueError(f"unknown domain_id in benchmark evidence: {domain_id}")
            if result.get("masterbot_id") is not None:
                raise ValueError("domain benchmark evidence cannot assign MasterBot ownership or mastery")
            by_domain.setdefault(domain_id, []).append(result)
        elif scope == "masterbot":
            masterbot_id = result.get("masterbot_id")
            if masterbot_id is None or int(masterbot_id) not in masterbot_by_id:
                raise ValueError(f"unknown or missing MasterBot ID in benchmark evidence: {masterbot_id}")
            by_masterbot.setdefault(int(masterbot_id), []).append(result)
        else:
            raise ValueError(f"unsupported benchmark evidence scope: {scope}")

    queue = []
    for masterbot_id, masterbot in sorted(masterbot_by_id.items()):
        rows = by_masterbot.get(masterbot_id, [])
        if not rows:
            queue.append({
                "scope": "masterbot",
                "masterbot_id": masterbot_id,
                "domain_id": None,
                "division": masterbot["name"],
                "benchmark": None,
                "score": None,
                "target": None,
                "evidence_count": 0,
                "priority": 0,
                "action": "RUN_BENCHMARKS",
                "reason": "no MasterBot-scoped benchmark evidence; domain evidence is not transferable",
            })
        else:
            for row in rows:
                queue.append({
                    "scope": "masterbot",
                    "masterbot_id": masterbot_id,
                    "domain_id": None,
                    "division": masterbot["name"],
                    "benchmark": row.get("benchmark"),
                    "score": row.get("score"),
                    "target": row.get("target"),
                    "evidence_count": row.get("evidence_count", 0),
                    **_action_for(row),
                })

    for domain_id, domain in sorted(domain_by_id.items()):
        rows = by_domain.get(domain_id, [])
        if not rows:
            queue.append({
                "scope": "domain_division",
                "masterbot_id": None,
                "domain_id": domain_id,
                "division": domain["domain_name"],
                "benchmark": None,
                "score": None,
                "target": None,
                "evidence_count": 0,
                "priority": 0,
                "action": "RUN_BENCHMARKS",
                "reason": "no measured domain-division evidence",
            })
        else:
            for row in rows:
                queue.append({
                    "scope": "domain_division",
                    "masterbot_id": None,
                    "domain_id": domain_id,
                    "division": domain["domain_name"],
                    "benchmark": row.get("benchmark"),
                    "score": row.get("score"),
                    "target": row.get("target"),
                    "evidence_count": row.get("evidence_count", 0),
                    **_action_for(row),
                })

    queue.sort(key=lambda row: (
        row["priority"],
        row["scope"],
        row["masterbot_id"] or 0,
        row["domain_id"] or "",
        row.get("benchmark") or "",
    ))
    return {
        "schema": "dreamco.benchmark_gap_queue.v2",
        "masterbot_count": 65,
        "domain_division_count": 55,
        "queue": queue,
        "summary": {
            "masterbots_measured": len(by_masterbot),
            "masterbots_unmeasured": 65 - len(by_masterbot),
            "domain_divisions_measured": len(by_domain),
            "domain_divisions_unmeasured": 55 - len(by_domain),
            "queue_items": len(queue),
        },
        "measurement_policy": "unknown is not failure; domain evidence is not MasterBot mastery",
        "mastery_policy": "repeatable scope-specific evidence and owner approval required",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--scores", default="benchmark-scores.json")
    parser.add_argument("--out", default="benchmark-gap-queue.json")
    parser.add_argument("--registry", default="config/masterbot-65-registry.json")
    parser.add_argument("--crosswalk", default="config/generated/masterbot-55-domain-crosswalk.json")
    args = parser.parse_args()
    scores = json.loads(Path(args.scores).read_text(encoding="utf-8"))
    registry = json.loads(Path(args.registry).read_text(encoding="utf-8"))
    crosswalk = json.loads(Path(args.crosswalk).read_text(encoding="utf-8"))
    result = build_gap_queue(scores, registry, crosswalk)
    Path(args.out).write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result["summary"], indent=2))


if __name__ == "__main__":
    main()
