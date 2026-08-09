#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROGRAM = ROOT / "config" / "universal-api-task-sandbox-program.json"


def slug(value: str) -> str:
    return re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-", value.lower())).strip("-")


def validate_spec(spec: dict, program: dict) -> list[str]:
    missing = [field for field in program["required_target_spec"] if field not in spec]
    if spec.get("target_type") not in program["supported_targets"]:
        missing.append("supported target_type")
    return missing


def build_plan(spec: dict, program: dict) -> dict:
    missing = validate_spec(spec, program)
    if missing:
        raise SystemExit("Invalid target spec; missing/invalid: " + ", ".join(missing))
    target_type = spec["target_type"]
    side_effect = spec["side_effect_level"]
    if side_effect not in program["side_effect_levels"]:
        raise SystemExit(f"Unknown side_effect_level: {side_effect}")
    dimensions = list(program["shared_test_dimensions"])
    cases = []
    for mode in program["execution_modes"]:
        for dim in dimensions:
            cases.append({
                "case_id": slug(f"{spec['target_id']}-{mode}-{dim}"),
                "target_id": spec["target_id"],
                "target_type": target_type,
                "dimension": dim,
                "execution_mode": mode,
                "status": "planned_not_run",
                "evidence": None,
            })
    return {
        "schema": "dreamco.universal_api_task_sandbox_plan.v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "target": spec,
        "side_effect_policy": program["side_effect_levels"][side_effect],
        "planned_case_count": len(cases),
        "cases": cases,
        "benchmark_gap_output": program["benchmark_gap_output"],
        "truth_boundary": program["truth_rule"],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a DreamCo sandbox plan for any API/task contract")
    parser.add_argument("spec", help="Path to a JSON target spec")
    parser.add_argument("--output")
    args = parser.parse_args()
    program = json.loads(PROGRAM.read_text(encoding="utf-8"))
    spec_path = Path(args.spec)
    if not spec_path.is_absolute():
        spec_path = ROOT / spec_path
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    plan = build_plan(spec, program)
    output = Path(args.output) if args.output else ROOT / ".buddy-local" / "artifacts" / "sandbox-plans" / f"{slug(spec['target_id'])}.json"
    if not output.is_absolute():
        output = ROOT / output
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(plan, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"ok": True, "target": spec["target_id"], "cases": plan["planned_case_count"], "output": str(output.relative_to(ROOT))}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
