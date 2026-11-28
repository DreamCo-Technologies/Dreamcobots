"""Fail-closed source rights gate used before transcript or derivative processing."""
from pathlib import Path
from typing import Any
from urllib.parse import urlparse
VALID_TIERS={"PUBLIC_DOMAIN","PERMISSIVE_COMMERCIAL","FACT_EXTRACTION_ONLY","BLOCKED"}
def load_registry(path:Path)->dict[str,Any]:
    import yaml
    data=yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if data.get("schema")!="dreamco.source_license_policy.v1": raise ValueError("unsupported registry schema")
    for row in data.get("sources",[]):
        if row.get("tier") not in VALID_TIERS: raise ValueError(f"invalid tier for {row.get('source_id')}")
    return data
def evaluate_source(source:dict[str,Any],registry:dict[str,Any],purpose:str="transcript_extraction")->dict[str,Any]:
    host=(urlparse(str(source.get("source_url") or "")).hostname or "").lower(); match=None
    for row in registry.get("sources",[]):
        for domain in row.get("domains",[]):
            domain=str(domain).lower()
            if host==domain or host.endswith("."+domain): match=row; break
        if match: break
    tier=match.get("tier") if match else None; reason="ALLOW"; allowed=False
    if not match or match.get("verified") is not True: reason="BLOCKED_MISSING_VERIFIED_SOURCE_RECORD"
    elif tier=="BLOCKED": reason="BLOCKED_SOURCE_TIER"
    elif not source.get("license_record_verified") or not str(source.get("license_tag") or "").strip() or source.get("license_tag")=="UNKNOWN_UNVERIFIED": reason="BLOCKED_MISSING_ITEM_LICENSE_EVIDENCE"
    elif purpose=="transcript_extraction" and match.get("transcript_extraction_allowed") is not True: reason="BLOCKED_TRANSCRIPT_PERMISSION_NOT_GRANTED"
    elif purpose=="commercial_training" and (tier not in {"PUBLIC_DOMAIN","PERMISSIVE_COMMERCIAL"} or match.get("commercial_training_allowed") is not True or source.get("commercial_training_permission") is not True): reason="BLOCKED_COMMERCIAL_TRAINING_PERMISSION"
    elif purpose=="fact_extraction" and tier in {"PUBLIC_DOMAIN","PERMISSIVE_COMMERCIAL","FACT_EXTRACTION_ONLY"} and match.get("fact_extraction_allowed") is True: allowed=True
    elif purpose=="transcript_extraction" and tier in {"PUBLIC_DOMAIN","PERMISSIVE_COMMERCIAL"}: allowed=True
    else: reason="BLOCKED_PURPOSE_NOT_AUTHORIZED"
    return {"allowed":allowed,"reason":reason,"permission_tier":tier or "UNREGISTERED","source_id":match.get("source_id") if match else None,"purpose":purpose}
def require_source_permission(source:dict[str,Any],registry:dict[str,Any],purpose:str)->None:
    result=evaluate_source(source,registry,purpose)
    if not result["allowed"]: raise PermissionError(result["reason"])
