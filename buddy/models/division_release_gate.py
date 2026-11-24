"""Evidence-only release gate for independent DreamCo division models.

The gate verifies immutable evidence artifacts and returns eligibility for
independent review. It never deploys, promotes, or changes model weights.
"""
from __future__ import annotations
import hashlib,json,re
from pathlib import Path
from typing import Any

SHA=re.compile(r"^[0-9a-f]{64}$")
COMMIT=re.compile(r"^[0-9a-f]{40}$")
SCHEMA=re.compile(r"^dreamco_division_([0-9]{3})$")

class DivisionReleaseEvidenceError(ValueError):
    """Invalid evidence bundle or unsafe evidence path."""

def _sha(path:Path)->str:
    digest=hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda:stream.read(1024*1024),b""): digest.update(chunk)
    return digest.hexdigest()

def _load_ref(root:Path,ref:dict,label:str,reasons:list[str])->dict[str,Any]|None:
    if not isinstance(ref,dict):
        reasons.append(f"{label}: evidence reference missing")
        return None
    relative=Path(str(ref.get("path","")))
    if relative.is_absolute() or not relative.parts or ".." in relative.parts:
        reasons.append(f"{label}: evidence path must be a safe relative path")
        return None
    path=(root/relative).resolve()
    if root not in path.parents or not path.is_file():
        reasons.append(f"{label}: evidence file missing or outside evidence root")
        return None
    expected=str(ref.get("sha256",""))
    if not SHA.fullmatch(expected) or _sha(path)!=expected:
        reasons.append(f"{label}: evidence SHA-256 mismatch")
        return None
    try:
        payload=json.loads(path.read_text(encoding="utf-8"))
    except (UnicodeDecodeError,json.JSONDecodeError):
        reasons.append(f"{label}: evidence is not valid JSON")
        return None
    if not isinstance(payload,dict):
        reasons.append(f"{label}: evidence JSON must be an object")
        return None
    return payload

