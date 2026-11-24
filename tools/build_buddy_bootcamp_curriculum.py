"""Build a 65-division Buddy Bootcamp curriculum from the complete HF task taxonomy."""
from __future__ import annotations
import argparse,hashlib,json,re
from pathlib import Path
from typing import Any

ROOT=Path(__file__).resolve().parents[1]
MASTERBOTS=ROOT/"config/masterbot-65-registry.json"
TASKS=ROOT/"config/huggingface-task-taxonomy.json"
PACKS=ROOT/"config/hf-capability-download-map.json"
DIVISION_MAP=ROOT/"config/generated/division-huggingface-taxonomy-map.json"
SERVING_POLICY=ROOT/"config/buddy-model-serving-policy.json"
SOURCE_REGISTRY=ROOT/"config/dreamco-training-source-registry.json"
OUTPUT=ROOT/"config/generated/buddy-bootcamp-curriculum.json"

CORE_MODULES=[
 {"id":"foundations","name":"AI and machine-learning foundations","outcomes":["understand supervised, self-supervised and reinforcement learning","read model cards and training/evaluation documentation"],"practice":["reproduce a baseline","record assumptions and provenance"]},
 {"id":"data-engineering","name":"Dataset discovery, quality and governance","outcomes":["discover task-aligned datasets","validate splits, hashes, duplicates, PII and provenance","review license and training rights"],"practice":["build a versioned dataset card","keep train, validation, test and private holdout isolated"]},
 {"id":"instruction","name":"Instruction following and text generation","outcomes":["instruction fidelity","structured output","question answering and summarization"],"practice":["SFT on approved examples","measure task success and refusal correctness"]},
 {"id":"reasoning","name":"Reasoning, mathematics and decision quality","outcomes":["multi-step reasoning","calculation verification","uncertainty calibration"],"practice":["compare against deterministic reference answers","record error categories"]},
 {"id":"retrieval","name":"Embeddings, retrieval and reranking","outcomes":["semantic retrieval","feature extraction","reranking and citation grounding"],"practice":["build retrieval test sets","measure recall, precision and groundedness"]},
 {"id":"agents-tools","name":"Tool use and autonomous workflows","outcomes":["tool selection","function calling","permission checks and action verification"],"practice":["sandbox tools","test approval gates and idempotency"]},
 {"id":"multimodal","name":"Vision, audio, speech and video","outcomes":["image understanding and generation tasks","speech recognition and synthesis","multimodal grounding"],"practice":["evaluate each supported modality separately","record modality-specific limits"]},
 {"id":"multilingual","name":"Translation and multilingual capability","outcomes":["translation quality","language identification","cross-lingual robustness"],"practice":["stratify by language and script","avoid treating English-only scores as universal"]},
 {"id":"safety-privacy","name":"Safety, privacy and governance","outcomes":["safe refusal behavior","privacy leakage prevention","license, consent and provenance"],"practice":["red-team with approved test cases","verify canaries never appear in outputs"]},
 {"id":"reverse-engineering","name":"Authorized reverse engineering and software analysis","outcomes":["inspect permitted code and interfaces","map data flow and dependencies","reproduce documented behavior"],"practice":["use owned or explicitly authorized targets","do not bypass access controls or extract secrets"]},
 {"id":"training-distillation","name":"SFT, LoRA, distillation and checkpoint lifecycle","outcomes":["select pinned base models","train isolated division adapters or weights","record teacher/student lineage"],"practice":["save periodic checkpoints and tokenizer snapshots","verify hashes and reproducibility"]},
 {"id":"evaluation","name":"Benchmarking and model evaluation","outcomes":["baseline comparison","domain and general capability evaluation","safety, privacy, robustness and regression"],"practice":["run three independent seeds","keep private holdout out of training"]},
 {"id":"mlops-runtime","name":"MLOps, deployment and observability","outcomes":["model registry and versioning","serving health and latency","resource/cost accounting and rollback"],"practice":["canary deployment only after certification","monitor each division endpoint independently"]}
]

def _read(path:Path)->dict[str,Any]:
    return json.loads(path.read_text(encoding="utf-8"))

def _slug(value:str)->str:
    return re.sub(r"[^a-z0-9]+","-",value.casefold()).strip("-")

