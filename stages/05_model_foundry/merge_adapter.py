"""Merge a LoRA adapter only after signed holdout evaluation passes."""
from __future__ import annotations
import argparse, hashlib, json, re
from pathlib import Path
from .guardrails import require_model_authorization, sha256_file, verify_signed_manifest

def safetensors_digest(folder: Path) -> str:
    files=sorted(folder.glob("*.safetensors"))
    if not files: raise ValueError("adapter directory has no .safetensors weights")
    h=hashlib.sha256()
    for path in files:
        h.update(path.name.encode("utf-8")); h.update(path.read_bytes())
    return h.hexdigest()

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--adapter",type=Path,required=True)
    p.add_argument("--base-model",required=True)
    p.add_argument("--base-revision",required=True)
    p.add_argument("--manifest",type=Path,required=True)
    p.add_argument("--signature",type=Path,required=True)
    p.add_argument("--public-key",type=Path,required=True)
    p.add_argument("--holdout-report",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    p.add_argument("--execute-merge",action="store_true")
    a=p.parse_args()
    if not re.fullmatch(r"[0-9a-f]{40}",a.base_revision):
        raise PermissionError("base model revision must be a pinned 40-character commit SHA")
    manifest=verify_signed_manifest(a.manifest,a.signature,a.public_key)
    require_model_authorization(manifest,a.base_model,a.base_revision)
    report=json.loads(a.holdout_report.read_text(encoding="utf-8"))
    if report.get("schema")!="dreamco.foundry.holdout_evaluation.v1" or report.get("promotion_eligible") is not True:
        raise PermissionError("a passing isolated holdout evaluation is required before adapter merge")
    adapter_hash=safetensors_digest(a.adapter)
    if report.get("candidate_checkpoint_sha256")!=adapter_hash:
        raise PermissionError("holdout report does not attest to this exact adapter checkpoint")
    if not a.execute_merge:
        print(json.dumps({"preflight":"passed","adapter_sha256":adapter_hash,
          "base_model":a.base_model,"base_revision":a.base_revision,"merge_started":False},sort_keys=True))
        return
    if a.output.exists() and any(a.output.iterdir()):
        raise FileExistsError("merge output directory must be absent or empty")
    try:
        from transformers import AutoModelForCausalLM, AutoTokenizer
        from peft import PeftModel
    except ImportError as exc:
        raise RuntimeError("Install requirements-foundry-training.txt to merge LoRA adapters") from exc
    base=AutoModelForCausalLM.from_pretrained(a.base_model,revision=a.base_revision,
        trust_remote_code=False,use_safetensors=True,torch_dtype="auto")
    adapter=PeftModel.from_pretrained(base,a.adapter,is_trainable=False)
    merged=adapter.merge_and_unload()
    a.output.mkdir(parents=True,exist_ok=True)
    merged.save_pretrained(a.output,safe_serialization=True)
    tokenizer=AutoTokenizer.from_pretrained(a.adapter,trust_remote_code=False)
    tokenizer.save_pretrained(a.output)
    weights=safetensors_digest(a.output)
    payload={"schema":"dreamco.foundry.merged_checkpoint.v1","base_model":a.base_model,
      "base_revision":a.base_revision,"adapter_sha256":adapter_hash,
      "holdout_report_sha256":sha256_file(a.holdout_report),"merged_weights_sha256":weights,
      "promotion_gate":"passed","merge_started":True}
    (a.output/"merge_manifest.json").write_text(json.dumps(payload,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(payload,sort_keys=True))
if __name__=="__main__": main()
