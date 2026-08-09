#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import itertools
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROGRAM = ROOT / "config" / "buddy-full-potential-sandbox-open-source-evolution-program.json"
OUT = ROOT / "config" / "generated" / "full-potential-sandbox-catalog.json"


def slug(value: str) -> str:
    return re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-", value.lower())).strip("-")


def stable_id(parts: list[str]) -> str:
    label = "--".join(slug(part) for part in parts)
    digest = hashlib.sha256("|".join(parts).encode()).hexdigest()[:10]
    return f"sandbox--{label[:120]}--{digest}"


def main() -> int:
    program = json.loads(PROGRAM.read_text(encoding="utf-8"))
    axes = program["sandbox_axes"]
    families = program["required_test_families"]

    # Cross the highest-value behavioral axes. This intentionally creates thousands
    # of reusable categories without materializing every theoretical combination.
    cross_specs = [
        ("difficulty", "input_quality", "dependency_state"),
        ("difficulty", "permission_state", "workflow_shape"),
        ("resource_pressure", "efficiency_target", "workflow_shape"),
        ("security_privacy", "permission_state", "evidence_mode"),
        ("recovery", "dependency_state", "workflow_shape"),
        ("quality_target", "input_quality", "evidence_mode"),
        ("world_context", "permission_state", "security_privacy"),
    ]

    categories: list[dict] = []
    seen = set()
    for family in families:
        # Each family inherits a compact set of universal single-axis drills.
        for axis_name in ["difficulty", "evidence_mode", "world_context"]:
            for value in axes[axis_name]:
                parts = [family, axis_name, value]
                test_id = stable_id(parts)
                if test_id not in seen:
                    seen.add(test_id)
                    categories.append({
                        "category_id": test_id,
                        "family": family,
                        "axes": {axis_name: value},
                        "execution_status": "planned_not_run",
                    })

    for spec in cross_specs:
        values = [axes[name] for name in spec]
        for combo in itertools.product(*values):
            axis_map = dict(zip(spec, combo))
            parts = [f"{name}:{value}" for name, value in axis_map.items()]
            test_id = stable_id(list(spec) + list(combo))
            if test_id not in seen:
                seen.add(test_id)
                categories.append({
                    "category_id": test_id,
                    "family": "cross_axis_stress",
                    "axes": axis_map,
                    "execution_status": "planned_not_run",
                })

    payload = {
        "schema": "dreamco.full_potential_sandbox_catalog.v1",
        "source_program": str(PROGRAM.relative_to(ROOT)),
        "test_family_count": len(families),
        "axis_count": len(axes),
        "category_count": len(categories),
        "categories": categories,
        "application_rule": "Every bot capability, discovered tool and discovered callable function inherits relevant categories by family/axis reference; the catalog is shared to avoid duplicating thousands of rows per bot.",
        "truth_boundary": "Generated categories are planned drills. They become passed only when executable runners record evidence for a specific bot/capability/tool/function in an approved environment."
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "ok": True,
        "families": payload["test_family_count"],
        "axes": payload["axis_count"],
        "sandbox_categories": payload["category_count"],
        "output": str(OUT.relative_to(ROOT)),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
