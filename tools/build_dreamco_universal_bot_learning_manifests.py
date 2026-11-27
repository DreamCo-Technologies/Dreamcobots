#!/usr/bin/env python3
"""Build individualized 100-slot learning manifests for DreamCo's complete bot fleet.

Reads the canonical generated bot manifest and the preserved original-bot sources.
This generates curricula and manifests only; it does not fetch third-party data,
create synthetic examples, initialize weights, train models, or deploy bots.
"""
from __future__ import annotations
import argparse, hashlib, json, re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
FLEET = ROOT / "config/bots/bot-manifests.generated.json"
MASTERBOTS = ROOT / "config/masterbot-65-registry.json"
RECONCILIATION = ROOT / "config/generated/division-reconciliation.json"
BUSINESS = ROOT / "config/dreamco-business-bot-55-roster.json"
POLICY = ROOT / "config/dreamco-universal-bot-learning-foundry-policy.json"
OUTPUT = ROOT / "config/generated/dreamco-universal-bot-learning-index.json"
MANIFEST_DIR = ROOT / "config/generated/dreamco-bot-learning-manifests"

TAXONOMY_TOPICS = [
 "role mission and scope","task statements and work activities","required skills and competencies",
 "knowledge and proficiency levels","tools and technology exposure","human versus AI task boundaries",
 "human versus robot task boundaries","handoff and escalation conditions","safety-critical task identification",
 "decision rights and approval limits","inputs and outputs","workflow dependencies","exception categories",
 "service-level expectations","quality criteria","accessibility and inclusion","privacy-sensitive activities",
 "security-sensitive activities","jurisdiction and locale","industry vocabulary","customer and stakeholder roles",
 "workload and frequency","risk and impact classification","success measures","role-specific competency map"
]
PLAYBOOK_TOPICS = [
 "standard operating procedure","intake and qualification","preconditions and prerequisites",
 "step-by-step workflow","decision tree and exception handling","templates and structured forms",
 "calculations and business rules","compliance checklist","privacy and records policy","security controls",
 "customer communication standards","tool and API contracts","data schema and validation",
 "handoff and collaboration rules","quality assurance checklist","error recovery procedure",
 "audit trail and evidence requirements","cost and resource estimation","service-level and escalation rules",
 "versioning and change management","accessibility and localization","fraud and abuse prevention",
 "human approval checkpoints","rollback and continuity procedure","reporting and analytics",
 "integration contract","edge-case playbook","negative examples and prohibited actions",
 "domain-specific glossary","capability boundary and limitation"
]
SCENARIO_TOPICS = [
 "routine happy-path task","missing-input recovery","ambiguous-request clarification","conflicting-instructions resolution",
 "invalid-data rejection","schema-validation failure","permission-denied handling","human-escalation scenario",
 "cross-team handoff","time-sensitive request","high-volume workload","low-resource operation",
 "adversarial or manipulative input","privacy-sensitive input","safety-critical edge case","tool timeout and retry",
 "duplicate request and idempotency","partial completion recovery","unexpected external API response","out-of-distribution case",
 "calculation verification","customer complaint","policy change","multilingual input","accessibility constraint"
]
EVAL_TOPICS = [
 "input/output JSON contract","required-field and type validation","golden deterministic unit tests",
 "negative and boundary tests","unseen transfer task","domain accuracy benchmark","task completion benchmark",
 "tool-selection accuracy","tool-argument correctness","permission and approval enforcement",
 "privacy leakage canary test","prompt-injection resistance","uncertainty and abstention calibration",
 "latency and memory profiling","cost-per-task measurement","reliability and retry test",
 "regression comparison","independent holdout evaluation","human review rubric","model card and provenance audit"
]
STAGE = [
 ("01_task_taxonomy", TAXONOMY_TOPICS),
 ("02_domain_playbooks", PLAYBOOK_TOPICS),
 ("03_synthetic_scenarios", SCENARIO_TOPICS),
 ("04_evaluation_harnesses", EVAL_TOPICS),
]

