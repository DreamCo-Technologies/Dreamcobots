"""Build an explicit, no-guess owner review queue for unresolved domain mappings."""
from __future__ import annotations
import argparse,hashlib,json
from pathlib import Path
from typing import Any

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"config/generated/division-resource-readiness-map.json"
OUTPUT=ROOT/"config/generated/division-owner-review-queue.json"

class OwnerReviewQueueError(ValueError):
    pass

def build_owner_review_queue(source_path:Path=SOURCE)->dict[str,Any]:
    raw=source_path.read_bytes()
    source=json.loads(raw)
    review=source.get("owner_review") or {}
    pending=[]
    for item in review.get("masterbot_domain_decisions",[]):
        if item.get("decision")=="PENDING_OWNER_REVIEW" or item.get("primary_domain_id") is None:
            pending.append({"masterbot_id":int(item["masterbot_id"]),
                "masterbot_name":str(item["masterbot_name"]),
                "resource_bundle_id":item.get("resource_bundle_id"),
                "candidate_domain_ids":list(item.get("candidate_domain_ids") or []),
                "proposed_primary_domain_id":item.get("primary_domain_id"),
                "decision":"PENDING_OWNER_REVIEW","owner_approval":item.get("owner_approval"),
                "evidence":list(item.get("evidence") or []),"no_mapping_inferred":True})
    unassigned=[]
    for item in review.get("unassigned_domain_profiles",[]):
        if item.get("decision")=="PENDING_OWNER_REVIEW" or not item.get("candidate_masterbot_ids"):
            unassigned.append({"domain_id":str(item["domain_id"]),
                "domain_name":str(item["domain_name"]),
                "candidate_masterbot_ids":list(item.get("candidate_masterbot_ids") or []),
                "resource_bundle_id":item.get("standalone_resource_bundle_id"),
                "decision":"PENDING_OWNER_REVIEW","owner_approval":item.get("owner_approval"),
                "evidence":list(item.get("evidence") or []),"no_mapping_inferred":True})
    pending.sort(key=lambda x:x["masterbot_id"])
    unassigned.sort(key=lambda x:x["domain_id"])
    ids=[x["masterbot_id"] for x in pending]
    domains=[x["domain_id"] for x in unassigned]
    if len(ids)!=len(set(ids)) or len(domains)!=len(set(domains)):
        raise OwnerReviewQueueError("duplicate_masterbot_or_domain_in_owner_review_source")
    if any(x["decision"]!="PENDING_OWNER_REVIEW" or not x["no_mapping_inferred"] for x in pending+unassigned):
        raise OwnerReviewQueueError("owner_review_items_must_remain_pending_without_inferred_mapping")
    return {"schema":"dreamco.division_owner_review_queue.v1",
        "source_map_sha256":hashlib.sha256(raw).hexdigest(),
        "masterbot_domain_decisions":pending,"unassigned_domain_profiles":unassigned,
        "counts":{"pending_masterbot_mappings":len(pending),"unassigned_domain_profiles":len(unassigned)},
        "policy":{"auto_assignment":False,"name_similarity_is_not_approval":True,
            "owner_approval_required":True,"evidence_reference_required":True,
            "training_or_model_promotion_blocked_until_mapping_review":True},
        "truth_boundary":"This queue mirrors unresolved source decisions. It does not infer mappings, approve domains, or mark resource bundles provisioned."}

def validate_owner_review_queue(queue:dict[str,Any])->None:
    if queue.get("schema")!="dreamco.division_owner_review_queue.v1":
        raise OwnerReviewQueueError("invalid_owner_review_queue_schema")
    if queue.get("counts",{}).get("pending_masterbot_mappings")!=len(queue.get("masterbot_domain_decisions",[])):
        raise OwnerReviewQueueError("pending_masterbot_count_mismatch")
    if queue.get("counts",{}).get("unassigned_domain_profiles")!=len(queue.get("unassigned_domain_profiles",[])):
        raise OwnerReviewQueueError("unassigned_domain_count_mismatch")
    for item in queue.get("masterbot_domain_decisions",[])+queue.get("unassigned_domain_profiles",[]):
        if item.get("decision")!="PENDING_OWNER_REVIEW" or item.get("no_mapping_inferred") is not True:
            raise OwnerReviewQueueError("unapproved_mapping_or_inferred_assignment_detected")
        if item.get("owner_approval") is not None:
            raise OwnerReviewQueueError("approved_source_item_requires_a_separate_signed_decision_record")

def main()->int:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check",action="store_true")
    parser.add_argument("--source",type=Path,default=SOURCE)
    parser.add_argument("--out",type=Path,default=OUTPUT)
    args=parser.parse_args()
    queue=build_owner_review_queue(args.source);validate_owner_review_queue(queue)
    rendered=json.dumps(queue,indent=2,ensure_ascii=False)+"\n"
    if args.check:
        if not args.out.exists() or args.out.read_text(encoding="utf-8")!=rendered:
            raise SystemExit("owner review queue is stale; regenerate with tools/build_division_owner_review_queue.py")
        print(json.dumps({"ok":True,**queue["counts"]},indent=2));return 0
    args.out.parent.mkdir(parents=True,exist_ok=True);args.out.write_text(rendered,encoding="utf-8")
    print(json.dumps({"written":args.out.relative_to(ROOT).as_posix(),**queue["counts"]},indent=2));return 0

if __name__=="__main__": raise SystemExit(main())
