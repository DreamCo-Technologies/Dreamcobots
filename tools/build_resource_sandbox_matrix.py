#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROGRAM_PATH = ROOT / "config" / "buddy-resource-connection-sandbox-program.json"
ARSENAL_PATH = ROOT / "config" / "resource-sandbox-test-arsenal.json"
OUT_PATH = ROOT / "config" / "generated" / "resource-sandbox-test-matrix.json"


def slug(value: str) -> str:
    return re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-", value.lower())).strip("-")


def main() -> int:
    program = json.loads(PROGRAM_PATH.read_text(encoding="utf-8"))
    arsenal = json.loads(ARSENAL_PATH.read_text(encoding="utf-8"))

    shared = arsenal["shared_test_families"]
    category_scenarios = arsenal["category_scenarios"]
    matrix: list[dict] = []

    for resource_type in program["resource_types"]:
        for family, labels in shared.items():
            for label in labels:
                matrix.append({
                    "test_id": f"{resource_type}--{slug(family)}--{slug(label)}",
                    "resource_type": resource_type,
                    "scope": "shared",
                    "family": family,
                    "scenario": label,
                    "status": "not_run",
                    "execution_mode": "synthetic_or_mock_first",
                })
        for label in category_scenarios[resource_type]:
            matrix.append({
                "test_id": f"{resource_type}--category--{slug(label)}",
                "resource_type": resource_type,
                "scope": "category_specific",
                "family": "category_specific",
                "scenario": label,
                "status": "not_run",
                "execution_mode": "synthetic_or_mock_first",
            })

    ids = [row["test_id"] for row in matrix]
    if len(ids) != len(set(ids)):
        raise SystemExit("duplicate resource sandbox test ids detected")

    counts_by_type = {
        resource_type: sum(1 for row in matrix if row["resource_type"] == resource_type)
        for resource_type in program["resource_types"]
    }
    payload = {
        "schema": "dreamco.resource_sandbox_test_matrix.v1",
        "source_program": str(PROGRAM_PATH.relative_to(ROOT)),
        "source_arsenal": str(ARSENAL_PATH.relative_to(ROOT)),
        "network_executed": False,
        "external_writes_executed": False,
        "resource_type_count": len(program["resource_types"]),
        "shared_family_count": len(shared),
        "planned_test_count": len(matrix),
        "counts_by_resource_type": counts_by_type,
        "truth_boundary": "Generated rows are planned sandbox cases and remain not_run until a test runner records evidence.",
        "tests": matrix,
    }
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "ok": True,
        "resource_types": payload["resource_type_count"],
        "shared_families": payload["shared_family_count"],
        "planned_tests": payload["planned_test_count"],
        "output": str(OUT_PATH.relative_to(ROOT)),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