def read(path: Path) -> dict[str, Any]:
    if not path.is_file(): raise FileNotFoundError(f"Required source missing: {path.relative_to(ROOT)}")
    return json.loads(path.read_text(encoding="utf-8"))

def slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.casefold()).strip("-")[:80] or "unnamed"

def make_slots(bot_id: str, name: str, division: str, focus: list[str], source_refs: list[str]) -> list[dict[str, Any]]:
    slots=[]
    for stage_id, topics in STAGE:
        for topic in topics:
            n=len(slots)+1
            slots.append({
                "resource_id": f"{bot_id}_R{n:03d}",
                "stage": stage_id,
                "topic": topic,
                "personalized_scope": {"bot_name":name,"division":division,"focus_tags":focus},
                "source_query": f"{name} {division} {topic}",
                "source_refs": list(source_refs),
                "resource_kind": "original_lesson_or_rights_reviewed_reference",
                "slot_status": "PLANNED_NOT_CREATED",
                "third_party_rights": "UNKNOWN_BLOCKED",
                "training_permission": "BLOCKED_UNTIL_REVIEW",
                "data_path": None
            })
    if len(slots)!=100: raise ValueError("Each individualized manifest must contain exactly 100 slots")
    return slots

def model_profile(capability_count: int, source_kind: str) -> dict[str, Any]:
    target = 45_000_000 if capability_count >= 12 else 18_500_000
    return {
        "family": "45M-edge-agent" if target==45_000_000 else "18.5M-domain-micro-model",
        "target_parameters": target,
        "parameter_count_status": "TARGET_NOT_VERIFIED_BY_INSTANTIATED_TENSORS",
        "weights_included": False,
        "weights_status": "UNTRAINED_BLUEPRINT_READY_FOR_TRAINING",
        "selection_reason": "Broad capability surface; 45M target requires benchmark confirmation." if target==45_000_000 else "Focused specialist scope; 18.5M target is the initial efficiency hypothesis.",
        "source_kind": source_kind
    }

def build_bot_manifest(record: dict[str, Any], source_kind: str) -> dict[str, Any]:
    bot_id=str(record["bot_id"]); name=str(record["name"]); division=str(record["division"])
    focus=[str(x) for x in record.get("focus_tags",[]) if x]
    caps=int(record.get("capability_count",0))
    sources=[str(x) for x in record.get("source_refs",[]) if x]
    return {
        "schema":"dreamco.individual_bot_learning_manifest.v1",
        "bot_id":bot_id,"name":name,"division":division,"source_kind":source_kind,
        "source_refs":sources,"identity_status":record.get("identity_status","SOURCE_REGISTERED_REVIEW_REQUIRED"),
        "learning_division":True,
        "model":model_profile(caps,source_kind),
        "curriculum":{"resource_slot_count":100,"stages":[{"id":s,"count":len(t)} for s,t in STAGE],
            "synthetic_example_target":10000,"synthetic_examples_status":"TARGET_NOT_GENERATED",
            "mastery_stages":["source_and_rights_review","skill_extraction","original_lesson_authored","guided_example","sandbox_lab","automated_tests","unseen_transfer_task","human_review_when_required","capability_registered","division_routed"]},
        "resources":make_slots(bot_id,name,division,focus,sources),
        "privacy":{"private_data_shared_across_divisions":False,"private_holdout_used_for_training":False},
        "execution":{"production_enabled":False,"external_actions_require_owner_approval":True,"sandbox_required":True},
        "truth_boundary":"A generated learning manifest is a plan, not evidence of created lessons, trained weights, benchmark mastery, runtime implementation, or production readiness."
    }

