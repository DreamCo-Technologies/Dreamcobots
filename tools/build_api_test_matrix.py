#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROGRAM = ROOT / "config" / "api-test-arsenal-program.json"
OUT = ROOT / "config" / "generated" / "api-test-matrix.json"


def normalize_test_id(family: str, label: str) -> str:
    raw = f"{family}-{label}".lower()
    return "".join(ch if ch.isalnum() else "-" for ch in raw).strip("-").replace("--", "-")


def main() -> int:
    parser = argparse.ArgumentParser(description="Build Buddy Bootcamp API test matrices from reusable profiles.")
    parser.add_argument("--profile", action="append", help="Optional API profile id; repeat to select more than one.")
    parser.add_argument("--api-id", default="example-api", help="Logical API identifier for the generated plan.")
    parser.add_argument("--provider", default="unconfigured", help="Provider label; no network request is made.")
    args = parser.parse_args()

    program = json.loads(PROGRAM.read_text(encoding="utf-8"))
    profiles = program["api_profiles"]
    requested = set(args.profile or [])
    selected = [p for p in profiles if not requested or p["id"] in requested]
    if requested - {p["id"] for p in selected}:
        missing = sorted(requested - {p["id"] for p in selected})
        raise SystemExit(f"Unknown profile(s): {', '.join(missing)}")

    matrices = []
    total = 0
    for profile in selected:
        tests = []
        for family in profile["test_families"]:
            for label in program["test_families"].get(family, []):
                tests.append({
                    "test_id": normalize_test_id(family, label),
                    "family": family,
                    "name": label,
                    "status": "not_run",
                    "execution_boundary": profile["mode"],
                })
        total += len(tests)
        matrices.append({
            "api_id": args.api_id,
            "provider": args.provider,
            "profile": profile["id"],
            "kind": profile["kind"],
            "mode": profile["mode"],
            "tests": tests,
            "test_count": len(tests),
        })

    payload = {
        "schema": "dreamco.api_test_matrix.v1",
        "source": str(PROGRAM.relative_to(ROOT)),
        "network_executed": False,
        "external_write_executed": False,
        "truth_boundary": "This file is a generated test plan. Individual tests remain not_run until an approved runner records evidence.",
        "matrices": matrices,
        "profile_count": len(matrices),
        "total_planned_tests": total,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"ok": True, "profiles": len(matrices), "planned_tests": total, "output": str(OUT.relative_to(ROOT))}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
