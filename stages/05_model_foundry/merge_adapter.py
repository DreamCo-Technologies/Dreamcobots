"""Merge a LoRA adapter only after the matching holdout report passes."""
from __future__ import annotations
import argparse
import hashlib
import json
import re
from pathlib import Path
try:
    from .guardrails import require_model_authorization, verify_signed_manifest
except ImportError:
    from guardrails import require_model_authorization, verify_signed_manifest

def checkpoint_digest(directory: Path) -> str:
    files = sorted(directory.glob("*.safetensors"))
    if not files:
        raise ValueError("adapter directory contains no safetensors checkpoint")
    digest = hashlib.sha256()
    for path in files:
        digest.update(path.read_bytes())
    return digest.hexdigest()

def main():
    parser = argparse.ArgumentParser(description="Merge a verified DreamCo LoRA adapter")
    parser.add_argument("--base-model", required=True)
    parser.add_argument("--base-revision", required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--signature", type=Path, required=True)
    parser.add_argument("--public-key", type=Path, required=True)
    parser.add_argument("--adapter", type=Path, required=True)
    parser.add_argument("--tokenizer", type=Path, required=True)
    parser.add_argument("--holdout-report", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if not re.fullmatch(r"[0-9a-f]{40}", args.base_revision):
        raise ValueError("base revision must be a pinned 40-character commit SHA")
    manifest = verify_signed_manifest(args.manifest, args.signature, args.public_key)
    model_authorization = require_model_authorization(manifest, args.base_model, args.base_revision)
    report = json.loads(args.holdout_report.read_text(encoding="utf-8"))
    if report.get("promotion_eligible") is not True or report.get("regressions"):
        raise PermissionError("adapter merge is blocked until holdout verification passes")
    expected = report.get("candidate_checkpoint_sha256")
    actual = checkpoint_digest(args.adapter)
    if expected != actual:
        raise ValueError("holdout report does not match the exact adapter checkpoint bytes")

    import torch  # noqa: F401
    from peft import PeftModel
    from transformers import AutoModelForCausalLM, AutoTokenizer
    base = AutoModelForCausalLM.from_pretrained(
        args.base_model, revision=args.base_revision,
        trust_remote_code=False, use_safetensors=True, torch_dtype="auto",
    )
    model = PeftModel.from_pretrained(base, args.adapter)
    merged = model.merge_and_unload(safe_merge=True)
    args.output.mkdir(parents=True, exist_ok=True)
    merged.save_pretrained(args.output, safe_serialization=True)
    tokenizer = AutoTokenizer.from_pretrained(args.tokenizer, trust_remote_code=False)
    tokenizer.save_pretrained(args.output)
    manifest = {
        "schema": "dreamco.foundry.merged_checkpoint.v1",
        "base_model": args.base_model,
        "base_revision": args.base_revision,
        "license_evidence_id": model_authorization["license_evidence_id"],
        "adapter_sha256": actual,
        "holdout_report_sha256": hashlib.sha256(args.holdout_report.read_bytes()).hexdigest(),
        "merged_checkpoint_files": sorted(path.name for path in args.output.glob("*.safetensors")),
        "promotion_source": "verified_holdout_report",
    }
    (args.output / "merged_checkpoint_manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8",
    )

if __name__ == "__main__":
    main()
