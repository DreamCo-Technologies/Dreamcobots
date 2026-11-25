#!/usr/bin/env python3
"""Organize approved Buddy study guides into division paths and progress ledgers.

This builds study-ready learning packages from existing guide JSON files. It does
not invent missing summaries or claim model training/mastery.
"""
from __future__ import annotations
import argparse, hashlib, json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SCHEMA="dreamco.buddy_learning_package.v1"
def load(path:Path)->dict[str,Any]:
    return json.loads(path.read_text(encoding="utf-8"))

def slug(value:str)->str:
    return "-".join("".join(ch.lower() if ch.isalnum() else " " for ch in value).split())

def organize(guides:list[dict[str,Any]], divisions:list[str], user_data:list[dict[str,Any]]|None=None)->dict[str,Any]:
    packages=[]
    division_index={name:[] for name in divisions}
    for guide in guides:
        source=guide.get("source",{})
        rights=guide.get("rights",{})
        if guide.get("review",{}).get("status")!="approved":
            continue
        if not (rights.get("study_permission") is True and rights.get("summary_derivative_permission") is True and rights.get("evaluation_permission") is True):
            continue
        summary=guide.get("summary",{})
        mapping=guide.get("division_mapping",[])
        mapped=[]
        for item in mapping:
            name=item if isinstance(item,str) else item.get("division") if isinstance(item,dict) else None
            if name in division_index and name not in mapped:
                mapped.append(name)
        if not mapped:
            continue
        concepts=guide.get("key_concepts",[])
        objectives=guide.get("learning_objectives",[])
        sections=guide.get("sections",[])
        exercises=guide.get("exercises",[])
        checks=guide.get("knowledge_checks",[])
        package={
          "schema":SCHEMA,
          "asset_id":hashlib.sha256((str(source.get("source_type"))+"|"+str(source.get("source_id"))+"|"+str(source.get("revision"))).encode()).hexdigest()[:20],
          "ownership":{"artifact_owner":"DreamCo-Technologies","artifact_type":"DreamCo_original_derived_study_package","upstream_material_owner":"upstream_rightsholder","upstream_license":source.get("license"),"attribution_required":True,"rights_evidence_ref":rights.get("evidence_ref"),"user_data_is_separately_governed":True},
          "source":source,
          "rights":rights,
          "summary":{
            "executive_overview":summary.get("executive_overview"),
            "detailed_explanation":summary.get("detailed_explanation"),
            "best_knowledge_extracted":{
              "learning_objectives":objectives,
              "core_concepts":[{"concept":x.get("name"),"explanation":x.get("explanation")} for x in concepts if isinstance(x,dict)],
              "detailed_sections":[{"heading":x.get("heading"),"explanation":x.get("explanation"),"source_locator":x.get("source_locator")} for x in sections if isinstance(x,dict)],
              "worked_examples":guide.get("worked_examples",[]),
              "practical_exercises":exercises,
              "capstone":guide.get("capstone",{}),
              "knowledge_checks":checks,
              "answer_key":guide.get("answer_key",[]),
              "limitations_and_risks":guide.get("limitations_and_risks",[]),
              "references":guide.get("references",[])
            }
          },
          "study_path":{
            "path_id":"study-"+hashlib.sha256((str(source.get("source_id"))+"|"+str(source.get("revision"))).encode()).hexdigest()[:16],
            "source_revision":source.get("revision"),
            "prerequisites":guide.get("prerequisites",[]),
            "learning_objectives":objectives,
            "sequence":[
              {"step":1,"type":"orient","content":"Read the executive overview, source identity, revision, license and prerequisites","completion_evidence":"Learner can explain why this source matters and identify its boundaries"},
              {"step":2,"type":"deep_read","content":"Study the detailed explanation and every source-linked section in order","sections":[s.get("heading") for s in sections if isinstance(s,dict)],"completion_evidence":"Learner can explain each section in their own words"},
              {"step":3,"type":"concept_retrieval","concepts":[c.get("name") for c in concepts if isinstance(c,dict)],"completion_evidence":"Learner correctly explains and applies the core concepts"},
              {"step":4,"type":"worked_examples","items":guide.get("worked_examples",[]),"completion_evidence":"Learner reproduces and explains at least one example"},
              {"step":5,"type":"deliberate_practice","exercises":exercises,"completion_evidence":"Exercise acceptance criteria pass"},
              {"step":6,"type":"knowledge_check","checks":checks,"answer_key":guide.get("answer_key",[]),"completion_evidence":"Configured assessment threshold is met"},
              {"step":7,"type":"capstone","capstone":guide.get("capstone",{}),"completion_evidence":"Independent capstone acceptance tests pass"}
            ],
            "recommended_spaced_review_days":[1,3,7,14,30]
          },
          "division_ids":mapped,
          "assessment":{"knowledge_check_count":len(checks),"exercise_count":len(exercises),"capstone_acceptance_tests":guide.get("capstone",{}).get("acceptance_tests",[]),"mastery_requires_passed_assessment_and_independent_capstone":True},
          "training":{"study_or_rag_eligible":True,"weight_training_eligible":rights.get("training_permission") is True,"training_permission":rights.get("training_permission") is True,"blocked_reason":None if rights.get("training_permission") is True else "Explicit training permission is not recorded"},
          "progress":{"status":"ready_to_assign","assigned":False,"started_at":None,"last_activity_at":None,"lessons_completed":0,"assessment_attempts":0,"best_score":None,"capstone_passed":False,"mastery_status":"not_assessed","next_action":"assign_to_division_learning_queue","events":[],"last_assessed_revision":None}
        }
        packages.append(package)
        for name in mapped: division_index[name].append(package["asset_id"])
    divisions_out=[]
    for name,ids in division_index.items():
        divisions_out.append({"division":name,"learning_asset_ids":ids,"available_learning_assets":len(ids),"daily_target_lessons":5,"assignment_policy":"assign approved assets in prerequisite order; never count a pending source as a lesson","progress":{"assigned":0,"started":0,"completed":0,"mastered":0}})
    private=[]
    for row in user_data or []:
        if not isinstance(row,dict): continue
        private.append({"asset_id":row.get("asset_id"),"owner":"user","classification":row.get("classification","user_provided"),"consent_scope":row.get("consent_scope",[]),"study_allowed":row.get("study_allowed") is True,"summary_allowed":row.get("summary_allowed") is True,"evaluation_allowed":row.get("evaluation_allowed") is True,"training_allowed":row.get("training_allowed") is True,"retention_policy":row.get("retention_policy","user_configured"),"source_hash":row.get("sha256"),"source_uri":row.get("source_uri"),"division_ids":row.get("division_ids",[]),"ownership_note":"User retains ownership of user-provided data; consent is purpose-specific and never inferred."})
    return {"schema":"dreamco.buddy_learning_organization.v1","generated_at":datetime.now(timezone.utc).isoformat(),"status":"organized_from_approved_guides_only","ownership_policy":{"dreamco_original_summaries":"DreamCo-owned original authored expression and instructional structure, subject to applicable law and upstream license terms","user_data":"User retains ownership; purpose-specific consent is required for study, summary, evaluation and training","third_party_sources":"Retain upstream ownership, license, attribution and any reuse restrictions"},"coverage":{"approved_guides_organized":len(packages),"divisions":len(divisions_out),"divisions_with_assets":sum(bool(x["learning_asset_ids"]) for x in divisions_out),"user_data_assets_registered":len(private),"weight_training_eligible_assets":sum(x["training"]["weight_training_eligible"] for x in packages)},"packages":packages,"division_curricula":divisions_out,"user_data_registry":private,"progress_ledger":{"source_of_truth":"append-only progress events emitted by the Buddy runtime","required_events":["asset_assigned","study_started","lesson_completed","knowledge_check_submitted","exercise_passed","capstone_submitted","capstone_passed","mastery_awarded","remediation_assigned","training_run_started","training_run_completed","training_run_evaluated"],"mastery_rule":"Mastery requires configured assessment threshold plus independently verified capstone; exposure or summary reading alone never awards mastery.","training_runs_require":["approved data manifest","training_permission true for every included asset","user-data training consent where user data is included","baseline metrics","holdout evaluation","compute approval and budget","versioned checkpoint","rollback plan"]},"truth_boundary":"This organizer creates division-linked study packages and an initial progress structure. It does not create absent summaries, assign lessons in a running Buddy service, update model weights, or prove study progress."}

