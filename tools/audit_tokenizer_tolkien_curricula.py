"""Audit tokenizer and Tolkien curriculum structure and rights boundaries."""
from __future__ import annotations
import argparse,json
from pathlib import Path
from typing import Any
ROOT=Path(__file__).resolve().parents[1]


def audit(tokenizer:dict[str,Any],tolkien:dict[str,Any])->dict[str,Any]:
    errors=[]; warnings=[]
    if tokenizer.get("schema")!="dreamco.buddy_tokenizer_curriculum.v1": errors.append("unsupported tokenizer curriculum schema")
    lessons=tokenizer.get("lessons")
    if not isinstance(lessons,list) or len(lessons)!=12: errors.append("tokenizer curriculum must contain exactly 12 lessons"); lessons=lessons if isinstance(lessons,list) else []
    lesson_ids=[row.get("id") for row in lessons if isinstance(row,dict)]
    if lesson_ids!=[f"tok-{i:02d}" for i in range(1,13)]: errors.append("tokenizer lesson IDs must be contiguous tok-01 through tok-12")
    for row in lessons:
        if not isinstance(row,dict): errors.append("tokenizer lessons must be objects"); continue
        lid=row.get("id","<unknown>")
        for field in ("title","outcome","lab","assessment"):
            if not str(row.get(field,"")).strip(): errors.append(f"{lid}: missing {field}")
    refs=tokenizer.get("course_references")
    if not isinstance(refs,list) or len(refs)<4: errors.append("tokenizer track requires at least four attributed course references")
    else:
        for row in refs:
            if not str(row.get("url","")).startswith("https://") or not str(row.get("rights","")).strip():
                errors.append(f"{row.get('title','reference')}: HTTPS URL and rights note required")
    gates=tokenizer.get("gates",{})
    for key in ("rights","evaluation","artifact","model_compatibility","compute","release"):
        if not str(gates.get(key,"")).strip(): errors.append(f"tokenizer gate {key} is required")
    mastery=tokenizer.get("mastery",{})
    if mastery.get("reading_alone_is_not_mastery") is not True or mastery.get("tokenizer_training_is_not_model_weight_training") is not True:
        errors.append("tokenizer mastery policy must distinguish study, tokenizer training and model weight training")
    if tokenizer.get("status")!="curriculum_ready_training_not_executed":
        warnings.append("tokenizer status is not the expected not-executed curriculum state")

    if tolkien.get("schema")!="dreamco.tolkien_study_track.v1": errors.append("unsupported Tolkien study track schema")
    rights=tolkien.get("rights_policy",{})
    for key in ("copyrighted_tolkien_text_ingestion","training_on_copyrighted_tolkien_text","verbatim_text_reproduction"):
        if rights.get(key) is not False: errors.append(f"Tolkien rights policy must keep {key}=false")
    if rights.get("unknown_rights")!="BLOCK": errors.append("Tolkien unknown-rights policy must block")
    curriculum=tolkien.get("curriculum")
    if not isinstance(curriculum,list) or len(curriculum)<8: errors.append("Tolkien core curriculum must contain at least eight study areas"); curriculum=curriculum if isinstance(curriculum,list) else []
    for unit in curriculum:
        if not isinstance(unit,dict) or not unit.get("id") or not unit.get("lessons") or not unit.get("practice"):
            errors.append("every Tolkien curriculum area requires ID, lessons and practice")
    extended=tolkien.get("extended_study_path")
    if not isinstance(extended,list) or len(extended)!=12: errors.append("Tolkien extended study path must contain exactly 12 units"); extended=extended if isinstance(extended,list) else []
    for unit in extended:
        if not isinstance(unit,dict): errors.append("Tolkien extended units must be objects"); continue
        uid=unit.get("id","<unknown>")
        for field in ("title","outcome","lab","assessment","rights_gate"):
            if not str(unit.get(field,"")).strip(): errors.append(f"{uid}: missing {field}")
    integration=tolkien.get("course_integration",{})
    if integration.get("status")=="NEEDS_USER_SUPPLIED_COURSE_REFERENCE" and integration.get("url") is not None:
        errors.append("Tolkien course URL must remain empty until the user supplies or approves a source")
    policy=tolkien.get("mastery_policy",{})
    if policy.get("reading_or_catalog_discovery_is_mastery") is not False or policy.get("unknown_rights")!="BLOCKED":
        errors.append("Tolkien mastery policy must block unknown rights and separate reading from mastery")
    return {"schema":"dreamco.tokenizer_tolkien_curriculum_audit.v1",
        "status":"structural_errors" if errors else "curricula_valid_training_and_mastery_pending",
        "tokenizer_lessons":len(lessons),"tokenizer_references":len(refs) if isinstance(refs,list) else 0,
        "tolkien_core_areas":len(curriculum),"tolkien_extended_units":len(extended),
        "errors":errors,"warnings":warnings,"tokenizer_training_executed":False,
        "model_weight_training_executed":False,"copyrighted_tolkien_text_ingested":False,
        "mastery_awarded":False,
        "truth_boundary":"This audit verifies curriculum structure and rights gates only. It does not execute tokenizer training, model weight training, copyrighted text ingestion, learner assessment or mastery."}


def main()->int:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tokenizer",type=Path,default=ROOT/"config/buddy-tokenizer-training-curriculum.json")
    parser.add_argument("--tolkien",type=Path,default=ROOT/"config/buddy-tolkien-study-track.json")
    parser.add_argument("--output",type=Path)
    args=parser.parse_args()
    report=audit(json.loads(args.tokenizer.read_text(encoding="utf-8")),json.loads(args.tolkien.read_text(encoding="utf-8")))
    encoded=json.dumps(report,indent=2,ensure_ascii=False)+"\n"
    if args.output:
        args.output.parent.mkdir(parents=True,exist_ok=True); args.output.write_text(encoded,encoding="utf-8")
    print(encoded,end="")
    return 1 if report["errors"] else 0

if __name__=="__main__": raise SystemExit(main())
