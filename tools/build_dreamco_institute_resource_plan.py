#!/usr/bin/env python3
"""Route the 100-source Institute catalog into all 65 division learning lanes.

This is a metadata-only plan. It does not fetch resources, grant rights, or train models.
"""
import argparse,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
DIVISIONS=ROOT/"config/masterbot-65-registry.json"
RESOURCES=ROOT/"config/dreamco_institute_resource_registry.json"
EXTRACTION_TARGETS={
 "workforce_taxonomies":["occupation_skill_graphs","task_decomposition","human_robot_ai_allocation_rules","multilingual_skill_crosswalks"],
 "curriculum_and_practice":["competency_prerequisites","project_based_lab_patterns","test_assertion_categories","assessment_rubric_structures"],
 "model_hubs_and_architectures":["architecture_configuration_fields","tokenizer_interfaces","model_card_metadata","evaluation_protocol_patterns"],
 "datasets_and_pedagogy":["lesson_outline_schemas","task_template_categories","synthetic_exercise_blueprints","dataset_split_and_rubric_patterns"],
 "training_and_alignment":["trainer_configuration_patterns","optimization_method_categories","checkpoint_and_reproducibility_contracts","alignment_evaluation_structures"],
 "inference_and_edge":["runtime_interface_patterns","quantization_format_metadata","device_constraint_categories","deployment_test_patterns"],
 "data_clean_room_tooling":["document_parsing_contracts","deduplication_and_quality_rules","pii_and_secret_scan_requirements","data_lineage_schemas"],
 "robotics_and_simulation":["simulation_task_graphs","sensor_actuator_contracts","trajectory_safety_constraints","sim_to_real_evaluation_patterns"],
 "benchmarking_and_trust":["benchmark_task_schemas","metric_and_rubric_definitions","red_team_test_categories","holdout_and_regression_protocols"],
 "mlops_and_delivery":["ci_cd_gate_patterns","model_and_dataset_versioning","sbom_and_provenance_requirements","release_and_rollback_contracts"]
}
ROBOTICS_DIVISIONS={"DreamConstruction","DreamTransport","DreamMaintenance","DreamProduction","DreamProtection","DreamMilitary","DreamAgriculture","DreamScience","DreamPlanetary","DreamWorld","DreamSimulation","DreamVision"}
def build_plan(divisions_doc,resources_doc):
    divisions=divisions_doc.get("divisions",[]); resources=resources_doc.get("resources",[])
    if divisions_doc.get("canonical_count")!=65 or len(divisions)!=65: raise ValueError("expected canonical 65-division registry")
    if resources_doc.get("resource_count")!=100 or len(resources)!=100: raise ValueError("expected 100-source Institute registry")
    ids=[int(d["id"]) for d in divisions]
    if sorted(ids)!=list(range(1,66)): raise ValueError("division IDs must be 1..65")
    resource_ids=[r["id"] for r in resources]
    if len(set(resource_ids))!=100: raise ValueError("resource IDs must be unique")
    all_categories=sorted({r["category"] for r in resources})
    shared={"workforce_taxonomies","curriculum_and_practice","model_hubs_and_architectures","datasets_and_pedagogy","training_and_alignment","inference_and_edge","data_clean_room_tooling","benchmarking_and_trust","mlops_and_delivery"}
    lanes=[]
    for division in sorted(divisions,key=lambda d:int(d["id"])):
        specialist={"robotics_and_simulation"} if division["name"] in ROBOTICS_DIVISIONS else set()
        recommended=sorted(shared|specialist)
        lane_resources=[]
        for resource in resources:
            lane_resources.append({
                "resource_id":resource["id"],
                "name":resource["name"],
                "category":resource["category"],
                "learning_role":"SHARED_FOUNDATION" if resource["category"] in shared else ("SPECIALIST_REFERENCE" if resource["category"] in specialist else "DISCOVERABLE_REFERENCE_ONLY"),
                "rights_status":resource.get("license_status","UNVERIFIED"),
                "training_permission":resource.get("commercial_training_permission","NOT_ESTABLISHED"),
                "quarantine_status":resource.get("quarantine_status","BLOCKED_PENDING_REVIEW"),
                "owner_review_required":True,
                "extraction_targets":EXTRACTION_TARGETS.get(resource["category"],[]),
                "output_policy":"DREAMCO_ORIGINAL_AUTHORED_NO_SOURCE_TEXT_REUSE",
                "source_expression_retained":False,
                "content_acquired":False,
                "training_enabled":False
            })
        lanes.append({
            "division_id":int(division["id"]),
            "division":division["name"],
            "primary_owner":division["name"],
            "task_routing_curriculum":["HUMAN","ROBOT","AI"],
            "recommended_categories":recommended,
            "resource_catalog_visibility":"METADATA_ONLY",
            "resource_count":len(lane_resources),
            "resources":lane_resources,
            "weights_status":"NO_WEIGHTS_FROM_RESOURCE_CATALOG",
            "training_status":"NOT_AUTHORIZED_BY_CATALOG",
            "owner_approval_required":True
        })
    return {
        "schema":"dreamco.institute.division_resource_plan.v1",
        "status":"CATALOG_ROUTING_PLAN_ONLY",
        "division_count":len(lanes),
        "source_count":len(resources),
        "assignment_count":sum(x["resource_count"] for x in lanes),
        "categories":all_categories,
        "policy":{"metadata_only":True,"network_access":False,"downloads":False,"rights_granted":False,"training_started":False,"unknown_rights":"BLOCK","private_holdouts":"NEVER_TRAIN"},
        "divisions":lanes
    }
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument("--output",type=Path,default=ROOT/"artifacts/institute-resource-plan.json");a=p.parse_args()
    plan=build_plan(json.loads(DIVISIONS.read_text(encoding="utf-8")),json.loads(RESOURCES.read_text(encoding="utf-8")))
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(plan,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"status":plan["status"],"divisions":plan["division_count"],"sources":plan["source_count"],"assignments":plan["assignment_count"],"output":str(a.output)}))
if __name__=="__main__":raise SystemExit(main())
