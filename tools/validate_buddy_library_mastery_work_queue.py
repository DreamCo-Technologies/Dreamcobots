"""Validate library ecosystem and seed-candidate work queue coverage without promoting rights."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SEEDS=ROOT/"data/buddy-library-seed-catalog.json"
ECOSYSTEMS=ROOT/"config/library_ecosystems.json"
COVERAGE=ROOT/"config/buddy-library-ecosystem-adapter-coverage.json"
QUEUE=ROOT/"config/buddy-library-mastery-work-queue.json"
def validate(seeds,ecosystems,coverage,queue):
 errors=[]
 if queue.get("schema")!="dreamco.buddy_library_mastery_work_queue.v1": errors.append("unsupported library work queue schema")
 expected_candidates={x.get("id") for x in seeds.get("candidates",[]) if isinstance(x,dict)}
 candidate_rows=queue.get("candidate_work_items",[])
 candidate_ids=[x.get("candidate_id") for x in candidate_rows if isinstance(x,dict)]
 if len(candidate_ids)!=len(candidate_rows) or len(candidate_ids)!=len(set(candidate_ids)): errors.append("candidate IDs must be present and unique")
 if set(candidate_ids)!=expected_candidates: errors.append(f"candidate coverage mismatch: missing={len(expected_candidates-set(candidate_ids))}, extra={len(set(candidate_ids)-expected_candidates)}")
 expected_ecosystems={x.get("id") for x in ecosystems.get("ecosystems",[]) if isinstance(x,dict)}
 coverage_ids={x.get("id") for x in coverage.get("ecosystems",[]) if isinstance(x,dict)}
 rows=queue.get("ecosystem_work_items",[])
 ecosystem_ids=[x.get("ecosystem_id") for x in rows if isinstance(x,dict)]
 if set(ecosystem_ids)!=expected_ecosystems or set(coverage_ids)!=expected_ecosystems: errors.append("ecosystem registry and adapter coverage must match exactly")
 required={"resolve_canonical_package_identity","assign_exact_ecosystem_and_official_registry","pin_current_version_and_release_date","verify_official_documentation_and_source_repository","review_license_security_advisories_and_maintenance","inventory_public_api_with_versioned_provenance","write_original_use_cases_and_three_practice_exercises","build_safe_local_sandbox_without_untrusted_execution","define_task_benchmark_and_private_holdout","human_review_and_approve_for_internal_study"}
 for row in candidate_rows:
  if not isinstance(row,dict): continue
  cid=row.get("candidate_id","<unknown>")
  if not required.issubset(set(row.get("required_work",[]))): errors.append(f"{cid}: required work steps missing")
  if row.get("package_identity_status")!="unverified_candidate" or row.get("license_status")!="unknown_pending_review": errors.append(f"{cid}: candidate cannot be promoted without review")
  if row.get("mastery_status")!="not_assessed": errors.append(f"{cid}: candidate cannot claim mastery")
  rights=row.get("rights",{})
  if rights.get("download")!="pending" or rights.get("execution")!="prohibited_until_review" or rights.get("training")!="pending": errors.append(f"{cid}: rights boundary weakened")
 for row in rows:
  if row.get("status")!="ecosystem_discovery_review_required": errors.append(f"{row.get('ecosystem_id')}: ecosystem status must remain review required")
 if queue.get("worldwide_completeness_claimed") is not False: errors.append("worldwide completeness must not be claimed")
 if queue.get("counts",{}).get("seed_candidates")!=len(candidate_rows): errors.append("candidate count mismatch")
 return errors
def main():
 seeds=json.loads(SEEDS.read_text(encoding="utf-8")); ecosystems=json.loads(ECOSYSTEMS.read_text(encoding="utf-8")); coverage=json.loads(COVERAGE.read_text(encoding="utf-8")); queue=json.loads(QUEUE.read_text(encoding="utf-8")); errors=validate(seeds,ecosystems,coverage,queue)
 print(json.dumps({"status":"invalid" if errors else "valid","errors":errors,"ecosystem_count":len(queue.get("ecosystem_work_items",[])),"candidate_count":len(queue.get("candidate_work_items",[]))},indent=2))
 return 1 if errors else 0
if __name__=="__main__": raise SystemExit(main())
