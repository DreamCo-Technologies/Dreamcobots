#!/usr/bin/env python3
"""Convert domain-division benchmark evidence without inventing MasterBot ownership."""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def convert(source: dict, crosswalk: dict) -> dict:
    domains = crosswalk.get("domains", [])
    by_name = {row.get("domain_name"): row for row in domains if row.get("domain_name")}
    rows = source.get("divisionResults", [])
    names = [row.get("division") for row in rows]
    if len(names) != len(set(names)):
        raise ValueError("duplicate domain benchmark result")
    unknown = sorted(name for name in names if name not in by_name)
    if unknown:
        raise ValueError(f"benchmark results contain unknown domain divisions: {unknown}")
    missing = sorted(set(by_name) - set(names))
    if missing:
        raise ValueError(f"benchmark results are missing canonical domain divisions: {missing}")
    if source.get("divisions") is not None and int(source["divisions"]) != len(rows):
        raise ValueError("benchmark division count does not match result rows")

    results = []
    for item in rows:
        domain = by_name[item["division"]]
        domain_id = domain.get("domain_id")
        if not domain_id:
            raise ValueError(f"canonical domain is missing domain_id: {item['division']}")
        results.append({
            "scope": "domain_division",
            "domain_id": domain_id,
            "division": domain["domain_name"],
            # A domain benchmark is not MasterBot mastery or owner approval.
            "masterbot_id": None,
            "mapping_status": domain.get("mapping_status", "unresolved"),
            "benchmark": "buddy-division-contract",
            "score": float(item["score"]) if item.get("score") is not None else None,
            "target": 100,
            "status": "pass" if item.get("status") == "pass" else "failed",
            "evidence_count": int(item.get("passed", 0)),
            "source": "run_daily_division_benchmarks",
        })
    return {
        "schema": "dreamco.benchmark_scores.v2",
        "scope": "domain_divisions",
        "domain_division_count": len(results),
        "masterbot_evidence_count": 0,
        "results": results,
        "policy": "domain evidence is not MasterBot mastery or ownership approval",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--crosswalk", default="config/generated/masterbot-55-domain-crosswalk.json")
    args = parser.parse_args()
    source = json.loads(Path(args.input).read_text(encoding="utf-8"))
    crosswalk = json.loads(Path(args.crosswalk).read_text(encoding="utf-8"))
    result = convert(source, crosswalk)
    Path(args.output).write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "domain_divisions": result["domain_division_count"],
        "masterbot_evidence": 0,
    }, indent=2))


if __name__ == "__main__":
    main()