def build_curriculum(masterbots:dict,tasks:dict,packs:dict,division_map:dict,serving:dict,
                     source_hashes:dict[str,str]|None=None,
                     source_registry:dict[str,Any]|None=None)->dict[str,Any]:
    divisions=masterbots.get("divisions",[])
    task_families=tasks.get("task_families",[])
    capability_packs=packs.get("packs",[])
    routes={int(x["masterbot_id"]):x for x in division_map.get("routes",[])}
    if len(divisions)!=65 or len(routes)!=65: raise ValueError("canonical 65-division registry and taxonomy map required")
    task_ids=[]
    for family in task_families:
        if not isinstance(family,dict):
            raise ValueError("each Hugging Face task family must be a structured record")
        task_id=family.get("id")
        if not isinstance(task_id,str) or not task_id.strip():
            raise ValueError("each Hugging Face task family must have a non-empty stable id")
        task_ids.append(task_id.strip())
    if len(task_families)!=37 or len(set(task_ids))!=37:
        raise ValueError("expected 37 unique Hugging Face task family IDs")
    source_registry=source_registry or {}
    source_families=source_registry.get("source_families",[])
    source_ids=[item.get("id") for item in source_families if isinstance(item,dict)]
    required_source_families={"dreamco_original","official_technical_docs","public_dataset_catalogs",
        "research_metadata","code_and_software","government_and_standards","user_contributed",
        "teacher_outputs","evaluation_only"}
    if not required_source_families.issubset(set(source_ids)) or len(source_ids)!=len(set(source_ids)):
        raise ValueError("training source registry must contain all nine unique governed source families")
    if len(capability_packs)!=10 or len({x["id"] for x in capability_packs})!=10:
        raise ValueError("expected 10 unique Hugging Face capability packs")
    all_tasks=[{
        "task_family":family["id"],"family":family.get("family"),"modality":family.get("modality"),
        "pipeline_tag":family.get("pipeline_tag"),"description":family.get("description",""),
        "task_id_status":family.get("task_id_status"),
        "required_for_every_division":True,
        "discovery_source":"Hugging Face Hub task taxonomy",
        "training_rights":"REVIEW_REQUIRED","training_status":"NOT_RUN"
    } for family in task_families]
    pack_index={x["id"]:x for x in capability_packs}
    route_records=[]
    for division in sorted(divisions,key=lambda x:int(x["id"])):
        mid=int(division["id"]);route=routes[mid]
        slug=_slug(division["name"])
        pack_ids=list(route.get("capability_pack_ids") or [])
        unknown=set(pack_ids)-set(pack_index)
        if unknown: raise ValueError(f"unknown capability packs for MasterBot {mid}: {sorted(unknown)}")
        route_records.append({
          "masterbot_id":mid,"division_name":division["name"],"division_slug":slug,
          "model":{"model_name":f"dreamco/{slug}-mini","model_version":"0.1.0",
            "status":"SPECIFIED_NOT_TRAINED","weights_path":f"artifacts/division-models/masterbot-{mid:03d}-{slug}/v0.1.0/weights",
            "checkpoints_path":f"artifacts/division-models/masterbot-{mid:03d}-{slug}/v0.1.0/checkpoints",
            "tokenizer_path":f"artifacts/division-models/masterbot-{mid:03d}-{slug}/v0.1.0/tokenizer"},
          "huggingface":{"discovery_lane_id":route["lane_id"],
            "subject_terms":route.get("subject_terms",[]),
            "candidate_pipeline_tags":route.get("candidate_pipeline_tags",[]),
            "capability_pack_ids":pack_ids,
            "domain_crosswalk":route["domain_crosswalk"],
            "owner_review_required":bool(route["domain_crosswalk"].get("owner_review_required",True)),
            "owner_approval":route["domain_crosswalk"].get("owner_approval")},
          "curriculum":{"global_task_families":all_tasks,
            "specialization_pipeline_tags":route.get("candidate_pipeline_tags",[]),
            "capability_pack_details":[{"id":pid,"capability_ids":pack_index[pid].get("capability_ids",[]),
              "hf_model_pipeline":pack_index[pid].get("hf_model_pipeline"),
              "hf_dataset_task":pack_index[pid].get("hf_dataset_task")} for pid in pack_ids],
            "core_modules":[x["id"] for x in CORE_MODULES]},
          "resources":{"database_schema":f"dreamco_division_{mid:03d}",
            "dataset_discovery_lane":route["lane_id"],"object_store_prefix":f"dreamco/masterbot-{mid:03d}/",
            "teacher_routing_policy":"buddy_teacher_coordinator",
            "training_methods":["sft","lora"],"benchmark_suite":"division-independent-v1",
            "training_source_family_ids":sorted(required_source_families),
            "shared_foundation_data_policy":"immutable_source_reference_materialized_per_division",
            "private_division_data_shared":False,"private_holdouts_shared":False,
            "readiness":"REQUIREMENTS_DEFINED_NOT_PROVISIONED"},
          "lifecycle":{"dataset":"NOT_INGESTED","training":"NOT_RUN","benchmark":"NOT_RUN",
            "certification":"NOT_CERTIFIED","runtime":"NOT_DEPLOYED"}})
    return {"schema":"dreamco.buddy_bootcamp_curriculum.v1","curriculum_version":"1.0.0",
      "status":"CURRICULUM_SPECIFIED_NOT_TRAINED","teacher_model_role":{
        "name":"Buddy Teacher Coordinator","status":"ORCHESTRATOR_NOT_A_CLAIM_OF_A_TRAINED_TEACHER_MODEL",
        "responsibilities":["curriculum planning","route to approved teacher models","teacher quality evaluation",
          "student training orchestration","benchmark and evidence review"],
        "provider_policy":serving.get("policy",{}),
        "teacher_outputs_are_untrusted":True,"paid_teacher_calls_require_per_request_approval":True,
        "teacher_output_training_rights_review_required":True},
      "coverage":{"divisions":65,"task_families":len(all_tasks),"capability_packs":len(capability_packs),
        "training_source_families":len(source_families),
        "dataset_discovery_dimensions":tasks.get("dataset_discovery_dimensions",[]),
        "model_discovery_dimensions":tasks.get("model_discovery_dimensions",[]),
        "core_modules":len(CORE_MODULES),"division_task_coverage":65*len(all_tasks)},
      "global_task_families":all_tasks,"capability_pack_catalog":capability_packs,
      "training_resource_catalog":{"source_families":source_families,
        "discovery_adapters":source_registry.get("discovery_adapters",{}),
        "quality_gates":source_registry.get("quality_gates",[]),
        "training_methods":source_registry.get("training_methods",[]),
        "division_policy":source_registry.get("division_policy",{})},
      "core_modules":CORE_MODULES,"divisions":route_records,
      "rights_policy":tasks.get("rights_policy",{}),
      "source_hashes":source_hashes or {},
      "truth_boundary":"This curriculum routes discovery and learning plans only. It does not authorize dataset use, download models, run training, certify models, or deploy runtime endpoints."}

