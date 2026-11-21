"""Review-only study of public model-weight metadata; never downloads or modifies weights."""
from __future__ import annotations
import hashlib
import json
from typing import Any

ALLOWED_LICENSES = {"apache-2.0", "mit", "bsd-3-clause", "cc-by-4.0"}
TECHNIQUES = ("quantization", "lora", "qlora", "pruning", "distillation", "kv_cache", "mixed_precision")

def study_models(models: list[dict[str, Any]], *, memory_gb: float = 24.0) -> dict[str, Any]:
    """Generate evidence-based study proposals, not training jobs or capability claims."""
    if not 0 < memory_gb <= 4096:
        raise ValueError("invalid memory budget")
    output = []
    for item in models:
        model_id = str(item.get("model_id", "")).strip()
        revision = str(item.get("revision", "")).strip()
        license_id = str(item.get("license", "")).lower().strip()
        parameters = item.get("parameters")
        if not model_id or not revision or not isinstance(parameters, int) or parameters <= 0:
            continue
        if "/" not in model_id or any(c.isspace() for c in model_id):
            continue
        allowed = license_id in ALLOWED_LICENSES and item.get("derivative_training_permitted") is True
        memory = {str(bits): round(parameters * bits / 8 / 1e9 * 1.3, 2) for bits in (4, 8, 16)}
        output.append({
            "model_id": model_id, "revision": revision, "license": license_id,
            "license_review_required": not allowed,
            "estimated_weight_memory_gb": memory,
            "estimated_only_excludes_kv_cache_activations_training_optimizer": True,
            "local_inference_candidate_4bit": memory["4"] < memory_gb * 0.65,
            "local_training_approved": False,
            "study_topics": list(TECHNIQUES),
            "benchmark_required": True,
            "source_reference": str(item.get("source_reference", "")),
            "evidence_status": "metadata_unverified",
        })
    output.sort(key=lambda x: (x["model_id"], x["revision"]))
    payload = json.dumps(output, sort_keys=True, separators=(",", ":")).encode()
    return {"schema_version": 1, "models": output, "count": len(output),
            "manifest_sha256": hashlib.sha256(payload).hexdigest(),
            "training_executed": False, "weights_downloaded": False}

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("input", help="JSON array of model metadata supplied by an authorized curator")
    parser.add_argument("--memory-gb", type=float, default=24.0)
    args = parser.parse_args()
    with open(args.input, encoding="utf-8") as handle:
        models = json.load(handle)
    if not isinstance(models, list):
        parser.error("input must be a JSON array")
    print(json.dumps(study_models(models, memory_gb=args.memory_gb), indent=2))
