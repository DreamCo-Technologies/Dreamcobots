"""Bounded autonomous metadata discovery and per-MasterBot routing fleet."""
from __future__ import annotations
import json,re,os
from datetime import datetime,timezone
from pathlib import Path
from typing import Any
from .hub import DatasetHub,DatasetPolicyError
from .sources import discover,inspect_huggingface_dataset_card,SourceAccessError
from .license_policy import assess_training_candidate
from .unknown_router import ALIASES

ROOT=Path(__file__).resolve().parents[2]
REGISTRY=ROOT/"config/masterbot-65-registry.json"
TAXONOMY_MAP=ROOT/"config/generated/division-huggingface-taxonomy-map.json"
RESOURCE_MAP=ROOT/"config/generated/division-resource-readiness-map.json"

def _load_taxonomy_routes()->dict[int,dict[str,Any]]:
    payload=json.loads(TAXONOMY_MAP.read_text(encoding="utf-8"))
    if payload.get("status")!="discovery_only_requires_owner_and_rights_review":
        raise ValueError("Hugging Face taxonomy map must remain discovery-only")
    routes=payload.get("routes",[])
    if len(routes)!=65:
        raise ValueError("Hugging Face taxonomy map must cover all 65 MasterBots")
    indexed={int(row["masterbot_id"]):row for row in routes}
    if len(indexed)!=65:
        raise ValueError("Hugging Face taxonomy map contains duplicate MasterBot routes")
    return indexed

def _load_resource_profiles()->dict[int,dict[str,Any]]:
    payload=json.loads(RESOURCE_MAP.read_text(encoding="utf-8"))
    if payload.get("status")!="requirements_defined_not_provisioned":
        raise ValueError("division resource map must retain honest readiness status")
    routes=payload.get("routes",[])
    if len(routes)!=65:
        raise ValueError("division resource map must cover all 65 MasterBots")
    indexed={int(row["masterbot_id"]):row for row in routes}
    if len(indexed)!=65:
        raise ValueError("division resource map contains duplicate MasterBot routes")
    return indexed

def _query_for(name:str,taxonomy_route:dict[str,Any]|None=None)->str:
    if taxonomy_route:
        queries=taxonomy_route.get("search_queries",[])
        if queries and str(queries[0]).strip():
            return str(queries[0]).strip()
    tags=ALIASES.get(name)
    if tags:
        return " ".join(tags[:3])
    value=re.sub(r"(?<=[a-z])(?=[A-Z])"," ",name)
    value=re.sub(r"^Dream\\s*","",value,flags=re.I)
    return value.strip() or name

