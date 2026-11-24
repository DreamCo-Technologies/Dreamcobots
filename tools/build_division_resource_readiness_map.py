#!/usr/bin/env python3
"""Build a deterministic, discovery-only resource-readiness map for all 65 MasterBots."""
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
REGISTRY=ROOT/"config/masterbot-65-registry.json"
TAXONOMY=ROOT/"config/generated/division-huggingface-taxonomy-map.json"
CROSSWALK=ROOT/"config/generated/masterbot-55-domain-crosswalk.json"
PACKS=ROOT/"config/hf-capability-download-map.json"
ROUTER=ROOT/"config/buddy-model-router.json"
OUTPUT=ROOT/"config/generated/division-resource-readiness-map.json"
OWNER_REVIEW=ROOT/"config/review/masterbot-domain-crosswalk-owner-review.json"

RESOURCE_CONTRACT=json.loads(r'''{"id":"dreamco.division.resource_bundle.v1","truth_status":"requirements_defined_not_provisioned","architecture":"Shared DreamCo infrastructure with isolated per-division namespaces, model identities, dataset lanes, authorization scopes, metrics, and rollback pointers.","model_strategy":"Start with shared, license-reviewed base models plus division-specific adapters or compact specialists. Each division still owns a distinct versioned model identity, checkpoint lineage, benchmark suite, endpoint identity, and release record. Do not claim 65 separately pretrained foundation models.","baseline_requirements":["persistent operational database namespace and schema migrations","versioned dataset catalog, object storage, provenance and rights manifests","teacher and student model candidate catalog with pinned revisions and license review","domain-specific ML curriculum and reproducible sandbox labs","authorized reverse-engineering workflow and clean-room specification practice","rights-cleared teacher-student distillation pipeline","task, privacy, quality, cost and latency-aware model resource routing","domain benchmarks, protected holdouts, safety and regression evaluation","compute planning, resource metering, run observability and rollback"],"readiness_states":["requirements_defined_not_provisioned","configured","connected","validated","certified"],"promotion_rule":"A resource becomes connected or certified only after a real integration test and evidence artifact. A catalog candidate, config entry, or successful workflow alone is not proof of availability."}''')
ML_PRACTICES=json.loads(r'''["problem framing and measurable success criteria","data collection, provenance and consent","data validation, deduplication and quality profiling","label design, annotation agreement and inter-rater reliability","train-validation-test split design and leakage prevention","supervised learning and baseline selection","unsupervised learning and clustering","self-supervised and contrastive learning","feature engineering and representation learning","classification, regression and ranking","recommendation and retrieval","time-series forecasting and anomaly detection","calibration, uncertainty and out-of-distribution detection","neural network optimization and regularization","transformers, attention and sequence modeling","computer vision and OCR","speech recognition, audio understanding and synthesis","multimodal learning and fusion","reinforcement learning and simulation","RAG, embeddings, reranking and knowledge grounding","SFT, LoRA and QLoRA with rights-cleared data","teacher-student response and preference distillation","quantization, pruning and inference optimization","cross-validation, ablations and statistical confidence","robustness, adversarial testing, fairness and subgroup analysis","MLOps, reproducibility, model registry and experiment tracking","drift monitoring, scheduled evaluation and retraining gates","privacy, tenant isolation and secure ML supply chain","model serving, autoscaling, latency and cost optimization","model cards, licensing, governance and incident response"]''')
DATABASE=json.loads(r'''{"logical_isolation":"One stable division namespace and authorization scope per MasterBot; shared physical infrastructure is permitted.","recommended_stack":["PostgreSQL for operational metadata and relational records","pgvector for embeddings where retrieval requires it","PostgreSQL full-text search or dedicated search index for lexical retrieval","SQLite for local sandbox and reproducible offline labs","S3-compatible object storage for immutable datasets, checkpoints and evaluation artifacts"],"required_entities":["division_registry","dataset_manifests","dataset_versions","dataset_rights_reviews","dataset_splits_and_hashes","model_registry","model_versions","teacher_student_lineage","training_jobs","benchmark_runs","resource_allocations","inference_endpoints","approval_events","audit_events"],"controls":["schema migrations","tenant and division row-level authorization","least-privilege service identities","backup and restore tests","encryption in transit and at rest","retention and deletion policy"],"status":"not_provisioned_evidence_required"}''')
DATASETS=json.loads(r'''{"source_types":["DreamCo-original and owner-authorized assets","Hugging Face datasets and model cards","GitHub repositories and releases","OpenML and UCI","government open-data portals","academic repositories and Zenodo","customer-contributed opt-in datasets in isolated tenant lanes","synthetic fixtures clearly labeled as synthetic"],"planes":["public_reference_and_retrieval","dreamco_owned_training","licensed_training","user_contributed_opt_in_training","evaluation_only_holdout"],"gates":["record source URI, author, revision, retrieval date and content hash","review exact dataset card, file-level license and intended-use terms","verify consent, privacy, personal-data and sensitive-data handling","profile quality, duplicates, schema, language and contamination","create immutable train/validation/test manifests and split hashes","keep benchmark answer keys and private holdouts out of training"],"status":"discovery_only_until_rights_quality_and_privacy_approved"}''')
TEACHER=json.loads(r'''{"orchestrator":{"id":"buddy_teacher_coordinator","role":"curriculum, task decomposition, teacher selection and evidence review","status":"orchestration_role_not_a_claim_of_model_weights"},"candidate_policy":"Candidates are catalog references only. Pin exact revision, tokenizer, license, hardware fit, safety profile and benchmark before use.","training_output_policy":"Teacher outputs may be used for training or distillation only when the specific model/provider terms and data rights permit it.","status":"candidate_catalog_not_connected_or_approved"}''')
REVERSE_ENGINEERING=json.loads(r'''{"scope":"Only systems, source code, binaries, APIs, UI sessions, workflows and data the operator owns or is explicitly authorized to assess.","workflow":["confirm authority, scope and allowed test environment","inventory components, dependencies, interfaces and data flows","observe documented behavior with non-sensitive test inputs","record request/response contracts and state transitions","infer schema and workflow behavior from authorized evidence","write a clean-room specification with citations and unknowns","implement an independently authored alternative in an isolated branch","compare behavior using reproducible tests and security review"],"prohibited":["bypassing authentication or access controls","credential extraction or secret harvesting","unauthorized exploitation or persistence","circumventing DRM or technical protection measures","copying protected code, private datasets, trade secrets or proprietary weights without rights"],"status":"practice_and_review_contract_only"}''')
DISTILLATION=json.loads(r'''{"methods":["response distillation","instruction and task demonstration distillation","preference distillation where rights permit","task-specific adapter training","teacher-generated synthetic data with provenance labels"],"required_lineage":["teacher model ID, exact revision and tokenizer","student base model ID, exact revision and tokenizer","teacher/provider terms and output-use permission","source dataset manifest, license and content hashes","filtering, deduplication and contamination report","train/validation/private-holdout split hashes","training code, config, seed, hardware and cost","student checkpoint hash and model card"],"evaluation":["compare student against its baseline and teacher on identical tasks","run domain holdouts, general capability, safety and regression tests","measure latency, throughput, memory and cost","reject if quality, privacy or safety regressions exceed approved thresholds"],"safeguards":["never copy teacher weights unless explicit rights permit","never distill from providers whose terms prohibit it","never use customer-private data across tenants","never train on private benchmark holdouts","paid compute and production promotion require separate approval"],"status":"pipeline_specified_not_running"}''')
MODEL_ROUTING=json.loads(r'''{"objective":"Choose the best eligible model/resource for each task, not simply the largest model.","decision_order":["division and task capability match","first-party certified model if it meets quality and safety floors","approved local/open-weight candidate with pinned revision","external provider only if configured, permitted, consented and approved","safe fallback or human review when no eligible route exists"],"signals":["benchmark quality and confidence","data classification and tenant boundary","license and output-use permissions","latency and availability","token, GPU and storage cost","context length and modality fit","reliability, safety and recent error rate"],"hard_rules":["no paid provider use without explicit per-request approval","no external routing of private customer data without explicit consent and policy approval","no training/distillation from model outputs without explicit rights","provider connectors marked contract_only are not considered live"],"status":"policy_defined_runtime_dispatch_not_asserted"}''')
COMPUTE=json.loads(r'''{"order":["free/local CPU evaluation and tiny baselines","available approved local GPU or self-hosted capacity","approved low-cost hosted compute for eligible experiments","larger paid training only after explicit budget approval"],"measurements":["GPU/CPU type and utilization","VRAM/RAM peak","training and inference duration","tokens per second and throughput","storage and network use","estimated and actual cost"],"controls":["per-division budget and concurrency quota","checkpoint resume and cancellation","job timeout and retry budget","no paid compute by default","sandbox isolation and artifact scanning"],"status":"capacity_and_credentials_require_verification"}''')
EVALUATION=json.loads(r'''{"suites":["division task benchmark","general capability benchmark","retrieval and grounding benchmark","tool-use and workflow benchmark","safety and privacy benchmark","robustness and adversarial benchmark","latency, throughput, memory and cost benchmark","regression and catastrophic-forgetting benchmark"],"evidence":["pinned benchmark version and commit","fixed train/validation/test split hashes","protected private holdout","baseline and candidate scores","repeat-run variance and confidence intervals","human review for high-impact releases"],"status":"suite_requirements_defined_results_not_asserted"}''')
OPERATIONS=json.loads(r'''{"required":["versioned experiment tracking","central model and dataset registry","queue state and dependency tracking","per-division dashboards and alerts","trace IDs across Buddy, model router, jobs and data","release manifest and signed artifact hashes","canary, rollback and incident playbook"],"status":"integration_evidence_required"}''')

