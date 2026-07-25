#!/usr/bin/env python3
"""Validate and publish Buddy's governed open-model coding lab catalog."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "config" / "buddy-open-model-coding-lab.json"
GENERATED = ROOT / "config" / "generated" / "buddy_open_model_coding_lab.json"
PUBLIC = ROOT / "website" / "data" / "buddy-open-model-coding-lab.js"


def validate(payload: dict[str, Any]) -> dict[str, Any]:
    if payload.get("schema") != "dreamco.buddy_open_model_coding_lab.v1":
        raise ValueError("Unsupported open-model coding lab schema.")
    models = payload.get("model_families", [])
    tasks = payload.get("coding_tasks", [])
    runtimes = payload.get("local_runtimes", [])
    if len(models) < 6 or len(tasks) < 8 or len(runtimes) < 3:
        raise ValueError("The catalog needs global model, coding-task, and runtime coverage.")

    def unique_ids(rows: list[dict[str, Any]], label: str) -> None:
        ids = [str(row.get("id", "")).strip() for row in rows]
        if any(not value for value in ids) or len(ids) != len(set(ids)):
            raise ValueError(f"{label} ids must be present and unique.")

    unique_ids(models, "Model family")
    unique_ids(tasks, "Coding task")
    unique_ids(runtimes, "Runtime")
    regions = {str(model.get("developer_region", "")).strip() for model in models}
    if len(regions) < 3:
        raise ValueError("The catalog must represent at least three developer regions.")
    for model in models:
        source = urlsplit(str(model.get("official_source", "")))
        if source.scheme != "https" or not source.netloc:
            raise ValueError(f"Model source must be an official HTTPS URL: {model.get('id')}")
        if not str(model.get("license", "")).strip() or not model.get("exact_checkpoint_review_required"):
            raise ValueError(f"Model license and exact-checkpoint review are required: {model.get('id')}")
    policy = payload.get("comparison_policy", {})
    required_policy = {
        "developer_region_is_informational_only",
        "region_is_never_a_quality_score",
        "license_verified_per_exact_revision",
        "no_proprietary_output_harvesting",
        "live_execution_requires_a_sandbox_adapter",
    }
    if any(policy.get(key) is not True for key in required_policy):
        raise ValueError("Required comparison and licensing controls must remain enabled.")
    return {
        **payload,
        "summary": {
            "model_families": len(models),
            "developer_regions": len(regions),
            "coding_tasks": len(tasks),
            "local_runtimes": len(runtimes),
            "live_models_called": 0,
            "source_projects_executed": 0,
        },
    }


def serialize(payload: dict[str, Any]) -> str:
    return json.dumps(payload, indent=2, ensure_ascii=True) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    catalog = validate(json.loads(SOURCE.read_text(encoding="utf-8")))
    generated = serialize(catalog)
    public = f"window.BUDDY_OPEN_MODEL_CODING_LAB = {json.dumps(catalog, separators=(',', ':'))};\n"
    if args.check:
        for path, expected in ((GENERATED, generated), (PUBLIC, public)):
            if not path.exists() or path.read_text(encoding="utf-8") != expected:
                raise SystemExit(f"Generated file is stale: {path.relative_to(ROOT)}")
    else:
        GENERATED.parent.mkdir(parents=True, exist_ok=True)
        PUBLIC.parent.mkdir(parents=True, exist_ok=True)
        GENERATED.write_text(generated, encoding="utf-8")
        PUBLIC.write_text(public, encoding="utf-8")
    print(json.dumps(catalog["summary"], sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
