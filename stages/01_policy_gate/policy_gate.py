"""Fail-closed source rights gate used before transcript or derivative processing."""
from pathlib import Path
from datetime import datetime
import hashlib
import re
from typing import Any
from urllib.parse import urlparse
VALID_TIERS={"PUBLIC_DOMAIN","PERMISSIVE_COMMERCIAL","FACT_EXTRACTION_ONLY","BLOCKED"}
EVIDENCE_ROOT=Path(__file__).resolve().parents[2]
SHA256_RE=re.compile(r"^[0-9a-f]{64}$")
def _item_license_evidence_valid(source:dict[str,Any])->bool:
    if source.get("license_record_verified") is not True or not str(source.get("license_tag") or "").strip() or source.get("license_tag")=="UNKNOWN_UNVERIFIED": return False
    if not str(source.get("license_evidence_url") or "").startswith("https://"): return False
    evidence_path=Path(str(source.get("license_evidence_path") or ""))
    if not evidence_path.parts or evidence_path.is_absolute() or ".." in evidence_path.parts: return False
    snapshot=(EVIDENCE_ROOT/evidence_path).resolve()
    if not snapshot.is_relative_to(EVIDENCE_ROOT.resolve()) or not snapshot.is_file(): return False
    expected_hash=str(source.get("license_evidence_sha256") or "").lower()
    if not SHA256_RE.fullmatch(expected_hash): return False
    try:
        if hashlib.sha256(snapshot.read_bytes()).hexdigest()!=expected_hash: return False
    except OSError:
        return False
    if source.get("license_review_status")!="approved" or not str(source.get("license_reviewer_id") or "").strip(): return False
    try: datetime.fromisoformat(str(source.get("license_reviewed_at") or "").replace("Z","+00:00"))
    except ValueError: return False
    return True
def _url_matches_prefix(url:str,prefix:str)->bool:
    url=url.strip(); prefix=prefix.strip()
    if prefix.endswith("="): return url.startswith(prefix) and len(url)>len(prefix)
    base=prefix.rstrip("/")
    return url==base or url.startswith(base+"/") or url.startswith(base+"?")
def load_registry(path:Path)->dict[str,Any]:
    import yaml
    data=yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if data.get("schema")!="dreamco.source_license_policy.v1": raise ValueError("unsupported registry schema")
    for row in data.get("sources",[]):
        if row.get("tier") not in VALID_TIERS: raise ValueError(f"invalid tier for {row.get('source_id')}")
    return data
def evaluate_source(source:dict[str,Any],registry:dict[str,Any],purpose:str="transcript_extraction")->dict[str,Any]:
    source_url=str(source.get("source_url") or "").strip()
    host=(urlparse(source_url).hostname or "").lower()
    source_id=str(source.get("source_id") or "")
    domain_matches=[]
    for row in registry.get("sources",[]):
        if any(host==str(domain).lower() or host.endswith("."+str(domain).lower())
               for domain in row.get("domains",[])):
            domain_matches.append(row)
    match=None
    for row in domain_matches:
        allowed_ids={str(value) for value in row.get("catalog_source_ids",[row.get("source_id")])}
        if source_id in allowed_ids:
            match=row
            break
    if match is None and domain_matches:
        match=domain_matches[0]
    tier=match.get("tier") if match else None
    reason="ALLOW"
    allowed=False
    if not match or match.get("verified") is not True:
        reason="BLOCKED_MISSING_VERIFIED_SOURCE_RECORD"
    elif tier=="BLOCKED":
        reason="BLOCKED_SOURCE_TIER"
    elif source_id not in {str(value) for value in match.get("catalog_source_ids",[match.get("source_id")])}:
        reason="BLOCKED_SOURCE_ID_NOT_REGISTERED"
    elif match.get("allowed_url_prefixes") and not any(
        _url_matches_prefix(source_url,str(prefix)) for prefix in match.get("allowed_url_prefixes",[])
    ):
        reason="BLOCKED_SOURCE_URL_NOT_ALLOWLISTED"
    elif not _item_license_evidence_valid(source):
        reason="BLOCKED_MISSING_OR_UNVERIFIED_ITEM_LICENSE_EVIDENCE"
    elif purpose=="transcript_extraction" and match.get("transcript_extraction_allowed") is not True:
        reason="BLOCKED_TRANSCRIPT_PERMISSION_NOT_GRANTED"
    elif purpose=="commercial_training" and (
        tier not in {"PUBLIC_DOMAIN","PERMISSIVE_COMMERCIAL"}
        or match.get("commercial_training_allowed") is not True
        or source.get("commercial_training_permission") is not True
        or not str(source.get("commercial_training_evidence_ref") or "").strip()
    ):
        reason="BLOCKED_COMMERCIAL_TRAINING_PERMISSION"
    elif purpose=="fact_extraction" and tier in {"PUBLIC_DOMAIN","PERMISSIVE_COMMERCIAL","FACT_EXTRACTION_ONLY"} and match.get("fact_extraction_allowed") is True:
        allowed=True
    elif purpose=="transcript_extraction" and tier in {"PUBLIC_DOMAIN","PERMISSIVE_COMMERCIAL"}:
        allowed=True
    else:
        reason="BLOCKED_PURPOSE_NOT_AUTHORIZED"
    return {"allowed":allowed,"reason":reason,"permission_tier":tier or "UNREGISTERED",
            "source_id":match.get("source_id") if match else None,"purpose":purpose}
def require_source_permission(source:dict[str,Any],registry:dict[str,Any],purpose:str)->None:
    result=evaluate_source(source,registry,purpose)
    if not result["allowed"]: raise PermissionError(result["reason"])
