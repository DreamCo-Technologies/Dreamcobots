#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP_BOTS = ROOT / "App_bots"
PROGRAM = ROOT / "config" / "bot-universal-sandbox-skill-gap-program.json"
UNIVERSAL_TASK = ROOT / "config" / "generated" / "universal-human-ai-task-sandbox.json"
OUT = ROOT / "config" / "generated" / "bot-sandbox-curriculum.json"


def main() -> int:
    program = json.loads(PROGRAM.read_text(encoding="utf-8"))
    universal = json.loads(UNIVERSAL_TASK.read_text(encoding="utf-8")) if UNIVERSAL_TASK.exists() else None
    capability_dims = program["capability_test_dimensions"]
    tool_dims = program["tool_test_dimensions"]
    function_dims = program["function_test_dimensions"]
    efficiency_dims = program["efficiency_dimensions"]
    bots = []
    seen = set()
    total_capabilities = 0

    for path in sorted(APP_BOTS.glob("*.json")):
        payload = json.loads(path.read_text(encoding="utf-8"))
        division = payload.get("division") or path.stem
        for bot in payload.get("bots", []):
            slug = str(bot.get("slug", "")).strip()
            if not slug:
                raise SystemExit(f"bot without slug in {path}")
            if slug in seen:
                raise SystemExit(f"duplicate bot slug: {slug}")
            seen.add(slug)
            capabilities = [str(c).strip() for c in (bot.get("capabilities") or []) if str(c).strip()]
            total_capabilities += len(capabilities)
            capability_tests = [
                {
                    "capability": capability,
                    "dimensions": capability_dims,
                    "status": "planned_not_run",
                    "evidence": None,
                }
                for capability in capabilities
            ]
            bots.append({
                "slug": slug,
                "display_name": bot.get("displayName"),
                "division": division,
                "category": bot.get("category"),
                "source": str(path.relative_to(ROOT)),
                "declared_capability_count": len(capabilities),
                "capability_tests": capability_tests,
                "universal_task_sandbox": {
                    "catalog": "config/generated/universal-human-ai-task-sandbox.json",
                    "catalog_status": "available" if universal else "must_generate_first",
                    "base_category_count_available": universal.get("category_count") if universal else 0,
                    "selection_status": "runtime_mapping_required",
                    "selection_rule": "Map every declared capability and discovered tool/function to all relevant task-action/domain/complexity rows plus applicable modality, environment, personal/business, security, permission, efficiency, recovery and benchmark overlays.",
                    "all_applicable_tests_must_pass_for_graduation": True,
                    "unrelated_domain_tests_may_be_not_applicable_with_reason": True,
                },
                "tool_contract": {
                    "inventory_status": "runtime_discovery_required",
                    "dimensions": tool_dims,
                    "rule": "Every discovered runtime tool must receive this test set and relevant universal-task sandbox rows; a bot with no tools must record an explicit no-tool declaration."
                },
                "function_contract": {
                    "inventory_status": "runtime_discovery_required",
                    "dimensions": function_dims,
                    "rule": "Every discovered callable function must receive this test set and relevant universal-task sandbox rows; a bot with no callable functions must record an explicit no-function declaration."
                },
                "efficiency": {
                    "dimensions": efficiency_dims,
                    "baseline_status": "required",
                    "target_status": "required",
                },
                "skill_ladder": program["skill_ladder"],
                "benchmark_gap_plan": {
                    "status": "required",
                    "required_fields": program["gap_plan_required_fields"],
                    "priority_formula": program["gap_priority_formula"],
                    "shared_fix_first": True,
                },
                "graduation": {
                    "status": "not_graduated_by_generation",
                    "requires_runtime_evidence": True,
                    "requires_all_declared_capabilities_covered": True,
                    "requires_tools_and_functions_inventory": True,
                    "requires_universal_task_coverage": True,
                    "requires_all_applicable_universal_tests_pass": True,
                    "requires_efficiency_baseline": True,
                    "requires_gap_plan": True,
                }
            })

    payload = {
        "schema": "dreamco.bot_sandbox_curriculum.v1",
        "program": str(PROGRAM.relative_to(ROOT)),
        "universal_task_catalog": str(UNIVERSAL_TASK.relative_to(ROOT)),
        "universal_task_catalog_available": bool(universal),
        "universal_task_base_category_count": universal.get("category_count") if universal else 0,
        "bot_count": len(bots),
        "division_count": len({b['division'] for b in bots}),
        "declared_capability_count": total_capabilities,
        "capability_test_dimensions": len(capability_dims),
        "planned_capability_test_instances": total_capabilities * len(capability_dims),
        "tool_test_dimensions_per_discovered_tool": len(tool_dims),
        "function_test_dimensions_per_discovered_function": len(function_dims),
        "efficiency_dimensions_per_bot": len(efficiency_dims),
        "planned_efficiency_measurements": len(bots) * len(efficiency_dims),
        "bots": bots,
        "truth_boundary": "This file maps every declared bot capability to sandbox dimensions and the universal human/AI/software task catalog. Runtime tool/function inventories, applicability mapping and pass/fail evidence must be produced by executable runners; generation alone is not a pass."
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "ok": True,
        "bots": payload["bot_count"],
        "divisions": payload["division_count"],
        "capabilities": total_capabilities,
        "universal_task_categories_available": payload["universal_task_base_category_count"],
        "planned_capability_test_instances": payload["planned_capability_test_instances"],
        "planned_efficiency_measurements": payload["planned_efficiency_measurements"],
        "output": str(OUT.relative_to(ROOT)),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
