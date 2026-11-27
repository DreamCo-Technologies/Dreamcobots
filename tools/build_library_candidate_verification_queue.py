"""Build a safe verification queue for unverified software-library seed candidates."""
from __future__ import annotations
import argparse, json
from pathlib import Path
from typing import Any
ROOT=Path(__file__).resolve().parents[1]

STEPS=[
 {"id":"identify_upstream","title":"Verify canonical project identity","required_evidence":["official_project_url","upstream_repository","publisher_identity"]},
 {"id":"map_ecosystem","title":"Map candidate to a canonical language/ecosystem and registry","required_evidence":["ecosystem_id","registry_url","package_identity"]},
 {"id":"verify_release","title":"Verify current version and release lifecycle","required_evidence":["version","release_date","maintenance_status","retrieved_at"]},
 {"id":"verify_documentation","title":"Locate official documentation and API references","required_evidence":["official_docs_url","api_reference_url","docs_version"]},
 {"id":"review_license","title":"Review license and permitted uses","required_evidence":["license_spdx_id","license_url","redistribution_scope","training_permission"]},
 {"id":"review_security","title":"Review security, dependencies and supply-chain signals","required_evidence":["security_advisories","dependency_health","provenance_or_signature"]},
 {"id":"design_sandbox","title":"Design a bounded, isolated evaluation plan","required_evidence":["sandbox_profile","network_policy","resource_limits","test_fixture"]},
 {"id":"author_guide","title":"Author original study guide and independent benchmark","required_evidence":["guide_path","practice_path","benchmark_id","human_review_ref"]},
]


def build_queue(catalog:dict[str,Any], ecosystems:dict[str,Any])->dict[str,Any]:
    if catalog.get("schema")!="dreamco.buddy_library_seed_catalog.v1":
        raise ValueError("unsupported library seed catalog schema")
    if ecosystems.get("schema")!="dreamco.library_ecosystems.v1":
        raise ValueError("unsupported library ecosystem schema")
    candidates=catalog.get("candidates")
    eco_rows=ecosystems.get("ecosystems")
    if not isinstance(candidates,list) or not isinstance(eco_rows,list):
        raise ValueError("candidate and ecosystem inventories must be arrays")
    eco_ids={row.get("id") for row in eco_rows if isinstance(row,dict)}
    seen=set(); rows=[]; errors=[]
    for candidate in candidates:
        if not isinstance(candidate,dict):
            errors.append("candidate rows must be objects"); continue
        cid=str(candidate.get("id","")).strip()
        name=str(candidate.get("name","")).strip()
        if not cid or not name:
            errors.append("candidate ID and name are required"); continue
        if cid in seen:
            errors.append(f"duplicate candidate ID: {cid}"); continue
        seen.add(cid)
        status=candidate.get("status")
        rights=candidate.get("rights") if isinstance(candidate.get("rights"),dict) else {}
        if status!="seed_candidate_unverified":
            errors.append(f"{cid}: seed candidates must remain unverified until evidence review")
        if rights.get("execution")!="prohibited_by_seed_catalog":
            errors.append(f"{cid}: execution must remain prohibited at seed stage")
        if rights.get("download") not in {"pending","prohibited"}:
            errors.append(f"{cid}: download permission must remain pending or prohibited")
        rows.append({
            "candidate_id":cid,"name":name,"categories":candidate.get("categories",[]),
            "source_path":(candidate.get("source") or {}).get("path"),
            "ecosystem_mapping":{"status":"unresolved","ecosystem_id":None,"allowed_ids":sorted(x for x in eco_ids if isinstance(x,str))},
            "verification_status":"unverified_candidate",
            "verification_steps":STEPS,
            "rights":{"download":"blocked_pending_review","execution":"prohibited","evaluation":"pending","training":"pending"},
            "guide_status":"not_authored",
            "benchmark_status":"not_defined",
            "model_training_authorized":False,
            "package_downloaded":False,
            "code_executed":False,
            "mastery_awarded":False,
        })
    declared=catalog.get("unique_candidate_count")
    if declared is not None and declared!=len(candidates):
        errors.append("declared unique_candidate_count does not match candidate rows")
    return {
        "schema":"dreamco.library_candidate_verification_queue.v1",
        "status":"structural_errors" if errors else "verification_queue_ready",
        "seed_catalog_status":catalog.get("status"),
        "candidate_count":len(rows),
        "ecosystem_count":len(eco_ids),
        "worldwide_completeness_claimed":False,
        "verified_candidate_count":0,
        "guide_authored_count":0,
        "benchmark_implemented_count":0,
        "errors":errors,
        "candidates":rows,
        "policy":{"free_first":True,"no_automatic_download":True,"no_automatic_execution":True,
                  "unknown_license_blocks_use":True,"training_requires_separate_item_level_permission":True,
                  "human_review_required_before_approval":True},
        "truth_boundary":"This is a verification work queue built from candidate names. It does not verify package identity, current versions, official documentation, license, security, guide quality, execution, or mastery."
    }


def main()->int:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--catalog",type=Path,default=ROOT/"data/buddy-library-seed-catalog.json")
    parser.add_argument("--ecosystems",type=Path,default=ROOT/"config/library_ecosystems.json")
    parser.add_argument("--output",type=Path,default=ROOT/"artifacts/library-candidate-verification-queue.json")
    args=parser.parse_args()
    result=build_queue(json.loads(args.catalog.read_text(encoding="utf-8")),json.loads(args.ecosystems.read_text(encoding="utf-8")))
    encoded=json.dumps(result,indent=2,ensure_ascii=False)+"\n"
    args.output.parent.mkdir(parents=True,exist_ok=True); args.output.write_text(encoded,encoding="utf-8")
    print(json.dumps({k:result[k] for k in ("status","candidate_count","ecosystem_count","verified_candidate_count","guide_authored_count","benchmark_implemented_count","errors")},indent=2))
    return 1 if result["errors"] else 0

if __name__=="__main__": raise SystemExit(main())
