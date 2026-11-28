"""Stable train/holdout partitioning and evaluation recipe metadata."""
from __future__ import annotations
import hashlib, json
def bucket(task_id:str)->int:
    if not isinstance(task_id,str) or not task_id.strip(): raise ValueError("task_id is required")
    return int(hashlib.sha256(task_id.encode()).hexdigest()[:16],16)%100
def split_tasks(tasks:list[dict],holdout_percent:int=20)->dict:
    if not 1<=holdout_percent<=49: raise ValueError("holdout_percent must be 1..49")
    ids=[x.get("task_id") for x in tasks]
    if any(not isinstance(x,str) or not x for x in ids) or len(set(ids))!=len(ids): raise ValueError("task_id values must be unique and non-empty")
    train,holdout=[],[]
    for item in tasks:
        (holdout if bucket(item["task_id"])<holdout_percent else train).append(item)
    return {"schema":"dreamco.deterministic_task_split.v1","algorithm":"sha256(task_id)[:16] mod 100",
      "holdout_percent":holdout_percent,"train":train,"holdout":holdout,
      "train_ids":[x["task_id"] for x in train],"holdout_ids":[x["task_id"] for x in holdout],
      "holdout_access":"evaluation_only","split_digest":hashlib.sha256("\n".join(sorted(ids)).encode()).hexdigest()}
def evaluation_recipe(base_model:str,recipe:dict,task_manifest_sha256:str)->dict:
    if not base_model or not recipe or len(task_manifest_sha256)!=64: raise ValueError("pinned model, recipe, and manifest SHA-256 are required")
    return {"schema":"dreamco.evaluation_recipe.v1","base_model":base_model,"recipe":recipe,
      "task_manifest_sha256":task_manifest_sha256,"seed":20261127,
      "metrics":["accuracy","pass_rate","safety_gate_pass_rate","latency_ms"],
      "truth_boundary":"A recipe is not a training run; only checkpoint and evaluation artifacts establish a result."}
