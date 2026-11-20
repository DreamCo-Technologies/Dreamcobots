import json
import unittest
from pathlib import Path
from tools.build_buddy_dataset_routes import build

ROOT = Path(__file__).resolve().parents[1]

class BuddyDatasetRoutingTests(unittest.TestCase):
    def test_all_65_masterbots_receive_a_lane(self):
        result = build()
        self.assertEqual(result["masterbot_count"], 65)
        self.assertEqual(len({x["masterbot_id"] for x in result["routes"]}), 65)
        self.assertTrue(all(x["lane_id"] and x["routing_status"] == "HEURISTIC_DISCOVERY_ONLY" for x in result["routes"]))

    def test_catalog_entries_are_not_training_approved(self):
        candidates = [c for route in build()["routes"] for c in route["candidates"]]
        self.assertTrue(candidates)
        self.assertTrue(all(c["rights_status"] == "UNVERIFIED_DATASET_CARD_AND_TERMS_REQUIRED" for c in candidates))
        self.assertTrue(all(c["training_status"] == "DISCOVERY_ONLY_NOT_TRAINING_APPROVED" for c in candidates))

    def test_unknown_problem_fallback_is_defined(self):
        policy = json.loads((ROOT / "config/buddy-dataset-routing-policy.json").read_text())
        self.assertIn("search_local_dreamco_dataset_index", policy["unknown_problem_router"]["sequence"])
        self.assertIn("search_authorized_huggingface_catalog", policy["unknown_problem_router"]["sequence"])
        self.assertTrue(policy["unknown_problem_router"]["never_claim_unknown_solved_without_holdout_evidence"])

    def test_dataset_hub_connectors_and_training_runner_are_declared(self):
        policy = json.loads((ROOT / "config/buddy-dataset-routing-policy.json").read_text())
        runtime = policy["runtime_components"]
        self.assertEqual(runtime["dataset_hub"]["catalog"], "SQLite")
        self.assertEqual(runtime["source_adapters"]["huggingface_models"], "opt-in metadata search")
        self.assertEqual(runtime["training_runner"]["methods"], ["sft", "lora"])
        self.assertFalse(runtime["training_runner"]["automatic_execution"])
        self.assertFalse(runtime["training_runner"]["execution_verified"])

    def test_holdout_and_compute_gates_are_preserved(self):
        policy = json.loads((ROOT / "config/buddy-dataset-routing-policy.json").read_text())
        self.assertEqual(policy["hard_gates"]["benchmark_holdout"], "EVALUATION_ONLY_NEVER_TRAIN")
        self.assertEqual(policy["hard_gates"]["paid_compute"], "REQUIRES_EXPLICIT_BUDGET_APPROVAL")
        self.assertFalse(policy["defaults"]["automatic_production_weight_updates"])

if __name__ == "__main__":
    unittest.main()
