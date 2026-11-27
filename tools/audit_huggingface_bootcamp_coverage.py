"""Validate the Hugging Face course, ecosystem-module and task-family Bootcamp map."""
from __future__ import annotations
import argparse, json
from pathlib import Path
from typing import Any
ROOT=Path(__file__).resolve().parents[1]


def audit(learning_map:dict[str,Any], taxonomy:dict[str,Any], registry:dict[str,Any])->dict[str,Any]:
    errors=[]; warnings=[]
    courses=learning_map.get("official_courses")
    modules=learning_map.get("ecosystem_modules")
    families=taxonomy.get("task_families")
    tracks=registry.get("tracks")
    if learning_map.get("schema")!="dreamco.buddy_huggingface_full_learning_map.v1": errors.append("unsupported Hugging Face learning map schema")
    if taxonomy.get("schema")!="dreamco.huggingface_task_taxonomy.v1": errors.append("unsupported Hugging Face task taxonomy schema")
    if registry.get("schema")!="dreamco.buddy_course_track_registry.v1": errors.append("unsupported Buddy course track registry schema")
    for name,rows,expected in (("official_courses",courses,12),("ecosystem_modules",modules,18),("task_families",families,37)):
        if not isinstance(rows,list): errors.append(f"{name} must be an array"); continue
        if len(rows)!=expected: errors.append(f"{name} must contain exactly {expected} records")
        ids=[row.get("id") for row in rows if isinstance(row,dict)]
        if len(ids)!=len(rows) or len(ids)!=len(set(ids)): errors.append(f"{name} must have unique non-empty IDs")
    if isinstance(courses,list):
        for row in courses:
            if not isinstance(row,dict): continue
            cid=row.get("id","<unknown>")
            if not str(row.get("title","")).strip() or not str(row.get("topics","")).strip(): errors.append(f"{cid}: title and topics required")
            if not str(row.get("url","")).startswith("https://"): errors.append(f"{cid}: official course URL must use HTTPS")
            if row.get("training_data_authorized") is not False: errors.append(f"{cid}: third-party course content cannot be presumed training data")
            if row.get("transcript_permission")!="not_granted": errors.append(f"{cid}: transcript permission must remain explicit")
            if not str(row.get("assessment","")).strip(): errors.append(f"{cid}: independent assessment plan required")
    if isinstance(modules,list):
        expected_ids=[f"HFEC-{i:02d}" for i in range(1,len(modules)+1)]
        ids=[row.get("id") for row in modules if isinstance(row,dict)]
        if ids!=expected_ids: errors.append("ecosystem modules must be contiguous in HFEC prerequisite order")
        for row in modules:
            if not isinstance(row,dict): continue
            mid=row.get("id","<unknown>")
            for field in ("title","objective","practice","assessment","benchmark"):
                if not str(row.get(field,"")).strip(): errors.append(f"{mid}: missing {field}")
            if row.get("status") not in {"DEFINED_NOT_EXECUTED","queued_not_studied","in_progress"}:
                warnings.append(f"{mid}: verify status is evidence-backed; catalog metadata alone is not completion")
    if isinstance(families,list):
        for row in families:
            if not isinstance(row,dict) or not all(str(row.get(k,"")).strip() for k in ("id","family","modality","description")):
                errors.append("every task family requires id, family, modality and description")
    track_rows=tracks if isinstance(tracks,list) else []
    parsers={row.get("parser"):row for row in track_rows if isinstance(row,dict)}
    if "huggingface_learning_map" not in parsers or parsers["huggingface_learning_map"].get("source")!="config/buddy-huggingface-full-learning-map.json":
        errors.append("course track registry must route the full Hugging Face learning map")
    if "huggingface" not in parsers or parsers["huggingface"].get("source")!="config/huggingface-task-taxonomy.json":
        errors.append("course track registry must route the Hugging Face task taxonomy")
    delivery=learning_map.get("division_delivery",{})
    if delivery.get("canonical_divisions")!=55 or delivery.get("masterbot_lanes")!=65 or delivery.get("shared_foundation_available_to_all") is not True:
        errors.append("Hugging Face shared foundation must cover 55 divisions and 65 MasterBot lanes")
    if learning_map.get("course_count")!=len(courses or []) or learning_map.get("ecosystem_module_count")!=len(modules or []) or taxonomy.get("task_family_count")!=len(families or []):
        errors.append("declared Hugging Face counts must match actual records")
    return {"schema":"dreamco.huggingface_bootcamp_coverage_audit.v1",
        "status":"structural_errors" if errors else "coverage_catalog_valid_content_study_pending",
        "official_course_count":len(courses) if isinstance(courses,list) else 0,
        "ecosystem_module_count":len(modules) if isinstance(modules,list) else 0,
        "task_family_count":len(families) if isinstance(families,list) else 0,
        "division_foundation_count":delivery.get("canonical_divisions"),
        "masterbot_foundation_count":delivery.get("masterbot_lanes"),
        "errors":errors,"warnings":warnings,"course_content_downloaded":False,
        "transcripts_authorized":False,"model_training_authorized":False,
        "study_completed":False,"mastery_awarded":False,
        "truth_boundary":"This audit verifies catalog and routing structure. It does not prove official course content was studied, transcripts were licensed, guides were authored, assessments passed, or model weights were trained."}


def main()->int:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--learning-map",type=Path,default=ROOT/"config/buddy-huggingface-full-learning-map.json")
    parser.add_argument("--taxonomy",type=Path,default=ROOT/"config/huggingface-task-taxonomy.json")
    parser.add_argument("--registry",type=Path,default=ROOT/"config/buddy-course-track-registry.json")
    parser.add_argument("--output",type=Path)
    args=parser.parse_args()
    report=audit(*(json.loads(p.read_text(encoding="utf-8")) for p in (args.learning_map,args.taxonomy,args.registry)))
    encoded=json.dumps(report,indent=2,ensure_ascii=False)+"\n"
    if args.output:
        args.output.parent.mkdir(parents=True,exist_ok=True); args.output.write_text(encoded,encoding="utf-8")
    print(encoded,end="")
    return 1 if report["errors"] else 0

if __name__=="__main__": raise SystemExit(main())
