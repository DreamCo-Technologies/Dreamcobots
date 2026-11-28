import importlib.util
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parents[1] / "tools/dreamco_division_mastery_orchestrator.py"
spec = importlib.util.spec_from_file_location("division_mastery", MODULE_PATH)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class DivisionMasteryOrchestratorTests(unittest.TestCase):
    def test_canonical_registry_builds_65_nonempty_lanes(self):
        plan = module.build_plan()
        self.assertEqual(plan["expected_divisions"], 65)
        self.assertEqual(plan["division_lanes"], 65)
        self.assertEqual(len({lane["division_id"] for lane in plan["lanes"]}), 65)
        self.assertTrue(all(lane["goal_ids"] for lane in plan["lanes"]))
        self.assertEqual(plan["resource_bundle_count"],65)
        self.assertEqual(plan["resource_readiness_status"],"requirements_defined_not_provisioned")
        self.assertEqual(plan["capability_evidence_summary"]["canonical_masterbots"], 65)
        self.assertEqual(plan["capability_evidence_summary"]["original_core_domain_divisions"], 45)
        self.assertEqual(plan["capability_evidence_summary"]["promoted_supplemental_domain_profiles"], 10)
        self.assertEqual(len(plan["domain_capability_evidence"]), 55)
        self.assertTrue(all(
            lane["capability_evidence"]["masterbot_id"] == lane["division_id"]
            for lane in plan["lanes"]
        ))
        self.assertEqual(len({lane["resource_bundle_id"] for lane in plan["lanes"]}),65)
        self.assertTrue(all(lane["logical_database_namespace"] and lane["dataset_discovery_lane_id"] for lane in plan["lanes"]))

    def test_every_lane_has_dependency_gated_tasks(self):
        plan = module.build_plan()
        for lane in plan["lanes"]:
            self.assertEqual(lane["task_dag"][1]["depends_on"], ["registry_validation"])
            self.assertEqual(lane["task_dag"][2]["depends_on"], ["registry_validation", "platform_regression_suite"])
            self.assertEqual(lane["task_dag"][-1]["depends_on"], ["division_lane_plan", "division_contract_benchmark", "platform_regression_suite"])
            self.assertTrue(lane["goal_dependency_map"])
            self.assertTrue(all("traceability_status" in item for item in lane["goal_traceability"].values()))

    def test_goal_dependency_graph_is_acyclic(self):
        plan = module.build_plan()
        dependencies = plan["goal_dependency_map"]
        visiting = set()
        visited = set()
        def visit(goal_id):
            if goal_id in visiting:
                return False
            if goal_id in visited:
                return True
            visiting.add(goal_id)
            for dependency in dependencies.get(goal_id, []):
                if not visit(dependency):
                    return False
            visiting.remove(goal_id)
            visited.add(goal_id)
            return True
        self.assertTrue(all(visit(goal_id) for goal_id in dependencies))

    def test_promotion_requires_all_evidence_and_no_regression(self):
        good = {
            "baseline_score": 0.70, "candidate_score": 0.82,
            "holdout_passed": True, "regression_passed": True,
            "provenance_verified": True, "rights_verified": True,
            "review_approved": True, "tested_commit_sha": "abc123"
        }
        eligible, reason = module.promotion_eligible(good)
        self.assertTrue(eligible)
        self.assertIn("human_review", reason)
        bad = dict(good, candidate_score=0.60)
        self.assertEqual(module.promotion_eligible(bad), (False, "candidate_regressed"))
        self.assertEqual(module.promotion_eligible({}), (False, "missing_required_evidence"))


    def test_capability_evidence_inventory_keeps_all_ownership_and_mastery_gates_closed(self):
        inventory = module.build_capability_evidence()
        summary = inventory["summary"]
        self.assertEqual(summary["canonical_masterbots"], 65)
        self.assertEqual(summary["original_core_domain_divisions"], 45)
        self.assertEqual(summary["promoted_supplemental_domain_profiles"], 10)
        self.assertEqual(summary["shared_platform_masterbots"], 20)
        self.assertEqual(summary["pending_core_owner_reviews"], 45)
        self.assertEqual(summary["pending_shared_platform_confirmations"], 20)
        self.assertEqual(summary["pending_supplemental_collaborator_reviews"], 10)
        self.assertEqual(summary["capability_specific_task_runners_registered"], 0)
        self.assertEqual(summary["masterbot_specific_test_paths_mapped"], 0)
        self.assertEqual(summary["benchmark_adapter_entries"], 10)
        self.assertEqual(summary["benchmark_adapter_entries_core_masterbots"], 2)
        self.assertEqual(summary["benchmark_adapter_entries_shared_platform_masterbots"], 8)
        self.assertEqual(summary["benchmark_adapters_verified"], 0)
        self.assertEqual(summary["measured_benchmark_results"], 0)
        self.assertEqual(summary["weights_trained"], 0)
        self.assertEqual(summary["serving_endpoints_deployed"], 0)
        self.assertEqual(summary["mastery_claimed"], 0)

        core = [row for row in inventory["masterbots"] if row["masterbot_id"] <= 45]
        shared = [row for row in inventory["masterbots"] if row["masterbot_id"] >= 46]
        self.assertEqual(len(core), 45)
        self.assertEqual(len(shared), 20)
        self.assertTrue(all(row["ownership"]["approved_primary_domain_id"] is None for row in core))
        self.assertTrue(all(row["ownership"]["owner_approval"] is None for row in core))
        self.assertTrue(all(row["ownership"]["approved_primary_domain_id"] is None for row in shared))
        self.assertTrue(all(row["ownership"]["owner_approval"] is None for row in shared))
        self.assertTrue(all(row["task_runner"]["status"] == "not_registered_in_mastery_orchestrator" for row in inventory["masterbots"]))
        self.assertTrue(all(row["tests"]["domain_specific_status"] == "not_mapped_in_mastery_orchestrator" for row in inventory["masterbots"]))
        self.assertTrue(all(row["benchmark"]["result_status"] == "not_measured" for row in inventory["masterbots"]))
        self.assertTrue(all(row["model"]["weights_trained"] is False for row in inventory["masterbots"]))
        self.assertTrue(all(row["mastery_status"] == "not_claimed" for row in inventory["masterbots"]))

        domains = inventory["domain_profiles"]
        self.assertEqual(len(domains), 55)
        self.assertEqual(sum(row["domain_tier"] == "original_core" for row in domains), 45)
        self.assertEqual(sum(row["domain_tier"] == "promoted_supplemental" for row in domains), 10)
        self.assertTrue(all(row["approved_primary_masterbot_id"] is None for row in domains))
        self.assertTrue(all(row["owner_approval"] is None for row in domains))
        self.assertTrue(all(len(value) == 64 for value in inventory["source_hashes"].values()))
        self.assertEqual(inventory, module.build_capability_evidence())

    def test_safety_controls_are_explicit(self):
        plan = module.build_plan()
        self.assertFalse(plan["automatic_promotion"])
        self.assertFalse(plan["automatic_weight_merging"])
        self.assertTrue(plan["production_safety_hold"])


if __name__ == "__main__":
    unittest.main()
