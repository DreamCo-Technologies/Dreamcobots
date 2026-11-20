import importlib.util
import json
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

    def test_safety_controls_are_explicit(self):
        plan = module.build_plan()
        self.assertFalse(plan["automatic_promotion"])
        self.assertFalse(plan["automatic_weight_merging"])
        self.assertTrue(plan["production_safety_hold"])


if __name__ == "__main__":
    unittest.main()
