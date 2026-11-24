"""Policy-only resource planner for per-division teacher/model selection.

This module creates an auditable route plan; it does not invoke external providers.
"""
from __future__ import annotations
import json
from pathlib import Path
from typing import Any

ROOT=Path(__file__).resolve().parents[2]
RESOURCE_MAP=ROOT/"config/generated/division-resource-readiness-map.json"
MODEL_ROUTER=ROOT/"config/buddy-model-router.json"

TASK_PACKS={
 "chat":"pack.instruct","instruction":"pack.instruct","coding":"pack.code","software":"pack.code",
 "reasoning":"pack.reason","question_answering":"pack.reason","embedding":"pack.embed",
 "retrieval":"pack.embed","reranking":"pack.rerank","vision":"pack.vision","image":"pack.vision",
 "speech":"pack.speech","audio":"pack.speech","translation":"pack.translate","summarization":"pack.summarize",
 "safety":"pack.safety"
}
SENSITIVE_CLASSES={"customer_private","personal_data","sensitive","regulated","confidential"}

def load_resource_routes()->dict[int,dict[str,Any]]:
    payload=json.loads(RESOURCE_MAP.read_text(encoding="utf-8"))
    if payload.get("status")!="requirements_defined_not_provisioned":
        raise ValueError("resource map must preserve honest readiness status")
    routes=payload.get("routes",[])
    indexed={int(row["masterbot_id"]):row for row in routes}
    if len(indexed)!=65:
        raise ValueError("expected exactly 65 unique division resource routes")
    return indexed

def plan_resource_route(division_id:int,task_type:str,data_classification:str="public",
                        external_provider_consent:bool=False,paid_use_approved:bool=False,
                        configured_provider_ids:list[str]|None=None,
                        available_local_model_ids:list[str]|None=None)->dict[str,Any]:
    routes=load_resource_routes()
    if division_id not in routes:
        raise KeyError(f"unknown MasterBot division id: {division_id}")
    route=routes[division_id]
    payload=json.loads(RESOURCE_MAP.read_text(encoding="utf-8"))
    pack=TASK_PACKS.get(task_type.casefold(),"pack.instruct")
    seed_catalog=payload["resource_templates"]["teacher_models"]["seed_models_by_capability_pack"]
    candidates=list(dict.fromkeys(model_id for capability in route["capability_pack_ids"] if capability==pack for model_id in seed_catalog.get(capability,[])))
    available=set(available_local_model_ids or [])
    local=[model_id for model_id in candidates if model_id in available]
    classification=data_classification.casefold()
    sensitive=classification in SENSITIVE_CLASSES or classification not in {"public","non_sensitive","synthetic","open"}
    providers=set(configured_provider_ids or [])
    router=json.loads(MODEL_ROUTER.read_text(encoding="utf-8"))
    eligible=[]
    if external_provider_consent and paid_use_approved and not sensitive:
        for connector in router.get("connectors",[]):
            task_labels={task_type.casefold()}
            if task_type.casefold()=="reasoning": task_labels.add("analysis")
            if connector["id"] in providers and connector.get("mode")=="premium" and connector.get("implementation_status")=="adapter_implemented" and task_labels.intersection({x.casefold() for x in connector.get("task_types",[])}):
                eligible.append(connector["id"])
    if sensitive:
        reason="Sensitive/private data: keep inference local or in a first-party approved boundary; no external provider route."
    elif local:
        reason="A caller-confirmed local model candidate is available; benchmark and license checks still apply."
    elif eligible:
        reason="External provider is explicitly consented, paid-approved, configured and implemented; provider terms still apply."
    else:
        reason="No verified live model route is available; return a safe plan or request human setup rather than pretending a model is connected."
    return {
        "schema":"dreamco.model_resource_route_plan.v1",
        "division_id":division_id,"division_name":route["masterbot_name"],
        "resource_bundle_id":route["resource_bundle_id"],"task_type":task_type,"capability_pack_id":pack,
        "readiness_status":route["readiness_status"],"local_candidate_models":local,
        "catalog_candidate_models":candidates,
        "eligible_external_connectors":eligible,"sensitive_data":sensitive,
        "external_provider_consent":external_provider_consent,"paid_use_approved":paid_use_approved,
        "execution_status":"PLAN_ONLY_NO_PROVIDER_CALL_MADE","reason":reason
    }
