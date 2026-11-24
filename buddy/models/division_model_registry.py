"""Independent, versioned model identities for all canonical DreamCo divisions.

The registry describes isolated model artifacts and lifecycle contracts. It does
not claim that any model has been downloaded, trained, benchmarked, or deployed.
"""
from __future__ import annotations
import json,re
from pathlib import Path
from typing import Any

ROOT=Path(__file__).resolve().parents[2]
REGISTRY_PATH=ROOT/"config/masterbot-65-registry.json"
RESOURCE_MAP_PATH=ROOT/"config/generated/division-resource-readiness-map.json"
MODEL_VERSION="0.1.0"

def _slug(value:str)->str:
    return re.sub(r"[^a-z0-9]+","-",value.casefold()).strip("-")

def load_division_model_registry()->dict[str,Any]:
    source=json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    divisions=source.get("divisions",[])
    if source.get("canonical_count")!=65 or len(divisions)!=65:
        raise ValueError("canonical MasterBot registry must contain exactly 65 divisions")
    ids=[int(x["id"]) for x in divisions]
    names=[str(x["name"]) for x in divisions]
    if sorted(ids)!=list(range(1,66)) or len(set(names))!=65:
        raise ValueError("division IDs must be 1..65 and names must be unique")
    resources=json.loads(RESOURCE_MAP_PATH.read_text(encoding="utf-8"))
    routes={int(x["masterbot_id"]):x for x in resources.get("routes",[])}
    if len(routes)!=65:
        raise ValueError("resource readiness map must contain 65 unique MasterBot routes")
    models=[]
    for division in sorted(divisions,key=lambda x:int(x["id"])):
        division_id=int(division["id"])
        slug=_slug(division["name"])
        stem=f"masterbot-{division_id:03d}-{slug}"
        root=f"artifacts/division-models/{stem}/v{MODEL_VERSION}"
        route=routes[division_id]
        models.append({
            "masterbot_id":division_id,
            "division_name":division["name"],
            "division_slug":slug,
            "model_name":f"dreamco/{slug}-mini",
            "model_version":MODEL_VERSION,
            "model_family":"division_specialist_causal_lm",
            "model_status":"SPECIFIED_NOT_TRAINED",
            "trainable":True,
            "training_methods":["sft","lora"],
            "base_model":{"model_id":None,"immutable_revision":None,"license_status":"UNVERIFIED","selection_requires_owner_approval":True},
            "tokenizer":{"strategy":"division_owned_snapshot_of_pinned_base_tokenizer","base_tokenizer_id":None,"immutable_revision":None,"artifact_path":f"{root}/tokenizer","shared_tokenizer_runtime":False},
            "artifacts":{"root":root,"weights_path":f"{root}/weights","checkpoints_path":f"{root}/checkpoints","training_evidence_path":f"{root}/training-evidence.json","benchmark_evidence_path":f"{root}/benchmark-evidence.json","model_card_path":f"{root}/MODEL_CARD.json"},
            "data":{"database_schema":f"dreamco_division_{division_id:03d}","resource_bundle_id":route["resource_bundle_id"],"dataset_owner_masterbot_id":division_id,"holdout_isolation_required":True},
            "teacher_policy":{"teacher_selection":"buddy_coordinator_routes_only_to_explicitly_approved_provider_or_pinned_local_teacher","provider_call_requires_per_request_approval":True,"teacher_output_rights_review_required":True,"teacher_outputs_are_not_ground_truth":True},
            "benchmark_policy":{"baseline_required":True,"division_domain_suite_required":True,"general_capability_suite_required":True,"safety_regression_required":True,"private_holdout_never_trains":True,"promotion_requires_independent_review":True},
            "runtime_policy":{"endpoint_identity":f"division-{division_id:03d}","production_serving_enabled":False,"rollback_pointer_required":True,"health_evidence_required":True},
            "readiness":{"infrastructure":"REQUIREMENTS_DEFINED_NOT_PROVISIONED","dataset":"NOT_INGESTED","training":"NOT_RUN","benchmark":"NOT_RUN","runtime":"NOT_DEPLOYED"}
        })
    payload={"schema":"dreamco.independent_division_model_registry.v1","registry_version":"1.0.0",
        "canonical_division_count":65,"model_version_default":MODEL_VERSION,
        "model_identity_policy":"Every MasterBot has its own model name, version, weights, checkpoint lineage, tokenizer snapshot, dataset lane, benchmark record and runtime identity. Shared physical infrastructure/base weights are allowed; trained division artifacts are not shared across division paths.",
        "promotion_rule":"No model may be marked trained, benchmarked, certified or production-ready without immutable artifact hashes and independently verifiable evidence for the corresponding lifecycle stage.",
        "divisions":models}
    validate_division_model_registry(payload)
    return payload

def validate_division_model_registry(payload:dict[str,Any])->None:
    models=payload.get("divisions",[])
    if payload.get("canonical_division_count")!=65 or len(models)!=65:
        raise ValueError("expected exactly 65 independent division model identities")
    for field in ("model_name",):
        values=[x[field] for x in models]
        if len(set(values))!=65:
            raise ValueError(f"{field} must be unique across division models")
    for key in ("weights_path","checkpoints_path","tokenizer"):
        values=[x["artifacts"]["weights_path"] if key=="weights_path" else x["artifacts"]["checkpoints_path"] if key=="checkpoints_path" else x["tokenizer"]["artifact_path"] for x in models]
        if len(set(values))!=65:
            raise ValueError(f"{key} paths must be unique across divisions")
    for model in models:
        if not str(model.get("model_version","")).strip():
            raise ValueError("every division model must have its own explicit version")
        if model["model_status"]!="SPECIFIED_NOT_TRAINED" or model["readiness"]["training"]!="NOT_RUN":
            raise ValueError("registry generation must not fabricate training evidence")
        if model["base_model"]["immutable_revision"] is not None:
            if not re.fullmatch(r"[0-9a-f]{40}",str(model["base_model"]["immutable_revision"])):
                raise ValueError("base model revisions must be immutable commit SHAs")

def get_division_model_identity(masterbot_id:int)->dict[str,Any]:
    payload=load_division_model_registry()
    for model in payload["divisions"]:
        if model["masterbot_id"]==int(masterbot_id):
            return model
    raise KeyError(f"unknown MasterBot ID: {masterbot_id}")
