#!/usr/bin/env python3
"""Generate 55 per-bot, 100-slot DreamCo business curriculum manifests.

This generator creates metadata and empty, rights-blocked slots only. It does not
fetch external resources, create training examples, train models, or claim mastery.
"""
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ROSTER_PATH = ROOT / "config/dreamco-business-bot-swarm.json"
OUT = ROOT / "bot_manifests"
STAGES = [
    ("01_TASK_TAXONOMY", 1, 25, "occupational_task_taxonomies",
     "Role duties, skills, workflows, tool boundaries and human/robot/AI handoffs."),
    ("02_DOMAIN_PLAYBOOKS_SOPS", 26, 55, "domain_playbooks_and_sops",
     "Industry rules, SOPs, compliance checklists, templates, formulas and decision trees."),
    ("03_SYNTHETIC_SCENARIOS", 56, 80, "original_synthetic_scenarios",
     "Original synthetic examples, edge cases, multi-step tasks and failure-recovery drills."),
    ("04_EVALUATION_TOOL_HARNESSES", 81, 100, "evaluation_and_tool_use_harnesses",
     "Tool-use tests, JSON/schema contracts, benchmarks, regression and holdout evaluations."),
]

def build_manifest(bot: dict, model_targets: dict) -> dict:
    slots = []
    for stage, first, last, family, purpose in STAGES:
        for number in range(first, last + 1):
            slots.append({
                "resource_id": f"{bot['bot_id']}_R{number:03d}",
                "slot": number,
                "stage": stage,
                "source_family": family,
                "domain_tag": f"{bot['cluster'].lower()}.{bot['role_name'].lower()}",
                "purpose": purpose,
                "resource_ref": None,
                "asset_path": (
                    f"datasets/business_bots/{bot['bot_id'].lower()}/"
                    f"{stage.lower()}/resource_{number:03d}.jsonl"
                ),
                "resource_status": "UNASSIGNED_SLOT",
                "license_status": "NOT_REVIEWED",
                "training_permission": "UNKNOWN_BLOCKED",
                "provenance_required": True,
                "blocked_until_approved": [
                    "download_content", "bulk_ingest", "train", "fine_tune",
                    "redistribute", "resell_source_material"
                ],
            })
    return {
        "schema": "dreamco.business_bot_resource_manifest.v1",
        "manifest_version": "1.0.0",
        "bot_id": bot["bot_id"],
        "bot_number": bot["bot_number"],
        "role_name": bot["role_name"],
        "cluster": bot["cluster"],
        "focus": bot["focus"],
        "model_targets": model_targets,
        "curriculum_allocation": [
            {"stage": s[0], "slots_from": s[1], "slots_to": s[2],
             "resource_slots": s[2] - s[1] + 1, "source_family": s[3],
             "purpose": s[4]} for s in STAGES
        ],
        "curriculum": slots,
        "resource_count": len(slots),
        "policy": {
            "source_material_is_not_automatically_training_data": True,
            "unknown_rights": "BLOCK",
            "benchmark_holdouts_must_remain_separate": True,
            "synthetic_examples_must_be_original": True,
            "model_training_requires_separate_approval": True,
        },
    }

def main() -> int:
    catalog = json.loads(ROSTER_PATH.read_text(encoding="utf-8"))
    bots = catalog["bots"]
    if len(bots) != 55:
        raise ValueError(f"Expected 55 bots, found {len(bots)}")
    if len({b["bot_id"] for b in bots}) != 55:
        raise ValueError("Bot IDs must be unique")
    OUT.mkdir(parents=True, exist_ok=True)
    targets = {
        "micro_model_parameters": catalog["micro_model_computed_parameters"],
        "upgrade_model_parameters": catalog["upgrade_model_computed_parameters"],
        "collective_55_bot_target_parameters": catalog["aggregate_micro_model_parameters"],
        "weights_included": False,
        "weights_status": "UNTRAINED_BLUEPRINT_READY_FOR_TRAINING",
    }
    for bot in bots:
        manifest = build_manifest(bot, targets)
        if len(manifest["curriculum"]) != 100:
            raise AssertionError(f"{bot['bot_id']} does not have 100 slots")
        path = OUT / f"bot_{bot['bot_number']:02d}_manifest.json"
        path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"Generated {len(bots)} manifests and {len(bots) * 100} rights-blocked resource slots.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
