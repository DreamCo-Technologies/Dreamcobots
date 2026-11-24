"""Explicitly execute one approved division training job and package immutable evidence."""
from __future__ import annotations
import argparse
import hashlib
import json
import os
import re
import shutil
from pathlib import Path
from typing import Any
from buddy.datasets.transformers_runner import execute_job, TrainingExecutionError

class TrainingWorkerError(RuntimeError):
    """A training job was not eligible for execution or evidence packaging."""

def _hash_file(path:Path)->str:
    digest=hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda:stream.read(1024*1024),b""):
            digest.update(chunk)
    return digest.hexdigest()

def _verify_files(root:Path,files:list[dict[str,Any]],require_nonempty:bool=True)->None:
    if require_nonempty and not files: raise TrainingWorkerError("training artifact file manifest is empty")
    for item in files:
        relative=Path(str(item.get("path","")))
        if relative.is_absolute() or not relative.parts or ".." in relative.parts:
            raise TrainingWorkerError("unsafe training artifact path")
        path=(root/relative).resolve()
        if root.resolve() not in path.parents or not path.is_file():
            raise TrainingWorkerError("training artifact file is missing or outside its directory")
        if _hash_file(path)!=item.get("sha256") or path.stat().st_size!=item.get("bytes"):
            raise TrainingWorkerError("training artifact hash or size mismatch")

def package_training_evidence(result:dict[str,Any],evidence_root:str|Path)->dict[str,Any]:
    if result.get("execution_status")!="COMPLETED" or result.get("weights_trained") is not True or result.get("production_promoted") is not False:
        raise TrainingWorkerError("only a completed, non-promoted training result can be packaged")
    if not re.fullmatch(r"[0-9a-f]{40}",str(result.get("tested_commit_sha",""))):
        raise TrainingWorkerError("training result is missing immutable tested commit SHA")
    if not re.fullmatch(r"[0-9a-f]{64}",str(result.get("checkpoint_sha256",""))):
        raise TrainingWorkerError("training result is missing checkpoint manifest digest")
    expected_checkpoint_digest=hashlib.sha256(
        json.dumps(result.get("checkpoint_files") or [],sort_keys=True).encode("utf-8")).hexdigest()
    if expected_checkpoint_digest!=result["checkpoint_sha256"]:
        raise TrainingWorkerError("training checkpoint manifest digest does not match the file manifest")
    source_paths=result.get("artifact_paths") or {}
    root=Path(evidence_root).resolve()
    root.mkdir(parents=True,exist_ok=True)
    division_id=int(result["masterbot_id"])
    destinations={
        "weights":root/"checkpoints"/f"division-{division_id:03d}"/"weights",
        "checkpoints":root/"checkpoints"/f"division-{division_id:03d}"/"training-checkpoints",
        "tokenizer":root/"checkpoints"/f"division-{division_id:03d}"/"tokenizer"
    }
    expected={
        "weights":result.get("checkpoint_files") or [],
        "checkpoints":(result.get("artifact_hashes") or {}).get("checkpoints") or [],
        "tokenizer":(result.get("artifact_hashes") or {}).get("tokenizer") or []
    }
    for name,destination in destinations.items():
        source=Path(str(source_paths.get(name,""))).resolve()
        if not source.is_dir():
            raise TrainingWorkerError(f"{name} source directory is missing")
        _verify_files(source,expected[name],require_nonempty=name!="checkpoints")
        if destination.exists():
            raise TrainingWorkerError(f"evidence destination already exists: {name}")
        destination.parent.mkdir(parents=True,exist_ok=True)
        shutil.copytree(source,destination)
        _verify_files(destination,expected[name],require_nonempty=name!="checkpoints")
    relative_weights=str(destinations["weights"].relative_to(root))
    evidence_result=dict(result)
    evidence_result["checkpoint_root"]=relative_weights
    evidence_result["artifact_paths"]={name:str(path.relative_to(root)) for name,path in destinations.items()}
    evidence_result["checkpoint_files"]=expected["weights"]
    evidence_result["checkpoint_sha256"]=hashlib.sha256(
        json.dumps(expected["weights"],sort_keys=True).encode("utf-8")).hexdigest()
    training_path=root/"training-result.json"
    training_path.write_text(json.dumps(evidence_result,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    training_sha=_hash_file(training_path)
    fragment={
        "schema":"dreamco.division_training_evidence_fragment.v1",
        "division":{"masterbot_id":division_id,"division_model_id":f"DCM-{division_id:03d}",
            "model_id":result["model_id"],"version":result["model_version"]},
        "tested_commit_sha":result["tested_commit_sha"],
        "checkpoint_root":relative_weights,
        "evidence":{"training_result":{"path":"training-result.json","sha256":training_sha}},
        "production_promotion_performed":False
    }
    fragment_path=root/"training-evidence-fragment.json"
    fragment_path.write_text(json.dumps(fragment,indent=2)+"\n",encoding="utf-8")
    return {"status":"TRAINED_PENDING_BENCHMARK_AND_REVIEW","masterbot_id":division_id,
        "model_id":result["model_id"],"model_version":result["model_version"],
        "tested_commit_sha":result["tested_commit_sha"],"weights_trained":True,
        "checkpoint_sha256":evidence_result["checkpoint_sha256"],
        "training_result_path":str(training_path),"training_result_sha256":training_sha,
        "evidence_fragment_path":str(fragment_path),"checkpoint_root":relative_weights,
        "production_promoted":False}

def execute_approved_training_job(job_manifest:str|Path,approval_id:str,evidence_root:str|Path,
                                  allow_model_download:bool=False)->dict[str,Any]:
    if os.environ.get("DREAMCO_ALLOW_TRAINING_EXECUTION")!="1":
        raise TrainingWorkerError("set DREAMCO_ALLOW_TRAINING_EXECUTION=1 after compute approval to execute training")
    job=json.loads(Path(job_manifest).read_text(encoding="utf-8"))
    if not approval_id or approval_id!=job.get("compute_approval_id"):
        raise TrainingWorkerError("compute approval ID does not match the job manifest")
    output_root=Path(evidence_root).resolve().parent/"training-run-output"
    try:
        result=execute_job(job_manifest,approval_id,output_root,allow_model_download=allow_model_download)
    except TrainingExecutionError as exc:
        raise TrainingWorkerError(str(exc)) from None
    return package_training_evidence(result,evidence_root)

def main()->int:
    parser=argparse.ArgumentParser()
    parser.add_argument("--job-manifest",required=True)
    parser.add_argument("--approval-id",required=True)
    parser.add_argument("--evidence-root",default="artifacts/training-evidence")
    parser.add_argument("--allow-model-download",action="store_true")
    args=parser.parse_args()
    result=execute_approved_training_job(args.job_manifest,args.approval_id,args.evidence_root,args.allow_model_download)
    print(json.dumps(result,indent=2))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
