#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import itertools
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "config" / "universal-human-ai-software-task-sandbox.json"
OUT = ROOT / "config" / "generated" / "universal-human-ai-task-sandbox.json"


def slug(value: str) -> str:
    return re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-", value.lower())).strip("-")


def category_id(parts: list[str]) -> str:
    digest = hashlib.sha256("|".join(parts).encode()).hexdigest()[:10]
    label = "--".join(slug(p) for p in parts)
    return f"task--{label[:130]}--{digest}"


def main() -> int:
    cfg = json.loads(CONFIG.read_text(encoding="utf-8"))
    rows = []
    seen = set()

    # Primary task-space: task action × domain × complexity.
    for action, domain, complexity in itertools.product(cfg["task_actions"], cfg["domains"], cfg["complexity"]):
        parts = [action, domain, complexity]
        cid = category_id(parts)
        if cid in seen:
            continue
        seen.add(cid)
        rows.append({
            "category_id": cid,
            "task_action": action,
            "domain": domain,
            "complexity": complexity,
            "status": "planned_not_run",
            "inherits_quality_dimensions": True,
        })

    # Additional environment/modality/persona drills without exploding the repo.
    overlays = []
    for modality, environment in itertools.product(cfg["modalities"], cfg["environments"]):
        overlays.append({"modality": modality, "environment": environment})
    for context in cfg["user_contexts"]:
        overlays.append({"user_context": context})
    for scenario in cfg["special_business_client_scenarios"]:
        overlays.append({"special_business_scenario": scenario})
    for scenario in cfg["special_personal_scenarios"]:
        overlays.append({"special_personal_scenario": scenario})

    payload = {
        "schema": "dreamco.universal_human_ai_task_sandbox.generated.v1",
        "task_action_count": len(cfg["task_actions"]),
        "domain_count": len(cfg["domains"]),
        "complexity_count": len(cfg["complexity"]),
        "quality_dimension_count": len(cfg["quality_dimensions"]),
        "overlay_count": len(overlays),
        "category_count": len(rows),
        "categories": rows,
        "overlays": overlays,
        "application_rule": "Each bot or arbitrary user task selects relevant base categories and overlays by mission, domain, modality, environment, user context and side-effect policy. Runtime evidence is stored separately from the shared catalog.",
        "truth_boundary": cfg["truth_rule"],
    }
    if payload["category_count"] < cfg["minimum_generated_categories"]:
        raise SystemExit(f"universal task sandbox too small: {payload['category_count']}")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "ok": True,
        "task_actions": payload["task_action_count"],
        "domains": payload["domain_count"],
        "categories": payload["category_count"],
        "overlays": payload["overlay_count"],
        "output": str(OUT.relative_to(ROOT)),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
