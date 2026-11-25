#!/usr/bin/env python3
"""Create a rights-gated guide queue and validate Buddy-authored source guides."""
from __future__ import annotations
import argparse, json
from pathlib import Path
from typing import Any

ROOT=Path(__file__).resolve().parents[1]
RIGHTS=ROOT/"config/buddy-source-rights-manifest.json"

def read_json(path: Path) -> dict[str,Any]:
    return json.loads(path.read_text(encoding="utf-8"))

def rights_key(row: dict[str,Any]) -> str:
    return f"{row.get('source_type','')}|{row.get('source_id','')}"

def build_queue(snapshot: dict[str,Any], rights_doc: dict[str,Any]) -> dict[str,Any]:
    grants={rights_key(x):x for x in rights_doc.get("resources",[]) if isinstance(x,dict)}
    queue=[]
    for row in snapshot.get("resources",[]):
        grant=grants.get(rights_key(row),{})
        flags=("study_permission","summary_derivative_permission","evaluation_permission")
        eligible=all(grant.get(flag) is True for flag in flags) and bool(str(grant.get("evidence_ref","")).strip())
        queue.append({
            "source_type":row.get("source_type"),"source_id":row.get("source_id"),"url":row.get("url"),
            "revision":row.get("revision") or row.get("default_branch") or row.get("last_modified"),
            "license":row.get("license") or row.get("license_spdx"),
            "status":"guide_authoring_eligible" if eligible else "rights_pending",
            "training_permission":grant.get("training_permission") is True,
            "training_evidence_ref":grant.get("training_evidence_ref"),
            "model_training_eligible":grant.get("training_permission") is True and bool(str(grant.get("training_evidence_ref","")).strip()),
            "redistribution_permission":grant.get("redistribution_permission"),
            "commercial_use_permission":grant.get("commercial_use_permission"),
            "rights_evidence_ref":grant.get("evidence_ref") if eligible else None,
            "teacher_model":"GPT-6",
            "student_model":"Buddy",
            "authoring_prompt":"buddy/bootcamp/prompts/buddy-university-teacher-authoring.md",
            "authoring_status":"ready_for_teacher_authoring" if eligible else "blocked_rights_pending",
            "owner_designation":"user_designated_owner_pending_review",
            "required_guide":"dreamco.buddy_source_study_guide.v1",
            "required_study_path":["prerequisites","deep_read","best_knowledge_extraction","worked_examples",
                "software_and_tool_lab","workflow_simulation","independent_practice","knowledge_check",
                "capstone","teach_back_and_unseen_transfer","spaced_review"]
        })
    return {"schema":"dreamco.buddy_source_study_queue.v1","source_snapshot_generated_at":snapshot.get("generated_at"),
            "counts":{"discovered":len(queue),"guide_authoring_eligible":sum(x["status"]=="guide_authoring_eligible" for x in queue),
                      "rights_pending":sum(x["status"]=="rights_pending" for x in queue)},
            "queue":queue,"truth_boundary":"A queued source is not a completed summary, training example, or mastery result."}

def validate_guide(guide:dict[str,Any], queue_item:dict[str,Any])->list[str]:
    errors=[]
    if guide.get("schema")!="dreamco.buddy_source_study_guide.v1": errors.append("unsupported schema")
    source=guide.get("source") if isinstance(guide.get("source"),dict) else {}
    for key in ("source_type","source_id","url"):
        if source.get(key)!=queue_item.get(key): errors.append(f"source {key} mismatch")
    if queue_item.get("status")!="guide_authoring_eligible": errors.append("source is not rights-cleared for guide authoring")
    rights=guide.get("rights") if isinstance(guide.get("rights"),dict) else {}
    for key in ("study_permission","summary_derivative_permission","evaluation_permission"):
        if rights.get(key) is not True: errors.append(f"missing {key}")
    if not str(rights.get("evidence_ref","")).strip(): errors.append("missing rights evidence")
    summary=guide.get("summary") if isinstance(guide.get("summary"),dict) else {}
    if len(str(summary.get("executive_overview","")).strip())<100: errors.append("executive overview too short")
    if len(str(summary.get("detailed_explanation","")).strip())<500: errors.append("detailed explanation too short")
    for key,minimum in (("sections",1),("learning_objectives",3),("key_concepts",5),("worked_examples",1),("exercises",3),("knowledge_checks",5),("answer_key",5),("division_mapping",1),("references",1)):
        value=guide.get(key)
        if not isinstance(value,list) or len(value)<minimum: errors.append(f"{key} requires at least {minimum} entries")
    if not isinstance(guide.get("capstone"),dict) or not guide["capstone"].get("acceptance_tests"): errors.append("capstone acceptance tests required")
    review=guide.get("review") if isinstance(guide.get("review"),dict) else {}
    if review.get("status") not in {"draft","needs_review","approved","rejected"}: errors.append("invalid review status")
    return errors

def main()->int:
    parser=argparse.ArgumentParser()
    parser.add_argument("--snapshot",required=True)
    parser.add_argument("--rights",default=str(RIGHTS))
    parser.add_argument("--out-dir",required=True)
    args=parser.parse_args()
    snapshot=read_json(Path(args.snapshot))
    rights_path=Path(args.rights)
    rights=read_json(rights_path) if rights_path.exists() else {"resources":[]}
    result=build_queue(snapshot,rights)
    out=Path(args.out_dir); out.mkdir(parents=True,exist_ok=True)
    (out/"source-study-queue.json").write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(result["counts"],indent=2))
    return 0
if __name__=="__main__": raise SystemExit(main())