def source_records() -> list[dict[str,Any]]:
    from tools.place_original_bots import parse_category, parse_system
    network=ROOT/"original-bots/autonomous-income-network"
    systems=ROOT/"original-bots/systems"
    rows=[]
    for path in sorted(network.glob("category-*.md")):
        rows.extend(parse_category(path))
    for path in sorted(systems.glob("*.md")):
        rows.append(parse_system(path))
    if len([x for x in rows if x["kind"]=="income_network_bot"])!=200:
        raise ValueError("Original-bot source must resolve to exactly 200 income bots; inspect source tables.")
    if len([x for x in rows if x["kind"]=="major_system"])!=12:
        raise ValueError("Original-bot source must resolve to exactly 12 major systems.")
    return rows

def build() -> tuple[dict[str,Any], list[dict[str,Any]], list[dict[str,Any]]]:
    fleet=read(FLEET); master=read(MASTERBOTS); reconciliation=read(RECONCILIATION); business=read(BUSINESS); policy=read(POLICY)
    bots=fleet.get("bots",[])
    if len(bots)!=fleet.get("summary",{}).get("bots"): raise ValueError("Fleet manifest count does not match its summary.")
    if len(master.get("divisions",[]))!=65: raise ValueError("Expected all 65 canonical MasterBot learning divisions.")
    if len(reconciliation.get("domain_divisions",[]))!=55: raise ValueError("Expected all 55 domain learning divisions.")
    if len(business.get("bots",[]))!=55: raise ValueError("Expected all 55 commercial business micro-bots.")
    records=[]
    for item in bots:
        records.append({"bot_id":"FLEET_"+str(item["slug"]),"name":item["name"],"division":item.get("division") or item.get("primary_domain_owner") or "UNASSIGNED_REVIEW",
            "source_kind":"canonical_fleet",
            "capability_count":int(item.get("caps",0)),"focus_tags":[item.get("category","general"),item.get("engine","unmapped")],
            "source_refs":item.get("sources",[]),"identity_status":"DUPLICATE_REVIEW_REQUIRED" if "duplicate_profile" in item.get("flags",[]) else "CANONICAL_MANIFEST_ENTRY"})
    old=source_records()
    for item in old:
        records.append({"bot_id":"LEGACY_"+slug(item["source"].replace("/","-"))+"_"+str(item.get("index",0) or slug(item["slug"])),
            "source_kind":"legacy_original_bot_or_system",
            "name":item["display_name"],"division":item["primary_division"],"capability_count":len(item.get("capabilities",[])),
            "focus_tags":[item["kind"],item.get("mission","")[:120]],"source_refs":[item["source"]],"identity_status":"HISTORICAL_SOURCE_NOT_RUNTIME_VERIFIED"})
    for item in business["bots"]:
        records.append({"bot_id":item["bot_id"],"name":item["name"],"division":"Business Bot Foundry / "+item["cluster"],
            "source_kind":"commercial_business_microbot",
            "capability_count":8,"focus_tags":item["focus_tags"],"source_refs":["config/dreamco-business-bot-55-roster.json"],"identity_status":"OWNER_SPECIFIED_COMMERCIAL_BLUEPRINT"})
    if len({x["bot_id"] for x in records})!=len(records): raise ValueError("Bot IDs collide; preserve identity and resolve duplicates.")
    manifests=[build_bot_manifest(x,x["source_kind"]) for x in records]
    division_records=[]
    division_manifests=[]
    for item in master["divisions"]:
        division_records.append({"masterbot_id":int(item["id"]),"division":item["name"],"learning_division":True,
            "curriculum_status":"SEVEN_STAGE_PATH_PRESERVED_AND_EXTENDED_BY_100_SLOT_TEMPLATE",
            "model_family_target":"45M-edge-agent","model_status":"BLUEPRINT_TARGET_NOT_TRAINED",
            "resource_slot_template":"shared 100-slot learning template; division-personalized at materialization"})
        division_manifests.append(build_bot_manifest({"bot_id":"MASTERBOT_"+str(int(item["id"])).zfill(2),"name":item["name"],"division":item["name"],
            "capability_count":12,"focus_tags":["masterbot","division-orchestration"],"source_refs":["config/masterbot-65-registry.json"]},"masterbot_learning_division"))
    for item in reconciliation["domain_divisions"]:
        division_manifests.append(build_bot_manifest({"bot_id":"DOMAIN_"+slug(item["name"]),"name":item["name"],"division":item["name"],
            "capability_count":12,"focus_tags":["domain-division","specialist-learning"],"source_refs":["config/generated/division-reconciliation.json"]},"domain_learning_division"))
    index={
        "schema":"dreamco.universal_bot_learning_foundry_index.v1",
        "status":"CURRICULUM_AND_BLUEPRINT_PLAN_ONLY",
        "source_hashes":{p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in [FLEET,MASTERBOTS,RECONCILIATION,BUSINESS,POLICY]},
        "counts":{"canonical_fleet_entries":len(bots),"legacy_income_bots":200,"legacy_major_systems":12,
            "business_micro_bots":len(business["bots"]),"individual_bot_manifests":len(manifests),
            "masterbot_learning_divisions":len(division_records),"domain_learning_divisions":len(reconciliation["domain_divisions"]),
            "division_learning_manifests":len(division_manifests),
            "resource_slots_per_bot":100,"resource_slots_if_materialized":(len(manifests)+len(division_manifests))*100},
        "model_aggregation":{"business_micro_bot_count":55,"business_micro_bot_target_each":18500000,
            "business_micro_bot_aggregate_target":1017500000,"aggregate_is_one_dense_model":False,
            "fleet_parameter_total":"NOT_ASSERTED; mixed-size targets and untrained weights"},
        "router":{"name":"Buddy Semantic Router / Provost","loads_all_models_at_once":False,
            "route_policy":"select minimum necessary approved specialists; enforce primary division, permissions, sandbox, output contracts, evidence and human escalation"},
        "learning_divisions":division_records,
        "domain_learning_divisions":[{"division":x["name"],"learning_division":True,"manifest_path":"config/generated/dreamco-bot-learning-manifests/domain-"+slug(x["name"])+".json"} for x in reconciliation["domain_divisions"]],
        "manifest_paths":[f"config/generated/dreamco-bot-learning-manifests/{slug(x['bot_id'])}.json" for x in records],
        "division_manifest_paths":[f"config/generated/dreamco-bot-learning-manifests/{slug(x['bot_id'])}.json" for x in division_manifests],
        "truth_boundary":"This index is not proof of lessons authored, data ingested, models trained, tests passed, or production deployment."
    }
    return index,manifests,division_manifests

def main() -> int:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check",action="store_true")
    parser.add_argument("--materialize",action="store_true",help="Write one 100-slot JSON manifest per bot to the generated output directory.")
    parser.add_argument("--out",type=Path,default=OUTPUT)
    parser.add_argument("--manifest-dir",type=Path,default=MANIFEST_DIR)
    args=parser.parse_args()
    index,manifests,division_manifests=build()
    rendered=json.dumps(index,indent=2,ensure_ascii=False)+"\n"
    if args.check:
        if not args.out.exists() or args.out.read_text(encoding="utf-8")!=rendered: raise SystemExit("Learning-foundry index is stale.")
        print(json.dumps({"ok":True,**index["counts"]},indent=2)); return 0
    args.out.parent.mkdir(parents=True,exist_ok=True); args.out.write_text(rendered,encoding="utf-8")
    if args.materialize:
        args.manifest_dir.mkdir(parents=True,exist_ok=True)
        for manifest in manifests+division_manifests:
            path=args.manifest_dir/(slug(manifest["bot_id"])+".json")
            path.write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps({"written":args.out.relative_to(ROOT).as_posix(),**index["counts"],"materialized":args.materialize},indent=2))
    return 0

if __name__=="__main__": raise SystemExit(main())
