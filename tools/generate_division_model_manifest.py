#!/usr/bin/env python3
"""Generate an honest, registry-derived inventory of division model slots."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "config" / "masterbot-65-registry.json"
OUTPUT = ROOT / "config" / "generated" / "division-model-manifest.json"


def build_manifest(registry: dict, source_text: str) -> dict:
    divisions = registry.get("divisions")
    if not isinstance(divisions, list) or not divisions:
        raise ValueError("canonical registry must contain a non-empty divisions array")
    ids = [item.get("id") for item in divisions]
    names = [item.get("name") for item in divisions]
    if any(not isinstance(value, int) or value <= 0 for value in ids):
        raise ValueError("every division must have a positive integer id")
    if any(not isinstance(value, str) or not value.strip() for value in names):
        raise ValueError("every division must have a non-empty name")
    if len(ids) != len(set(ids)) or len(names) != len(set(names)):
        raise ValueError("division ids and names must be unique")
    if registry.get("canonical_count") != len(divisions):
        raise ValueError("canonical_count does not match the registry divisions array")

    records = []
    for division in divisions:
        slug = "".join(ch.lower() if ch.isalnum() else "-" for ch in division["name"]).strip("-")
        while "--" in slug:
            slug = slug.replace("--", "-")
        records.append({
            "division_id": division["id"], "division_name": division["name"],
            "model_id": f"dreamco.division.{slug}", "model_version": "0.0.0",
            "lifecycle_state": "planned", "ownership_class": "dreamco_first_party_candidate",
            "base_model": None,
            "tokenizer": {"mode": "unselected", "reference": None},
            "training": {"dataset_manifest": None, "recipe": None, "checkpoint": None, "checkpoint_sha256": None},
            "evaluation": {"suite": None, "last_result": None},
            "serving": {"endpoint": None, "deployment_revision": None},
            "release_evidence": {"model_card": None, "license_review": None, "approval_record": None}
        })
    git_blob = f"blob {len(source_text.encode('utf-8'))}\\0".encode("ascii") + source_text.encode("utf-8")
    return {
        "schema": "dreamco.division_model_manifest.v1",
        "status": "inventory_only_not_trained",
        "source_of_truth": "config/masterbot-65-registry.json",
        "source_blob_sha": hashlib.sha1(git_blob).hexdigest(),
        "division_count": len(records), "records": records,
        "truth": "Generated inventory placeholders only. Null artifacts and planned states mean no training, evaluation, approval, or deployment is asserted."
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="fail if the committed manifest is stale")
    args = parser.parse_args()
    source_text = SOURCE.read_text(encoding="utf-8")
    manifest = build_manifest(json.loads(source_text), source_text)
    rendered = json.dumps(manifest, indent=2, ensure_ascii=False) + "\\n"
    if args.check:
        if not OUTPUT.exists() or OUTPUT.read_text(encoding="utf-8") != rendered:
            raise SystemExit("division model manifest is stale; run tools/generate_division_model_manifest.py")
        print(f"division model manifest current: {manifest['division_count']} divisions")
        return 0
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(rendered, encoding="utf-8")
    print(f"generated {OUTPUT.relative_to(ROOT)} for {manifest['division_count']} divisions")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