def validate_curriculum(payload:dict[str,Any])->None:
    if payload.get("schema")!="dreamco.buddy_bootcamp_curriculum.v1": raise ValueError("invalid curriculum schema")
    if payload.get("coverage",{}).get("divisions")!=65 or len(payload.get("divisions",[]))!=65:
        raise ValueError("curriculum must cover all 65 divisions")
    tasks=payload.get("global_task_families",[])
    if len(tasks)!=37: raise ValueError("curriculum must cover all 37 HF task families")
    source_families=payload.get("training_resource_catalog",{}).get("source_families",[])
    if len(source_families)!=9: raise ValueError("curriculum must cover all nine governed training source families")
    if payload.get("coverage",{}).get("capability_packs")!=10: raise ValueError("all 10 capability packs required")
    model_names=[x["model"]["model_name"] for x in payload["divisions"]]
    if len(set(model_names))!=65: raise ValueError("division model names must be unique")
    for division in payload["divisions"]:
        if len(division["curriculum"]["global_task_families"])!=37:
            raise ValueError("every division must receive all global task families")
        if len(division["resources"].get("training_source_family_ids",[]))!=9:
            raise ValueError("every division must receive the governed multi-source training catalog")
        if division["resources"].get("private_division_data_shared") is not False or division["resources"].get("private_holdouts_shared") is not False:
            raise ValueError("private division data and holdouts must remain isolated")
        if division["model"]["status"]!="SPECIFIED_NOT_TRAINED":
            raise ValueError("curriculum generation cannot fabricate model training status")
        if division["huggingface"]["owner_review_required"] and division["huggingface"]["owner_approval"] is None:
            if division["huggingface"]["domain_crosswalk"]["mapping_status"] not in {"unresolved","proposed_exact_name_match"}:
                raise ValueError("unapproved domain mapping cannot be treated as final")

def main()->int:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check",action="store_true")
    parser.add_argument("--out",type=Path,default=OUTPUT)
    args=parser.parse_args()
    inputs=[MASTERBOTS,TASKS,PACKS,DIVISION_MAP,SERVING_POLICY,SOURCE_REGISTRY]
    hashes={p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs}
    payload=build_curriculum(*[_read(p) for p in inputs[:5]],source_hashes=hashes,
        source_registry=_read(SOURCE_REGISTRY))
    validate_curriculum(payload)
    rendered=json.dumps(payload,indent=2,ensure_ascii=False)+"\n"
    if args.check:
        if not args.out.exists() or args.out.read_text(encoding="utf-8")!=rendered:
            raise SystemExit("Buddy Bootcamp curriculum is stale; regenerate with tools/build_buddy_bootcamp_curriculum.py")
        print(json.dumps({"ok":True,**payload["coverage"]},indent=2));return 0
    args.out.parent.mkdir(parents=True,exist_ok=True);args.out.write_text(rendered,encoding="utf-8")
    print(json.dumps({"written":args.out.relative_to(ROOT).as_posix(),**payload["coverage"]},indent=2));return 0

if __name__=="__main__": raise SystemExit(main())
