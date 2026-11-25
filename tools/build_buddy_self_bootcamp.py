#!/usr/bin/env python3
"""Build Buddy's division-specific curriculum map and self-authoring bootcamp plan.

This creates a verifiable plan and coverage ledger. It does not pretend to have
authored source guides or trained Buddy; those require a connected authoring/model runtime.
"""
from __future__ import annotations
import argparse, json, re
from pathlib import Path
from typing import Any

def division_names(source: str) -> list[str]:
    pattern = re.compile(r"^  ([A-Za-z][A-Za-z0-9]+): \{\n([\s\S]*?)^  \},?$", re.MULTILINE)
    names=[]
    for match in pattern.finditer(source):
        body=match.group(2)
        if all(key in body for key in ("purpose:", "focusAreas:", "serves:", "outcome:", "boundary:")):
            names.append(match.group(1))
    if len(names)!=55 or len(set(names))!=55:
        raise ValueError(f"Expected 55 unique domain divisions; found {len(names)}")
    return names

def build(divisions:list[str], hf:dict[str,Any], onet:dict[str,Any], queue:dict[str,Any], workforce:dict[str,Any], government:dict[str,Any])->dict[str,Any]:
    subjects=sorted(set(hf.get("subject_terms",[])))
    tasks=int(onet.get("inventory",{}).get("task_statements",0))
    occupations=int(onet.get("inventory",{}).get("occupations",0))
    sources=queue.get("counts",{})
    tracks=workforce.get("training_paths",[])
    gov_tracks=government.get("official_sources",[])
    rows=[]
    for name in divisions:
        rows.append({
          "division":name,
          "curriculum_status":"planned_not_yet_authored",
          "hugging_face_subject_taxonomy_count":len(subjects),
          "hugging_face_subjects":subjects,
          "occupational_learning_path":{
            "source":"O*NET",
            "occupations_in_current_import":occupations,
            "task_statements_in_current_import":tasks,
            "status":"available_if_current_import_passed" if tasks else "awaiting_verified_O*NET_import",
            "must_map_relevant_tasks_to_division":True
          },
          "shared_entrepreneurship_tracks":[x.get("id") for x in tracks],
          "government_and_workforce_sources":[x.get("id") for x in gov_tracks],
          "daily_plan":{"target_lessons":5,"schedule":"daily","only_publish_lessons_with_verified_source_guides":True},
          "weekly_assessment":{"required":True,"assess_each_eligible_source_at_least_weekly":True,"mastery_requires_practical_evidence":True},
          "guide_requirements":["executive summary","detailed explanation","prerequisites","concept map","step-by-step worked examples","original exercises","capstone","knowledge checks and answer key","source citations and license","hands-on acceptance tests"],
          "commercial_readiness":{"sales_rep_for_relevant_tasks":True,"verified_offer_and_capability_required":True,"human_approval_before_contact_or_bid":True},
          "community_service":{"include_homelessness_veterans_and_benefits_pathways":True,"partner_led_and_consent_based":True,"never_promise_benefits_or_awards":True}
        })
    return {
      "schema":"dreamco.buddy_self_authoring_bootcamp.v1",
      "status":"curriculum_map_generated_source_guides_and_model_study_not_yet_executed",
      "coverage":{"domain_divisions":len(rows),"hugging_face_subject_terms":len(subjects),"onet_occupations":occupations,"onet_task_statements":tasks,
        "source_discovered":sources.get("discovered",0),"source_guide_authoring_eligible":sources.get("guide_authoring_eligible",0),"source_rights_pending":sources.get("rights_pending",0)},
      "divisions":rows,
      "buddy_bootcamp_builder_loop":{
        "trigger":"after_each_weekly_learning_cycle_and_on_material_source_or_taxonomy_change",
        "steps":["inventory newly discovered and changed sources","verify source revision license and permissions","author detailed original study guides with source citations","validate each guide against schema and rights evidence","map guides to the 55 divisions and 65 MasterBot capability routes","build prerequisite graphs and five-lessons-per-day schedules","create exercises projects and capstones","run weekly per-source and transfer assessments","record strengths gaps and remediation","have Buddy propose a revised next bootcamp version","run regression and safety checks","publish versioned bootcamp and human-review report"],
        "promotion_rule":"A Buddy-generated bootcamp version is a draft until source, rights, quality, benchmark and human governance checks pass.",
        "ownership_rule":"DreamCo owns its original authored curriculum artifacts and code subject to applicable law; upstream facts, data, code, model weights and third-party materials retain their original licenses and attribution.",
        "training_rule":"Studying/retrieval is not weight training. Fine-tuning or distillation requires explicit training rights, approved data manifests, compute budget, baseline, holdout evaluation and rollback."
      },
      "truth_boundary":"This artifact is a curriculum map and authoring plan. It is not proof that detailed guides were generated, Buddy studied them, model weights changed, or mastery was achieved."
    }

def main()->int:
    p=argparse.ArgumentParser()
    p.add_argument("--division-source",required=True); p.add_argument("--hf-taxonomy",required=True)
    p.add_argument("--onet",required=True); p.add_argument("--source-queue",required=True)
    p.add_argument("--workforce",required=True); p.add_argument("--government",required=True)
    p.add_argument("--out-dir",required=True); a=p.parse_args()
    read=lambda x:json.loads(Path(x).read_text(encoding="utf-8"))
    names=division_names(Path(a.division_source).read_text(encoding="utf-8"))
    result=build(names,read(a.hf_taxonomy),read(a.onet),read(a.source_queue),read(a.workforce),read(a.government))
    out=Path(a.out_dir); out.mkdir(parents=True,exist_ok=True)
    (out/"buddy-self-authoring-bootcamp.json").write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    lines=["# Buddy self-authoring bootcamp","",f"- Domain divisions: {result['coverage']['domain_divisions']}",f"- Hugging Face task/subject terms: {result['coverage']['hugging_face_subject_terms']}",f"- O*NET occupations in import: {result['coverage']['onet_occupations']}",f"- O*NET task statements: {result['coverage']['onet_task_statements']}",f"- Sources discovered: {result['coverage']['source_discovered']}",f"- Rights-cleared guide candidates: {result['coverage']['source_guide_authoring_eligible']}","", "Buddy must author detailed guides, study them, pass weekly assessments, and propose the next bootcamp version. This plan is not evidence that those actions have run."]
    (out/"buddy-self-authoring-bootcamp.md").write_text("\n".join(lines)+"\n",encoding="utf-8")
    print(json.dumps(result["coverage"],indent=2))
    return 0
if __name__=="__main__": raise SystemExit(main())
