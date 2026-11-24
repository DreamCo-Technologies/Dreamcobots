"""Explicit SFT/LoRA runner with division-isolated weights, checkpoints and tokenizer snapshots.

No network download or GPU use occurs unless the operator passes the explicit
execution flag, a matching compute approval ID, and enables model download.
"""
from __future__ import annotations
import hashlib
import json
import os
import re
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

def _hash_tree(root:Path)->list[dict[str,str]]:
    files=[]
    if not root.exists(): return files
    for path in sorted(x for x in root.rglob("*") if x.is_file()):
        digest=hashlib.sha256(path.read_bytes()).hexdigest()
        files.append({"path":path.relative_to(root).as_posix(),"sha256":digest,"bytes":path.stat().st_size})
    return files

def _directory_sha256(root:Path)->str:
    digest=hashlib.sha256()
    for item in _hash_tree(root):
        digest.update(item["path"].encode("utf-8")+b"\\0")
        digest.update(bytes.fromhex(item["sha256"]))
    return digest.hexdigest()

def validate_job(job: dict, approval_id: str) -> tuple[Path,list[dict]]:
    if job.get("schema")!="dreamco.model_training_job.v1" or job.get("execution_status")!="NOT_EXECUTED":
        raise TrainingExecutionError("Invalid or already executed job manifest")
    if not approval_id or approval_id != job.get("compute_approval_id"):
        raise TrainingExecutionError("Compute approval ID does not match the job")
    if not re.fullmatch(r"[0-9a-f]{40}",str(job.get("base_model_revision",""))):
        raise TrainingExecutionError("Base model revision is not immutable")
    tokenizer_revision=job.get("tokenizer_revision") or job.get("base_model_revision")
    if not re.fullmatch(r"[0-9a-f]{40}",str(tokenizer_revision)):
        raise TrainingExecutionError("Tokenizer revision is not immutable")
    tested_commit_sha=os.environ.get("GITHUB_SHA") or job.get("tested_commit_sha","")
    if not re.fullmatch(r"[0-9a-f]{40}",str(tested_commit_sha)):
        raise TrainingExecutionError("Training requires the immutable tested commit SHA from GITHUB_SHA or the job manifest")
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
    identity=job.get("division_model")
    if identity:
        if int(job.get("masterbot_id",-1))<1 or not re.fullmatch(r"dreamco/[a-z0-9-]+-mini",str(identity.get("model_name",""))):
            raise TrainingExecutionError("Division model identity is invalid")
        if not identity.get("model_version") or not identity.get("artifact_root"):
            raise TrainingExecutionError("Division model version and artifact namespace are required")
        if not identity.get("database_schema")==f"dreamco_division_{target_masterbot:03d}":
            raise TrainingExecutionError("Division database namespace does not match MasterBot ID")
    return object_path,lane_rows

