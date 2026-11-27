#!/usr/bin/env python3
"""Fail-closed validation for the DreamCo pretrained-model storefront catalog."""
from __future__ import annotations
import argparse, hashlib, json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "config/marketplace/pretrained-model-catalog.json"
HASH = re.compile(r"^[a-f0-9]{64}$")
REQUIRED_SALE_FIELDS = (
    "model_id", "version", "display_name", "parameter_count", "architecture",
    "weights_sha256", "tokenizer_sha256", "model_license",
    "commercial_use_allowed", "redistribution_allowed", "minimum_memory_gb",
    "recommended_memory_gb", "supported_runtimes", "evaluation_report",
    "model_card", "training_run_id", "dataset_provenance",
    "rights_evidence_ref", "weights_package_uri", "status",
)

def validate(catalog: dict) -> list[str]:
    errors = []
    if catalog.get("schema") != "dreamco.pretrained_model_marketplace.v1":
        errors.append("unsupported catalog schema")
    policy = catalog.get("policy", {})
    if policy.get("parameter_count_limit") is not None:
        errors.append("marketplace parameter_count_limit must remain null (unbounded catalog)")
    if policy.get("source_data_included") is not False:
        errors.append("source datasets must never be included in model packages")
    if not isinstance(catalog.get("models"), list):
        return errors + ["models must be a list"]
    seen = set()
    for model in catalog["models"]:
        model_id = model.get("model_id", "")
        if not model_id or model_id in seen:
            errors.append("model IDs must be non-empty and unique")
        seen.add(model_id)
        if not isinstance(model.get("parameter_count"), int) or model["parameter_count"] < 1:
            errors.append(f"{model_id}: parameter_count must be a positive integer")
        if model.get("status") == "approved_for_sale":
            missing = [field for field in REQUIRED_SALE_FIELDS if field not in model or model[field] in (None, "", [])]
            if missing:
                errors.append(f"{model_id}: sale listing missing {', '.join(missing)}")
            for key in ("weights_sha256", "tokenizer_sha256"):
                if not HASH.fullmatch(str(model.get(key, ""))):
                    errors.append(f"{model_id}: invalid {key}")
            for key in ("commercial_use_allowed", "redistribution_allowed"):
                if not isinstance(model.get(key), bool):
                    errors.append(f"{model_id}: {key} must be an explicit boolean")
            if model.get("minimum_memory_gb", 0) <= 0 or model.get("recommended_memory_gb", 0) < model.get("minimum_memory_gb", 0):
                errors.append(f"{model_id}: invalid memory requirements")
            if model.get("rights_approval_status") != "APPROVED":
                errors.append(f"{model_id}: rights approval must be APPROVED")
            if model.get("evaluation_status") != "PASSED":
                errors.append(f"{model_id}: evaluation status must be PASSED")
    return errors

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--catalog", type=Path, default=CATALOG)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    catalog = json.loads(args.catalog.read_text(encoding="utf-8"))
    errors = validate(catalog)
    if errors:
        print("\n".join(f"ERROR: {e}" for e in errors))
        return 1
    print(f"OK: {len(catalog['models'])} catalog entries; unbounded parameter count; sale gates enforced")
    return 0
if __name__ == "__main__":
    raise SystemExit(main())