def validate_division_release(bundle_path:str|Path,evidence_root:str|Path|None=None)->dict[str,Any]:
    bundle_file=Path(bundle_path).resolve()
    root=Path(evidence_root).resolve() if evidence_root else bundle_file.parent
    if root not in bundle_file.parents or not bundle_file.is_file():
        raise DivisionReleaseEvidenceError("bundle must be a file inside the evidence root")
    bundle=json.loads(bundle_file.read_text(encoding="utf-8"))
    if bundle.get("schema")!="dreamco.division_release_evidence.v1":
        raise DivisionReleaseEvidenceError("unsupported division release evidence schema")
    division=bundle.get("division") or {}
    masterbot_id=division.get("masterbot_id")
    if isinstance(masterbot_id,bool) or not isinstance(masterbot_id,int) or not 1<=masterbot_id<=65:
        raise DivisionReleaseEvidenceError("masterbot_id must be a canonical integer from 1 through 65")
    if division.get("division_model_id")!=f"DCM-{masterbot_id:03d}":
        raise DivisionReleaseEvidenceError("division_model_id does not match canonical MasterBot ID")
    if not str(division.get("model_id","")).strip() or not str(division.get("version","")).strip():
        raise DivisionReleaseEvidenceError("model_id and model version are required")
    tested_commit=str(bundle.get("tested_commit_sha",""))
    if not COMMIT.fullmatch(tested_commit):
        raise DivisionReleaseEvidenceError("tested_commit_sha must be a full immutable Git commit SHA")

    reasons=[]
    refs=bundle.get("evidence") or {}
    labels=("postgres_probe","dataset_catalog","object_storage","provider_health",
            "dataset_card","training_result","benchmark_report","runtime_deployment")
    docs={name:_load_ref(root,refs.get(name),name,reasons) for name in labels}
    postgres=docs["postgres_probe"] or {}
    if postgres.get("status")!="CONNECTED_SCHEMAS_VERIFIED" or postgres.get("expected_division_namespaces")!=65 or postgres.get("verified_division_namespaces")!=65 or postgres.get("missing_division_namespaces")!=[]:
        reasons.append("PostgreSQL: all 65 division namespaces must be verified by a read-only probe")
    catalog=docs["dataset_catalog"] or {}
    expected_schema=f"dreamco_division_{masterbot_id:03d}"
    if catalog.get("status")!="PERSISTED" or catalog.get("masterbot_id")!=masterbot_id or catalog.get("schema")!=expected_schema:
        reasons.append("dataset catalog: this division's manifest must be persisted in its own namespace")
    storage=docs["object_storage"] or {}
    if not (storage.get("status")=="HEALTHY" and storage.get("encryption_at_rest") is True
            and storage.get("versioning_enabled") is True and storage.get("backup_restore_test")=="PASS"
            and isinstance(storage.get("retention_days"),int) and storage.get("retention_days",0)>0):
        reasons.append("object storage: health, encryption, versioning, tested restore, and retention evidence are required")
    provider=docs["provider_health"] or {}
    if not (provider.get("status")=="HEALTHY" and provider.get("live_smoke_test") is True
            and provider.get("provider_id") and provider.get("model_id") and provider.get("request_id")):
        reasons.append("model serving: a successful live provider smoke test with request evidence is required")

    dataset=docs["dataset_card"] or {}
    split=dataset.get("split_manifest") or {}
    if not (dataset.get("training_approved") is True and dataset.get("rights_status")=="VERIFIED"
            and dataset.get("holdout") is not True and dataset.get("primary_masterbot_id")==masterbot_id
            and all(SHA.fullmatch(str(split.get(k,""))) for k in ("train_sha256","validation_sha256","test_sha256"))):
        reasons.append("dataset: verified rights, division ownership, training approval, and pinned splits are required")

    training=docs["training_result"] or {}
    checkpoint_sha=str(training.get("checkpoint_sha256",""))
    if not (training.get("execution_status")=="COMPLETED" and training.get("weights_trained") is True
            and training.get("production_promoted") is False and training.get("masterbot_id")==masterbot_id
            and training.get("model_id")==division.get("model_id")
            and training.get("dataset_id")==dataset.get("dataset_id")
            and training.get("dataset_sha256")==dataset.get("content_sha256")
            and training.get("split_manifest")==split
            and training.get("tokenizer_revision") and COMMIT.fullmatch(str(training.get("base_model_revision","")))
            and SHA.fullmatch(checkpoint_sha) and training.get("tested_commit_sha")==tested_commit):
        reasons.append("training: completed run, pinned base/tokenizer, matching dataset, checkpoint hash, and tested commit are required")
    checkpoint_root_value=bundle.get("checkpoint_root")
    checkpoint_files=training.get("checkpoint_files")
    if not isinstance(checkpoint_files,list) or not checkpoint_files or not checkpoint_root_value:
        reasons.append("training: checkpoint file manifest and copied checkpoint directory are required")
    else:
        cp_root=Path(str(checkpoint_root_value))
        if cp_root.is_absolute() or ".." in cp_root.parts:
            reasons.append("training: checkpoint directory must be relative to evidence root")
        else:
            cp_dir=(root/cp_root).resolve()
            if root not in cp_dir.parents or not cp_dir.is_dir():
                reasons.append("training: checkpoint directory is missing or outside evidence root")
            else:
                observed=[]
                for item in checkpoint_files:
                    rel=Path(str(item.get("path","")))
                    if rel.is_absolute() or not rel.parts or ".." in rel.parts:
                        reasons.append("training: unsafe checkpoint file path")
                        continue
                    file=(cp_dir/rel).resolve()
                    if cp_dir not in file.parents or not file.is_file():
                        reasons.append("training: checkpoint file missing")
                        continue
                    digest=_sha(file)
                    if digest!=item.get("sha256") or file.stat().st_size!=item.get("bytes"):
                        reasons.append("training: checkpoint file hash/size mismatch")
                    observed.append({"path":str(rel),"sha256":digest,"bytes":file.stat().st_size})
                computed=hashlib.sha256(json.dumps(observed,sort_keys=True).encode()).hexdigest()
                if computed!=checkpoint_sha:
                    reasons.append("training: checkpoint manifest digest mismatch")

    benchmark=docs["benchmark_report"] or {}
    if not (benchmark.get("dataset_id")==dataset.get("dataset_id")
            and benchmark.get("dataset_sha256")==dataset.get("content_sha256")
            and benchmark.get("model_id")==division.get("model_id")
            and benchmark.get("checkpoint_sha256")==checkpoint_sha
            and benchmark.get("tested_commit_sha")==tested_commit
            and benchmark.get("domain_benchmark_status")=="PASS"
            and benchmark.get("general_regression_status")=="PASS"
            and benchmark.get("private_holdout_status")=="PASS"
            and benchmark.get("safety_status")=="PASS"
            and benchmark.get("test_split_used_for_training") is False):
        reasons.append("benchmarks: domain, general regression, private holdout, and safety must all pass on this exact checkpoint")
    performance=benchmark.get("performance_profile") or {}
    for key in ("latency_p95_ms","tokens_per_second","peak_memory_bytes","cost_per_1k_tokens_usd"):
        value=performance.get(key)
        if not isinstance(value,(int,float)) or isinstance(value,bool) or value<0:
            reasons.append(f"benchmarks: performance profile missing valid {key}")
    runtime=docs["runtime_deployment"] or {}
    if not (runtime.get("status")=="HEALTHY" and str(runtime.get("endpoint","")).startswith("https://")
            and runtime.get("deployment_revision") and runtime.get("model_id")==division.get("model_id")
            and runtime.get("checkpoint_sha256")==checkpoint_sha and runtime.get("tested_commit_sha")==tested_commit
            and runtime.get("smoke_test")=="PASS" and runtime.get("rollback_target")):
        reasons.append("runtime: healthy HTTPS deployment, matching checkpoint/commit, smoke test, and rollback target are required")
    approval=bundle.get("independent_review") or {}
    if not (str(approval.get("reviewer_id","")).strip() and str(approval.get("approval_id","")).strip()
            and approval.get("approved") is True):
        reasons.append("promotion: independent reviewer approval evidence is required")

    return {"schema":"dreamco.division_release_gate_result.v1",
        "status":"READY_FOR_INDEPENDENT_REVIEW" if not reasons else "BLOCKED",
        "masterbot_id":masterbot_id,"division_model_id":division["division_model_id"],
        "model_id":division["model_id"],"model_version":division["version"],
        "tested_commit_sha":tested_commit,"blockers":reasons,
        "evidence_refs_verified":sum(1 for value in docs.values() if value is not None),
        "production_promotion_performed":False,
        "note":"Passing this gate only makes a release eligible for independent review; it never deploys or promotes weights."}
