"""Explicitly invoked SFT/LoRA runner for rights-approved local JSONL datasets.

No network download or GPU use occurs unless the operator passes the explicit
execution flag, a matching compute approval ID, and enables model download.
"""
from __future__ import annotations
import hashlib
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from .hub import DatasetHub

class TrainingExecutionError(RuntimeError):
    pass

def _load_rows(path: Path) -> list[dict]:
    rows=[]
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip(): continue
        row=json.loads(line)
        if not isinstance(row,dict) or row.get("split") not in {"train","validation","test"}:
            raise TrainingExecutionError("Every JSONL record must be an object with train/validation/test split")
        if not isinstance(row.get("masterbot_id"), int):
            raise TrainingExecutionError("Every row must carry its canonical primary MasterBot ID")
        if not (row.get("text") or (row.get("instruction") and row.get("output"))):
            raise TrainingExecutionError("Each row needs text or instruction/output fields")
        rows.append(row)
    return rows

def _split_hash(rows: list[dict], split: str) -> str:
    payload="".join(json.dumps(row,sort_keys=True,ensure_ascii=False)+"\n" for row in rows if row["split"]==split)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()

def validate_job(job: dict, approval_id: str) -> tuple[Path,list[dict]]:
    if job.get("schema")!="dreamco.model_training_job.v1" or job.get("execution_status")!="NOT_EXECUTED":
        raise TrainingExecutionError("Invalid or already executed job manifest")
    if not approval_id or approval_id != job.get("compute_approval_id"):
        raise TrainingExecutionError("Compute approval ID does not match the job")
    if not re.fullmatch(r"[0-9a-f]{40}",str(job.get("base_model_revision",""))):
        raise TrainingExecutionError("Base model revision is not immutable")
    if not job.get("model_license") or not str(job.get("model_license_url","")).startswith("https://") or job.get("model_license_status") != "VERIFIED" or not job.get("model_license_evidence"):
        raise TrainingExecutionError("Verified model license evidence is missing")
    if job.get("training_method") not in {"sft","lora"}:
        raise TrainingExecutionError("Unsupported training method")
    hub=Path(job["dataset_hub_path"]).resolve()
    dataset_card=DatasetHub(hub).get(job["dataset_id"],int(job["dataset_version"]))
    if not dataset_card or dataset_card.get("training_approved") is not True or dataset_card.get("rights_status") != "VERIFIED" or dataset_card.get("holdout"):
        raise TrainingExecutionError("Dataset Hub card no longer authorizes training")
    card_hash=hashlib.sha256(json.dumps(dataset_card,sort_keys=True).encode()).hexdigest()
    if card_hash != job.get("dataset_card_sha256") or dataset_card.get("content_sha256") != job.get("dataset_sha256") or dataset_card.get("split_manifest") != job.get("split_manifest"):
        raise TrainingExecutionError("Dataset card, split manifest, or provenance changed after job creation")
    allowed_masterbots = {int(dataset_card.get("primary_masterbot_id"))} | {int(item) for item in dataset_card.get("collaborating_masterbot_ids", [])}
    if int(job.get("masterbot_id", -1)) not in allowed_masterbots:
        raise TrainingExecutionError("Training job is not assigned to the dataset's MasterBot owner or collaborator")
    object_path=(hub / job["dataset_object_path"]).resolve()
    if dataset_card.get("object_path") != job["dataset_object_path"]:
        raise TrainingExecutionError("Training job object path differs from the approved dataset card")
    if hub not in object_path.parents or not object_path.is_file():
        raise TrainingExecutionError("Dataset object is missing or outside the dataset hub")
    if hashlib.sha256(object_path.read_bytes()).hexdigest()!=job.get("dataset_sha256"):
        raise TrainingExecutionError("Dataset object hash mismatch")
    rows=_load_rows(object_path)
    expected=job.get("split_manifest",{})
    for split in ("train","validation","test"):
        if _split_hash(rows,split)!=expected.get(f"{split}_sha256"):
            raise TrainingExecutionError(f"{split} split hash mismatch")
        if not any(row["split"]==split for row in rows):
            raise TrainingExecutionError(f"{split} split is empty")
    target_masterbot=int(job["masterbot_id"])
    lane_rows=[row for row in rows if row["masterbot_id"]==target_masterbot]
    for split in ("train","validation","test"):
        if not any(row["split"]==split for row in lane_rows):
            raise TrainingExecutionError(f"MasterBot {target_masterbot} has no {split} examples")
    return object_path,lane_rows