def execute_job(job_path: str | Path, approval_id: str, output_root: str | Path,
                allow_model_download: bool=False) -> dict[str,Any]:
    job_path=Path(job_path)
    job=json.loads(job_path.read_text(encoding="utf-8"))
    object_path,rows=validate_job(job,approval_id)
    tokenizer_revision=job.get("tokenizer_revision") or job.get("base_model_revision")
    tested_commit_sha=os.environ.get("GITHUB_SHA") or job.get("tested_commit_sha","")
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
    tokenizer=AutoTokenizer.from_pretrained(job["model_id"],revision=tokenizer_revision,local_files_only=local_only)
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
    identity=job.get("division_model") or {"division_slug":"legacy","model_version":"0.0.0"}
    output=Path(output_root)/f"masterbot-{int(job['masterbot_id']):03d}-{identity['division_slug']}"/f"v{identity['model_version']}"/job["job_id"]
    checkpoint_dir=output/"checkpoints"
    weights_dir=output/"weights"
    tokenizer_dir=output/"tokenizer"
    checkpoint_dir.mkdir(parents=True,exist_ok=True)
    weights_dir.mkdir(parents=True,exist_ok=True)
    tokenizer_dir.mkdir(parents=True,exist_ok=True)
    checkpoint_interval=max(1,min(10,int(cfg["max_steps"])//5 or 1))
    args_kwargs={"output_dir":str(checkpoint_dir),"max_steps":int(cfg["max_steps"]),
        "per_device_train_batch_size":int(cfg["per_device_train_batch_size"]),
        "gradient_accumulation_steps":int(cfg["gradient_accumulation_steps"]),
        "learning_rate":float(cfg["learning_rate"]),"seed":int(cfg["seed"]),
        "report_to":[],"save_strategy":"steps","save_steps":checkpoint_interval,
        "save_total_limit":3,"logging_steps":1,"load_best_model_at_end":True,
        "metric_for_best_model":"eval_loss","greater_is_better":False}
    import inspect
    signature=inspect.signature(TrainingArguments)
    if "eval_strategy" in signature.parameters: args_kwargs["eval_strategy"]="steps"
    else: args_kwargs["evaluation_strategy"]="steps"
    args_kwargs["eval_steps"]=checkpoint_interval
    trainer=Trainer(model=model,args=TrainingArguments(**args_kwargs),train_dataset=train_ds,
        eval_dataset=validation_ds,data_collator=DataCollatorForLanguageModeling(tokenizer=tokenizer,mlm=False))
    baseline_validation=trainer.evaluate(validation_ds,metric_key_prefix="baseline_validation")
    train_result=trainer.train()
    validation=trainer.evaluate(validation_ds,metric_key_prefix="validation")
    holdout=trainer.evaluate(test_ds,metric_key_prefix="holdout")
    trainer.model.save_pretrained(weights_dir)
    tokenizer.save_pretrained(tokenizer_dir)
    training_checkpoint_files=_hash_tree(checkpoint_dir)
    weight_files=_hash_tree(weights_dir)
    tokenizer_files=_hash_tree(tokenizer_dir)
    checkpoint_files=weight_files
    checkpoint_sha256=hashlib.sha256(json.dumps(checkpoint_files,sort_keys=True).encode("utf-8")).hexdigest()
    result={"schema":"dreamco.model_training_result.v3","job_id":job["job_id"],
        "execution_status":"COMPLETED","masterbot_id":int(job["masterbot_id"]),"division_model":identity,
        "model_id":identity.get("model_name") if identity else job["model_id"],
        "model_version":identity.get("model_version") if identity else "0.0.0",
        "base_model_id":job["model_id"],"base_model_revision":job["base_model_revision"],
        "tokenizer_revision":tokenizer_revision,"tested_commit_sha":tested_commit_sha,
        "compute_approval_id":job.get("compute_approval_id"),
        "dataset_id":job["dataset_id"],"dataset_version":job.get("dataset_version"),
        "dataset_sha256":job["dataset_sha256"],
        "split_manifest":job["split_manifest"],"training_method":job["training_method"],
        "training_config":cfg,"global_step":train_result.global_step,
        "baseline_validation_metrics":baseline_validation,"train_metrics":train_result.metrics,
        "validation_metrics":validation,"holdout_metrics":holdout,
        "artifact_paths":{"weights":str(weights_dir),"checkpoints":str(checkpoint_dir),"tokenizer":str(tokenizer_dir)},
        "artifact_hashes":{"weights":weight_files,"checkpoints":training_checkpoint_files,"tokenizer":tokenizer_files,
            "weights_directory_sha256":_directory_sha256(weights_dir),
            "checkpoints_directory_sha256":_directory_sha256(checkpoint_dir),
            "tokenizer_directory_sha256":_directory_sha256(tokenizer_dir)},
        "checkpoint_root":str(weights_dir),"checkpoint_files":checkpoint_files,
        "checkpoint_sha256":checkpoint_sha256,
        "training_config_sha256":hashlib.sha256(json.dumps(cfg,sort_keys=True).encode("utf-8")).hexdigest(),
        "weights_trained":True,"production_promoted":False,
        "requires_independent_benchmark_and_review":True}
    (output/"training-result.json").write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    return result
