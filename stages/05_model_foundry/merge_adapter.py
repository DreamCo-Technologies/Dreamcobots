"""Merge a LoRA adapter only after signed holdout evaluation passes."""
from __future__ import annotations
import argparse, hashlib, json, re
from pathlib import Path
from .guardrails import require_model_authorization, sha256_file, verify_signed_manifest

def safetensors_digest(folder: Path) -> str:
    files=sorted(folder.glob("*.safetensors"),key=lambda item:item.name)
    if not files: raise ValueError("adapter directory has no .safetensors weights")
    return hashlib.sha256(b"".join(path.read_bytes() for path in files)).hexdigest()

def tokenizer_digest(folder: Path) -> str:
    names={"tokenizer.json","tokenizer_config.json","special_tokens_map.json",
           "added_tokens.json","vocab.json","merges.txt","tokenizer.model",
           "spiece.model","foundry-tokenizer-manifest.json"}
    files=sorted((item for item in folder.rglob("*") if item.is_file() and item.name in names),
                 key=lambda item:item.relative_to(folder).as_posix())
    if not files: raise ValueError("adapter directory has no tokenizer artifacts")
    digest=hashlib.sha256()
    for item in files:
        digest.update(item.relative_to(folder).as_posix().encode("utf-8"))
        digest.update(b"\\0")
        digest.update(item.read_bytes())
        digest.update(b"\\0")
    return digest.hexdigest()

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
    model_auth=require_model_authorization(manifest,a.base_model,a.base_revision)
    checkpoint_manifest_path=a.adapter/"checkpoint_manifest.json"
    if not checkpoint_manifest_path.is_file():
        raise PermissionError("adapter checkpoint provenance manifest is required")
    checkpoint_manifest=json.loads(checkpoint_manifest_path.read_text(encoding="utf-8"))
    adapter_config_path=a.adapter/"adapter_config.json"
    if not adapter_config_path.is_file():
        raise PermissionError("LoRA adapter_config.json is required")
    adapter_config=json.loads(adapter_config_path.read_text(encoding="utf-8"))
    report=json.loads(a.holdout_report.read_text(encoding="utf-8"))
    if (report.get("schema")!="dreamco.foundry.holdout_evaluation.v1"
            or report.get("promotion_eligible") is not True
            or report.get("regressions")
            or report.get("holdout_access")!="evaluation_only"
            or report.get("training_access") is not False
            or report.get("source_manifest_sha256")!=sha256_file(a.manifest)):
        raise PermissionError("a passing baseline-comparison report for this signed holdout manifest is required before adapter merge")
    adapter_hash=safetensors_digest(a.adapter)
    provenance_ok = (
        checkpoint_manifest.get("schema")=="dreamco.foundry.checkpoint.v1"
        and checkpoint_manifest.get("stage")=="dpo"
        and checkpoint_manifest.get("checkpoint_sha256")==adapter_hash
        and checkpoint_manifest.get("source_manifest_sha256")==sha256_file(a.manifest)
        and checkpoint_manifest.get("base_model_id")==a.base_model
        and checkpoint_manifest.get("base_model_revision")==a.base_revision
        and adapter_config.get("base_model_name_or_path")==a.base_model
        and report.get("candidate_base_model_id")==a.base_model
        and report.get("candidate_base_model_revision")==a.base_revision
        and report.get("candidate_base_model_license_evidence_id")==model_auth.get("license_evidence_id")
        and checkpoint_manifest.get("license_evidence_id")==model_auth.get("license_evidence_id")
        and checkpoint_manifest.get("tokenizer_sha256")==tokenizer_digest(a.adapter)
        and checkpoint_manifest.get("training_split")=="train"
        and checkpoint_manifest.get("holdout_used_for_training") is False
        and checkpoint_manifest.get("weight_updates_started") is True
        and isinstance(checkpoint_manifest.get("authorization_reference_sha256"),str)
        and len(checkpoint_manifest.get("authorization_reference_sha256",""))==64
        and bool(checkpoint_manifest.get("shard_manifest_sha256"))
        and isinstance(checkpoint_manifest.get("recipe_sha256"),str)
        and len(checkpoint_manifest.get("recipe_sha256",""))==64
    )
    if not provenance_ok:
        raise PermissionError("adapter checkpoint provenance does not match this model, manifest, tokenizer and training authorization")
    if report.get("candidate_checkpoint_sha256")!=adapter_hash:
        raise PermissionError("holdout report does not attest to this exact adapter checkpoint")
    if report.get("candidate_tokenizer_sha256")!=tokenizer_digest(a.adapter):
        raise PermissionError("holdout report does not attest to the tokenizer stored with this adapter")
    if not a.execute_merge:
        print(json.dumps({"preflight":"passed","adapter_sha256":adapter_hash,
          "base_model":a.base_model,"base_revision":a.base_revision,
          "checkpoint_manifest_sha256":sha256_file(checkpoint_manifest_path),"merge_started":False},sort_keys=True))
        return
    if a.output.exists() and any(a.output.iterdir()):
        raise FileExistsError("merge output directory must be absent or empty")
    try:
        from transformers import AutoModelForCausalLM, AutoTokenizer
        from peft import PeftModel
    except ImportError as exc:
        raise RuntimeError("Install requirements-foundry-training.txt to merge LoRA adapters") from exc
    tokenizer=AutoTokenizer.from_pretrained(a.adapter,trust_remote_code=False,local_files_only=True)
    base=AutoModelForCausalLM.from_pretrained(a.base_model,revision=a.base_revision,
        trust_remote_code=False,use_safetensors=True,torch_dtype="auto",local_files_only=True)
    if len(tokenizer)!=base.get_input_embeddings().weight.shape[0]:
        base.resize_token_embeddings(len(tokenizer),mean_resizing=True)
    adapter=PeftModel.from_pretrained(base,a.adapter,is_trainable=False)
    merged=adapter.merge_and_unload(safe_merge=True)
    a.output.mkdir(parents=True,exist_ok=True)
    merged.save_pretrained(a.output,safe_serialization=True)
    tokenizer.save_pretrained(a.output)
    weights=safetensors_digest(a.output)
    payload={"schema":"dreamco.foundry.merged_checkpoint.v1","base_model":a.base_model,
      "base_revision":a.base_revision,"license_evidence_id":model_auth["license_evidence_id"],
      "checkpoint_manifest_sha256":sha256_file(checkpoint_manifest_path),
      "source_manifest_sha256":sha256_file(a.manifest),"adapter_sha256":adapter_hash,
      "holdout_report_sha256":sha256_file(a.holdout_report),"merged_weights_sha256":weights,
      "promotion_gate":"passed","merge_started":True}
    (a.output/"merge_manifest.json").write_text(json.dumps(payload,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(payload,sort_keys=True))
if __name__=="__main__": main()