def git_blob_sha(content:str)->str:
    raw=content.encode("utf-8")
    return hashlib.sha1(f"blob {len(raw)}\0".encode("ascii")+raw).hexdigest()

def build(registry,taxonomy,crosswalk,packs,router,source_blob_shas):
    bots=registry.get("divisions",[])
    tax_routes={row["masterbot_id"]:row for row in taxonomy.get("routes",[])}
    if len(bots)!=65 or len(tax_routes)!=65 or set(tax_routes)!={row["id"] for row in bots}:
        raise ValueError("resource map must match all 65 canonical MasterBots and taxonomy routes")
    if len(crosswalk.get("domains",[]))!=55 or len(crosswalk.get("masterbots",[]))!=65:
        raise ValueError("expected the 55-domain / 65-MasterBot crosswalk")
    templates={
        "database":DATABASE,"datasets":DATASETS,
        "teacher_models":{**TEACHER,"seed_models_by_capability_pack":packs.get("seed_models",{})},
        "reverse_engineering":REVERSE_ENGINEERING,"distillation":DISTILLATION,
        "model_routing":{**MODEL_ROUTING,"provider_connector_inventory":[{"id":x["id"],"mode":x["mode"],
            "implementation_status":x["implementation_status"],"availability":x["availability"]}
            for x in router.get("connectors",[])]},
        "compute":COMPUTE,"evaluation":EVALUATION,"operations":OPERATIONS
    }
    routes=[]
    for bot in bots:
        tax=tax_routes[bot["id"]]
        mapping=tax["domain_crosswalk"]
        routes.append({
            "masterbot_id":bot["id"],"masterbot_name":bot["name"],
            "resource_bundle_id":f"division-resource-{bot['id']:03d}",
            "readiness_status":"requirements_defined_not_provisioned",
                        "logical_database_namespace":f"dreamco_division_{bot['id']:03d}",
            "dataset_discovery_lane_id":tax["lane_id"],
            "dataset_rights_status":"UNVERIFIED_DISCOVERY_ONLY",
            "dataset_training_approved":False,
            "capability_pack_ids":tax["capability_pack_ids"],
            "domain_mapping":{"mapping_status":mapping.get("mapping_status"),
                "domain_id":mapping.get("domain_id"),"domain_name":mapping.get("domain_name"),
                "owner_review_required":True,"owner_approval":mapping.get("owner_approval"),
                "unresolved":mapping.get("mapping_status")=="unresolved"}
        })
    masterbot_routes={row["masterbot_id"]:row for row in routes}
    domain_routes=[]
    for domain in crosswalk["domains"]:
        masterbot_id=domain.get("masterbot_id")
        linked=masterbot_routes.get(masterbot_id) if masterbot_id is not None else None
        if linked:
            bundle_id=linked["resource_bundle_id"]
            namespace=linked["logical_database_namespace"]
            lane_id=linked["dataset_discovery_lane_id"]
            capabilities=linked["capability_pack_ids"]
            route_type="linked_to_masterbot_resource_bundle"
        else:
            bundle_id=f"domain-resource-{domain['domain_id']}"
            namespace=f"dreamco_domain_{domain['domain_id']}"
            lane_id=f"domain-discovery-{domain['domain_id']}"
            capabilities=["pack.instruct","pack.reason","pack.safety"]
            route_type="standalone_domain_resource_bundle"
        domain_routes.append({
            "domain_id":domain["domain_id"],"domain_name":domain["domain_name"],
            "masterbot_id":masterbot_id,"masterbot_name":domain.get("masterbot_name"),
            "route_type":route_type,"resource_bundle_id":bundle_id,
            "readiness_status":"requirements_defined_not_provisioned",
            "logical_database_namespace":namespace,"dataset_discovery_lane_id":lane_id,
            "capability_pack_ids":capabilities,"dataset_rights_status":"UNVERIFIED_DISCOVERY_ONLY",
            "dataset_training_approved":False,"owner_review_required":True,
            "mapping_status":domain.get("mapping_status"),"owner_approval":domain.get("owner_approval")
        })
    unresolved_bots=[{"masterbot_id":x["masterbot_id"],"masterbot_name":x["masterbot_name"],
        "primary_domain_id":None,"primary_domain_name":None,"candidate_domain_ids":[],
        "resource_bundle_id":f"division-resource-{x['masterbot_id']:03d}",
        "resource_readiness_status":"requirements_defined_not_provisioned",
        "decision":"PENDING_OWNER_REVIEW","review_required":True,"owner_approval":None,
        "evidence":x.get("evidence",[])} for x in crosswalk["masterbots"] if x.get("mapping_status")=="unresolved"]
    unresolved_domains=[{"domain_id":x["domain_id"],"domain_name":x["domain_name"],
        "candidate_masterbot_ids":[],
        "standalone_resource_bundle_id":f"domain-resource-{x['domain_id']}",
        "logical_database_namespace":f"dreamco_domain_{x['domain_id']}",
        "dataset_discovery_lane_id":f"domain-discovery-{x['domain_id']}",
        "resource_readiness_status":"requirements_defined_not_provisioned",
        "decision":"PENDING_OWNER_REVIEW","review_required":True,
        "owner_approval":None,"evidence":x.get("evidence",[])}
        for x in crosswalk["domains"] if x.get("mapping_status")=="unresolved"]
    return {"schema":"dreamco.division_resource_readiness_map.v1",
        "status":"requirements_defined_not_provisioned","source_of_truth":"config/masterbot-65-registry.json",
        "counts":{"masterbots":len(routes),"domain_divisions":len(crosswalk["domains"]),
            "unresolved_masterbot_mappings":len(unresolved_bots),"unassigned_domain_profiles":len(unresolved_domains),"domain_resource_routes":len(domain_routes),
            "standalone_domain_resource_bundles":sum(x["route_type"]=="standalone_domain_resource_bundle" for x in domain_routes)},
        "source_blob_shas":source_blob_shas,"resource_contract":RESOURCE_CONTRACT,
        "machine_learning_practices":ML_PRACTICES,"resource_templates":templates,"routes":routes,"domain_routes":domain_routes,
        "owner_review":{"masterbot_domain_decisions":unresolved_bots,"unassigned_domain_profiles":unresolved_domains},
        "truth":"This map defines resource requirements and candidate references. It does not provision databases, download datasets, connect providers, allocate GPUs, run training, certify teacher models, or prove any division model exists. All unresolved crosswalk mappings remain unassigned until owner approval."}

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check",action="store_true")
    args=parser.parse_args()
    paths={"masterbot_registry":REGISTRY,"taxonomy_map":TAXONOMY,"domain_crosswalk":CROSSWALK,
        "hf_capability_packs":PACKS,"buddy_model_router":ROUTER}
    texts={k:p.read_text(encoding="utf-8") for k,p in paths.items()}
    docs={k:json.loads(v) for k,v in texts.items()}
    hashes={k:git_blob_sha(v) for k,v in texts.items()}
    payload=build(docs["masterbot_registry"],docs["taxonomy_map"],docs["domain_crosswalk"],
        docs["hf_capability_packs"],docs["buddy_model_router"],hashes)
    encoded=json.dumps(payload,ensure_ascii=False,separators=(",",":"))+"\n"
    review_payload={"schema":"dreamco.masterbot_domain_owner_review.v1",
        "status":"pending_owner_review_no_guessed_mappings",
        "source":"config/generated/masterbot-55-domain-crosswalk.json",
        "counts":{"unresolved_masterbot_mappings":len(payload["owner_review"]["masterbot_domain_decisions"]),
            "unassigned_domain_profiles":len(payload["owner_review"]["unassigned_domain_profiles"])},
        "instructions":"Please assign only with authoritative ownership evidence. Empty candidate arrays are intentional; do not infer a mapping from similar names. Record reviewer, evidence, decision date and approval.",
        **payload["owner_review"]}
    review_encoded=json.dumps(review_payload,indent=2,ensure_ascii=False)+"\n"
    if args.check:
        if not OUTPUT.exists() or OUTPUT.read_text(encoding="utf-8")!=encoded:
            raise SystemExit("Division resource readiness map is stale; regenerate it")
        if not OWNER_REVIEW.exists() or OWNER_REVIEW.read_text(encoding="utf-8")!=review_encoded:
            raise SystemExit("MasterBot/domain owner-review queue is stale; regenerate it")
    else:
        OUTPUT.parent.mkdir(parents=True,exist_ok=True)
        OWNER_REVIEW.parent.mkdir(parents=True,exist_ok=True)
        OUTPUT.write_text(encoded,encoding="utf-8")
        OWNER_REVIEW.write_text(review_encoded,encoding="utf-8")
    print(json.dumps({"ok":True,**payload["counts"],"readiness_status":payload["status"]},indent=2))
    return 0
if __name__=="__main__":
    raise SystemExit(main())
