"""Create benchmark jobs against isolated evaluation-only holdout datasets."""
from __future__ import annotations
import hashlib,json,re,uuid
from datetime import datetime,timezone
from pathlib import Path
from typing import Any
from .hub import DatasetHub,DatasetPolicyError,sha256_file

def create_private_holdout_job(hub:DatasetHub,dataset_id:str,masterbot_id:int,
                               candidates:list[dict[str,Any]],compute_approval_id:str,
                               output_dir:str|Path="artifacts/private-holdout-jobs",
                               min_exact_match:float=0.70,min_token_f1:float=0.70,
                               max_regression:float=0.02)->dict[str,Any]:
    card=hub.get(dataset_id)
    if not card or card.get("data_plane")!="evaluation_only_holdout" or card.get("holdout") is not True:
        raise DatasetPolicyError("A separately registered evaluation-only holdout is required")
    if card.get("training_approved") is not False or card.get("evaluation_approved") is not True or card.get("rights_status")!="VERIFIED":
        raise DatasetPolicyError("Holdout must be evaluation-approved and explicitly excluded from training")
    if card.get("primary_masterbot_id")!=masterbot_id:
        raise DatasetPolicyError("Holdout belongs to a different MasterBot lane")
    if not compute_approval_id.strip():
        raise DatasetPolicyError("Private benchmark compute approval ID is required")
    if not 0<=min_exact_match<=1 or not 0<=min_token_f1<=1 or not 0<=max_regression<=1:
        raise DatasetPolicyError("Benchmark thresholds must be between zero and one")
    if len(candidates)<2 or sum(1 for c in candidates if c.get("role")=="baseline")!=1:
        raise DatasetPolicyError("Provide exactly one baseline and at least one candidate")
    clean=[]
    for item in candidates:
        if not item.get("model_id") or not re.fullmatch(r"[0-9a-f]{40}",str(item.get("revision",""))):
            raise DatasetPolicyError("Every candidate requires a model ID and immutable revision")
        if item.get("license_status")!="VERIFIED" or not item.get("license") or not str(item.get("license_url","")).startswith("https://") or not item.get("license_evidence"):
            raise DatasetPolicyError("Every model requires verified license evidence")
        if item.get("role") not in {"baseline","trained_candidate","open_weight_alternative"}:
            raise DatasetPolicyError("Unsupported benchmark candidate role")
        clean.append({k:item[k] for k in ("model_id","revision","license","license_url","license_status","license_evidence","role")})
    object_path=(hub.home/card["object_path"]).resolve()
    if hub.home.resolve() not in object_path.parents or not object_path.is_file():
        raise DatasetPolicyError("Private holdout object is missing or outside its hub")
    digest=sha256_file(object_path)
    if digest!=card.get("content_sha256"):
        raise DatasetPolicyError("Private holdout object hash mismatch")
    split=card.get("split_manifest") or {}
    if not re.fullmatch(r"[0-9a-f]{64}",str(split.get("test_sha256",""))):
        raise DatasetPolicyError("Private holdout test split hash is missing")
    payload={"schema":"dreamco.private_holdout_benchmark_job.v1",
        "job_id":"holdout-bench-"+uuid.uuid4().hex[:16],"created_at":datetime.now(timezone.utc).isoformat(),
        "dataset_id":dataset_id,"dataset_version":card["version"],"dataset_sha256":digest,
        "dataset_card_sha256":hashlib.sha256(json.dumps(card,sort_keys=True).encode()).hexdigest(),
        "dataset_hub_path":str(hub.home.resolve()),"dataset_object_path":card["object_path"],
        "split_manifest":split,"masterbot_id":masterbot_id,"compute_approval_id":compute_approval_id,
        "candidates":clean,"thresholds":{"min_exact_match":min_exact_match,"min_token_f1":min_token_f1,
        "max_regression":max_regression},"metric":["exact_match","token_f1"],"private_holdout":True,
        "test_split_only":True,"status":"READY_FOR_EXPLICIT_BENCHMARK",
        "execution_status":"NOT_EXECUTED","training_started":False,"production_promotion":False}
    root=Path(output_dir);root.mkdir(parents=True,exist_ok=True)
    path=root/f"{payload['job_id']}.json"
    path.write_text(json.dumps(payload,indent=2)+"\n",encoding="utf-8")
    payload["manifest_path"]=str(path)
    return payload
