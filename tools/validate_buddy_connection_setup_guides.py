"""Validate beginner-friendly connection setup guides against the canonical catalog."""
from __future__ import annotations
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
CATALOG=ROOT/"config/buddy-universal-connection-catalog.json"
GUIDES=ROOT/"config/buddy-connection-setup-guides.json"

def validate(catalog, guides):
    errors=[]
    if catalog.get("schema")!="dreamco.buddy.connection_setup_catalog.v1":
        errors.append("unsupported connection catalog schema")
    if guides.get("schema")!="dreamco.buddy.connection_setup_guides.v1":
        errors.append("unsupported setup guide schema")
    source=catalog.get("connections")
    rows=guides.get("profiles")
    if not isinstance(source,list) or not isinstance(rows,list):
        return errors+["connections and profiles must be arrays"]
    expected={row.get("id") for row in source if isinstance(row,dict)}
    actual=[row.get("connection_id") for row in rows if isinstance(row,dict)]
    if len(actual)!=len(rows):
        errors.append("every profile must be an object")
    if len(actual)!=len(set(actual)):
        errors.append("duplicate connection setup profile")
    if set(actual)!=expected:
        errors.append(f"catalog/profile mismatch: missing={sorted(expected-set(actual))}, extra={sorted(set(actual)-expected)}")
    for row in rows:
        if not isinstance(row,dict): continue
        cid=row.get("connection_id","<unknown>")
        for field in ("beginner_explanation","setup_steps","permission_review","credential_handling","cost_review","local_or_low_cost_alternative","health_check","disconnect_and_recovery","official_setup_url","current_provider_terms_review"):
            if not row.get(field): errors.append(f"{cid}: missing {field}")
        if len(row.get("setup_steps",[]))<5: errors.append(f"{cid}: setup_steps must be actionable")
        permission=row.get("permission_review",{})
        if permission.get("credential_values_in_chat") is not False or permission.get("browser_storage_for_secrets") is not False:
            errors.append(f"{cid}: unsafe credential handling policy")
        credential=row.get("credential_handling",{})
        if credential.get("required") and not credential.get("secret_reference"):
            errors.append(f"{cid}: required secret reference missing")
        health=row.get("health_check",{})
        if health.get("status")!="not_run_by_catalog":
            errors.append(f"{cid}: catalog must not imply a health check ran")
        if row.get("status")!="guide_template_ready_live_connection_unverified":
            errors.append(f"{cid}: live connection status must remain unverified")
    policy=guides.get("global_policy",{})
    if policy.get("no_password_or_raw_secret_collection_in_chat") is not True:
        errors.append("global policy must prohibit raw secret collection in chat")
    if policy.get("default_access")!="read_only_or_mock":
        errors.append("default access must be read-only or mock")
    return errors

def main():
    catalog=json.loads(CATALOG.read_text(encoding="utf-8"))
    guides=json.loads(GUIDES.read_text(encoding="utf-8"))
    errors=validate(catalog,guides)
    print(json.dumps({"status":"invalid" if errors else "valid","errors":errors,"profile_count":len(guides.get("profiles",[]))},indent=2))
    return 1 if errors else 0

if __name__=="__main__": raise SystemExit(main())