def execute_job(job_path: str | Path, approval_id: str, output_root: str | Path,
                allow_model_download: bool=False) -> dict[str,Any]:
    job_path=Path(job_path)
    job=json.loads(job_path.read_text(encoding="utf-8"))
    object_path,rows=validate_job(job,approval_id)
    if allow_model_download and os.environ.get("DREAMCO_ALLOW_MODEL_DOWNLOAD")!="1":
        raise TrainingExecutionError("Set DREAMCO_ALLOW_MODEL_DOWNLOAD=1 to authorize base-model download")
    try:
        import torch
        from torch.utils.data import Dataset
        from transformers import AutoModelForCausalLM, AutoTokenizer, DataCollatorForLanguageModeling, Trainer, TrainingArguments
    except ImportError as exc:
        raise TrainingExecutionError("Install torch and transformers to execute SFT; install peft for LoRA") from exc
    cfg=job["training_config"]
    local_only=not allow_model_download
    tokenizer=AutoTokenizer.from_pretrained(job["model_id"],revision=job["base_model_revision"],local_files_only=local_only)
    if tokenizer.pad_token is None: tokenizer.pad_token=tokenizer.eos_token
    model=AutoModelForCausalLM.from_pretrained(job["model_id"],revision=job["base_model_revision"],local_files_only=local_only)
    if job["training_method"]=="lora":
        try:
            from peft import LoraConfig, get_peft_model
        except ImportError as exc:
            raise TrainingExecutionError("Install peft to execute LoRA training") from exc
        model=get_peft_model(model,LoraConfig(r=8,lora_alpha=16,lora_dropout=0.05,task_type="CAUSAL_LM"))
    class Rows(Dataset):
        def __init__(self, split):
            self.items=[]
            for row in rows:
                if row["split"]!=split: continue
                text=row.get("text") or f"### Instruction:\n{row['instruction']}\n### Response:\n{row['output']}"
                encoded=tokenizer(text,truncation=True,max_length=int(cfg["max_seq_length"]))
                self.items.append({"input_ids":encoded["input_ids"],"attention_mask":encoded["attention_mask"]})
        def __len__(self): return len(self.items)
        def __getitem__(self,index): return self.items[index]
    train_ds,validation_ds,test_ds=Rows("train"),Rows("validation"),Rows("test")
    if not len(train_ds) or not len(validation_ds) or not len(test_ds):
        raise TrainingExecutionError("All three data splits must contain tokenizable records")
    output=Path(output_root)/job["job_id"]
    output.mkdir(parents=True,exist_ok=True)
    args_kwargs={"output_dir":str(output/"trainer"),"max_steps":int(cfg["max_steps"]),
        "per_device_train_batch_size":int(cfg["per_device_train_batch_size"]),
        "gradient_accumulation_steps":int(cfg["gradient_accumulation_steps"]),
        "learning_rate":float(cfg["learning_rate"]),"seed":int(cfg["seed"]),
        "report_to":[],"save_strategy":"no","logging_steps":1}
    import inspect
    signature=inspect.signature(TrainingArguments)
    if "eval_strategy" in signature.parameters: args_kwargs["eval_strategy"]="steps"
    else: args_kwargs["evaluation_strategy"]="steps"
    args_kwargs["eval_steps"]=max(1,min(10,int(cfg["max_steps"])//5 or 1))
    trainer=Trainer(model=model,args=TrainingArguments(**args_kwargs),train_dataset=train_ds,
        eval_dataset=validation_ds,data_collator=DataCollatorForLanguageModeling(tokenizer=tokenizer,mlm=False))
    baseline_validation=trainer.evaluate(validation_ds,metric_key_prefix="baseline_validation")
    train_result=trainer.train()
    validation=trainer.evaluate(validation_ds,metric_key_prefix="validation")
    holdout=trainer.evaluate(test_ds,metric_key_prefix="holdout")
    model.save_pretrained(output/"model")
    tokenizer.save_pretrained(output/"model")
    artifact_dir=output/"model"
    artifact_files=[]
    for artifact in sorted(artifact_dir.rglob("*")):
        if artifact.is_symlink():
            raise TrainingExecutionError("Model artifact directory contains a symlink")
        if artifact.is_file():
            artifact_files.append({"path":str(artifact.relative_to(artifact_dir)),
                "sha256":hashlib.sha256(artifact.read_bytes()).hexdigest(),"bytes":artifact.stat().st_size})
    if not artifact_files:
        raise TrainingExecutionError("Training produced no checkpoint or tokenizer files")
    artifact_manifest_hash=hashlib.sha256(json.dumps(artifact_files,sort_keys=True).encode()).hexdigest()
    tested_commit=os.environ.get("GITHUB_SHA") or os.environ.get("DREAMCO_GIT_COMMIT")
    if tested_commit and not re.fullmatch(r"[0-9a-f]{40}",tested_commit):
        tested_commit=None
    result={"schema":"dreamco.model_training_result.v1","execution_status":"COMPLETED",
        "completed_at":datetime.now(timezone.utc).isoformat(),"job_id":job["job_id"],
        "masterbot_id":job["masterbot_id"],"model_id":job["model_id"],
        "base_model_revision":job["base_model_revision"],"tokenizer_revision":job["base_model_revision"],
        "model_license":job["model_license"],"model_license_status":job["model_license_status"],
        "model_license_evidence":job["model_license_evidence"],
        "dataset_id":job["dataset_id"],"dataset_version":job["dataset_version"],
        "dataset_sha256":job["dataset_sha256"],"split_manifest":job["split_manifest"],
        "training_method":job["training_method"],"global_step":train_result.global_step,
        "baseline_validation_metrics":baseline_validation,
        "train_metrics":train_result.metrics,"validation_metrics":validation,"holdout_metrics":holdout,
        "artifact_dir":str(artifact_dir),"checkpoint_sha256":artifact_manifest_hash,
        "checkpoint_files":artifact_files,"tested_commit_sha":tested_commit,
        "weights_trained":True,"production_promoted":False,
        "requires_independent_benchmark_and_review":True}
    (output/"checkpoint-manifest.json").write_text(json.dumps({
        "schema":"dreamco.checkpoint_manifest.v1","model_id":job["model_id"],
        "masterbot_id":job["masterbot_id"],"base_model_revision":job["base_model_revision"],
        "tokenizer_revision":job["base_model_revision"],"checkpoint_sha256":artifact_manifest_hash,
        "files":artifact_files},indent=2)+"\n",encoding="utf-8")
    (output/"training-result.json").write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    return result