def main()->int:
    p=argparse.ArgumentParser()
    p.add_argument("--guides-dir",required=True);p.add_argument("--divisions",required=True)
    p.add_argument("--user-data-manifest");p.add_argument("--out-dir",required=True);a=p.parse_args()
    guide_dir=Path(a.guides_dir)
    guides=[load(x) for x in sorted(guide_dir.glob("*.json"))] if guide_dir.exists() else []
    names=json.loads(Path(a.divisions).read_text(encoding="utf-8"))
    user=load(Path(a.user_data_manifest)).get("assets",[]) if a.user_data_manifest and Path(a.user_data_manifest).exists() else []
    result=organize(guides,names,user)
    out=Path(a.out_dir);out.mkdir(parents=True,exist_ok=True)
    (out/"buddy-learning-organization.json").write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    lines=["# Buddy learning organization","",f"- Approved study guides organized: {result['coverage']['approved_guides_organized']}",f"- Divisions with assigned-ready assets: {result['coverage']['divisions_with_assets']} / {result['coverage']['divisions']}",f"- User-owned data assets registered: {result['coverage']['user_data_assets_registered']}",f"- Weight-training eligible assets: {result['coverage']['weight_training_eligible_assets']}","", "This report is not evidence that Buddy has studied or trained on these assets."]
    (out/"buddy-learning-progress.md").write_text("\\n".join(lines)+"\n",encoding="utf-8")
    print(json.dumps(result["coverage"],indent=2));return 0
if __name__=="__main__":raise SystemExit(main())
