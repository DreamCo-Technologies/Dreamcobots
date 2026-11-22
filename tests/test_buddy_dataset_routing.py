import json
import unittest
from pathlib import Path
from tools.build_buddy_dataset_routes import build, equivalent_payload

ROOT = Path(__file__).resolve().parents[1]

class BuddyDatasetRoutingTests(unittest.TestCase):
    def test_check_ignores_only_the_informational_generated_timestamp(self):
        expected = {"schema": "dreamco.buddy_dataset_routes.v1", "generated_at": "2026-01-01T00:00:00+00:00", "routes": []}
        same_data_new_timestamp = {**expected, "generated_at": "2026-11-22T17:00:00+00:00"}
        self.assertTrue(equivalent_payload(same_data_new_timestamp, expected))
        changed_data = {**same_data_new_timestamp, "routes": [{"masterbot_id": 1}]}
        self.assertFalse(equivalent_payload(changed_data, expected))

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
        self.assertIn("search_persistent_local_dreamco_dataset_hub", policy["unknown_problem_router"]["sequence"])
        self.assertIn("search_authorized_huggingface_dataset_and_model_catalogs", policy["unknown_problem_router"]["sequence"])
        self.assertTrue(policy["unknown_problem_router"]["never_claim_unknown_solved_without_holdout_evidence"])

    def test_dataset_hub_connectors_and_training_runner_are_declared(self):
        policy = json.loads((ROOT / "config/buddy-dataset-routing-policy.json").read_text())
        runtime = policy["runtime_components"]
        self.assertEqual(runtime["dataset_hub"]["catalog"], "SQLite")
        self.assertEqual(runtime["source_adapters"]["huggingface_models"], "opt-in metadata search")
        self.assertEqual(runtime["training_runner"]["methods"], ["sft", "lora"])
        self.assertFalse(runtime["training_runner"]["automatic_execution"])
        self.assertFalse(runtime["training_runner"]["execution_verified"])
        self.assertEqual(runtime["cross_model_benchmark"]["metric"], "bits_per_utf8_byte")
        self.assertFalse(runtime["cross_model_benchmark"]["execution_verified"])

    def test_daily_discovery_and_legal_use_gates_are_declared(self):
        policy = json.loads((ROOT / "config/buddy-dataset-routing-policy.json").read_text())
        discovery = policy["automatic_discovery"]
        self.assertTrue(discovery["enabled"])
        self.assertEqual(discovery["lanes_per_daily_run"], 5)
        self.assertEqual(discovery["full_rotation_daily_runs"], 13)
        self.assertIn("Zenodo", " ".join(discovery["sources"]))
        self.assertFalse(discovery["download_files"])
        legal = policy["legal_use_policy"]
        self.assertFalse(legal["auto_approval"])
        self.assertIn("explicit_ai_training_permission", legal["required_for_training_candidate"])

    def test_holdout_and_compute_gates_are_preserved(self):
        policy = json.loads((ROOT / "config/buddy-dataset-routing-policy.json").read_text())
        self.assertEqual(policy["hard_gates"]["benchmark_holdout"], "EVALUATION_ONLY_NEVER_TRAIN")
        self.assertEqual(policy["hard_gates"]["paid_compute"], "REQUIRES_EXPLICIT_BUDGET_APPROVAL")
        self.assertFalse(policy["defaults"]["automatic_production_weight_updates"])

if __name__ == "__main__":
    unittest.main()