def run_discovery_fleet(hub:DatasetHub|None=None,lanes_per_run:int=5,offset:int|None=None,limit:int=3)->dict[str,Any]:
    if not 1<=lanes_per_run<=65: raise ValueError("lanes_per_run must be between 1 and 65")
    if not 1<=limit<=10: raise ValueError("per-source result limit must be between 1 and 10")
    registry=json.loads(REGISTRY.read_text(encoding="utf-8"))
    bots=registry.get("divisions",[])
    if len(bots)!=65: raise ValueError("Canonical registry must contain exactly 65 MasterBots")
    taxonomy_routes=_load_taxonomy_routes()
    resource_profiles=_load_resource_profiles()
    canonical_ids={int(bot["id"]) for bot in bots}
    if canonical_ids!=set(taxonomy_routes):
        raise ValueError("Hugging Face taxonomy lanes do not match canonical MasterBot IDs")
    if canonical_ids!=set(resource_profiles):
        raise ValueError("division resource bundles do not match canonical MasterBot IDs")
    if offset is None: offset=(datetime.now(timezone.utc).date().toordinal()*lanes_per_run)%65
    selected=[bots[(offset+i)%65] for i in range(lanes_per_run)]
    catalog=hub or DatasetHub()
    report={"schema":"dreamco.dataset_discovery_fleet.v1","created_at":datetime.now(timezone.utc).isoformat(),
        "masterbot_count":65,"lanes_scanned":[],"candidates_recorded":0,"source_errors":{},
        "network_enabled":os.environ.get("DREAMCO_ALLOW_SOURCE_NETWORK")=="1","files_downloaded":False,"training_approved":False,"weights_trained":False}
    for bot in selected:
        taxonomy_route=taxonomy_routes[int(bot["id"])]
        resource_profile=resource_profiles[int(bot["id"])]
        query=_query_for(bot["name"],taxonomy_route)
        found=discover(query,limit=limit)
        recorded=0
        for candidate in found["results"]+found["model_results"]:
            candidate={**candidate,"rights_assessment":"UNVERIFIED_DISCOVERY_ONLY","ai_training_allowed":False,"content_rights_verified":False,"privacy_review":"PENDING",
                "dreamco_taxonomy":{"lane_id":taxonomy_route["lane_id"],
                    "subject_terms":taxonomy_route["subject_terms"],
                    "capability_pack_ids":taxonomy_route["capability_pack_ids"],
                    "candidate_pipeline_tags":taxonomy_route["candidate_pipeline_tags"],
                    "domain_crosswalk":taxonomy_route["domain_crosswalk"],
                    "routing_status":"DISCOVERY_ONLY_NOT_TRAINING_APPROVED"},
                "division_resources":{"resource_bundle_id":resource_profile["resource_bundle_id"],
                    "readiness_status":resource_profile["readiness_status"],
                    "database_namespace":resource_profile["database"]["logical_namespace"],
                    "teacher_model_candidate_ids":[x["model_id"] for x in resource_profile["teacher_models"]["candidate_models"]],
                    "model_routing_status":resource_profile["model_routing"]["status"],
                    "resource_truth":"requirements_defined_not_provisioned"}}
            if candidate.get("source")=="huggingface":
                try:
                    card=inspect_huggingface_dataset_card(str(candidate.get("id","")))
                    candidate["dataset_card_summary"]={k:card.get(k) for k in ("card_sha256","license","tags","task_categories","language","rights_status")}
                    candidate["license"]=card.get("license") or candidate.get("license")
                    candidate["dataset_card_ai_training_claim"]=card.get("ai_training_allowed")
                    candidate["ai_training_allowed"]=str(card.get("ai_training_allowed","")).strip().lower() in {"true","yes"}
                except (SourceAccessError,ValueError) as exc:
                    candidate["dataset_card_inspection_error"]=type(exc).__name__
            candidate["license_assessment"]=assess_training_candidate(candidate)
            try:
                catalog.record_external_candidate(candidate,int(bot["id"]),query)
                recorded+=1
            except DatasetPolicyError as exc:
                report["source_errors"]["candidate_validation"]=report["source_errors"].get("candidate_validation",0)+1
        report["candidates_recorded"]+=recorded
        for source,error in found["source_errors"].items():
            report["source_errors"][source]=report["source_errors"].get(source,0)+1
        report["lanes_scanned"].append({"masterbot_id":bot["id"],"masterbot":bot["name"],
            "query":query,"candidate_count":recorded,"status":"DISCOVERY_ONLY_RIGHTS_UNVERIFIED",
            "taxonomy_lane_id":taxonomy_route["lane_id"],
            "candidate_pipeline_tags":taxonomy_route["candidate_pipeline_tags"],
            "resource_bundle_id":resource_profile["resource_bundle_id"],
            "resource_readiness_status":resource_profile["readiness_status"]})
    report["next_offset"]=(offset+lanes_per_run)%65
    report["catalog_stats"]=catalog.stats()
    report["limitations"]=["Metadata discovery only; no dataset files downloaded",
        "Public listing or license tag does not establish AI-training rights",
        "Source coverage is bounded and rate-limited; it is not exhaustive",
        "Training still requires dataset quality, privacy, rights, compute and approval gates"]
    return report
