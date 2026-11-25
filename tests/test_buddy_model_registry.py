from __future__ import annotations

import copy
import unittest
from pathlib import Path

from buddy.modeling.registry import (
    ModelRegistryError,
    load_registry,
    route_model,
    validate_registry,
)


ROOT = Path(__file__).resolve().parents[1]
SHA = "a" * 64
COMMIT = "b" * 40


def eligible_candidate():
    return {
        "model_id": "dreamco/test-candidate",
        "lifecycle_status": "PRODUCTION_VERIFIED",
        "model_card": "models/test/README.md",
        "code_path": "buddy/modeling/tiny_gpt.py",
        "capabilities": ["causal_language_modeling"],
        "lineage": {
            "parent_model_id": None,
            "dataset_card": "config/test-data-card.json",
            "dataset_card_sha256": SHA,
            "dataset_rights_status": "VERIFIED",
            "model_license_status": "VERIFIED",
            "model_license_url": "https://example.com/model-license",
            "model_license_evidence": "model-license-review-123",
            "training_authorization_id": "approval-123",
            "training_run_id": "run-123",
            "base_model_revision": COMMIT,
        },
        "weights": {
            "trained": True,
            "artifact_path": "artifacts/models/test/model.safetensors",
            "artifact_sha256": SHA,
        },
        "route_policy": {"enabled": True},
        "benchmark_evidence": [{
            "benchmark_id": "heldout-causal-lm-v1",
            "baseline_score": 0.70,
            "candidate_score": 0.82,
            "score_direction": "higher_is_better",
            "routing_weight": 1.0,
            "holdout_passed": True,
            "regression_passed": True,
            "provenance_verified": True,
            "dataset_rights_verified": True,
            "independent_review_approved": True,
            "tested_commit_sha": COMMIT,
        }],
    }


class BuddyModelRegistryTests(unittest.TestCase):
    def test_committed_baseline_is_registered_but_never_routed(self):
        registry = load_registry(ROOT / "config" / "buddy-model-registry.json")
        self.assertEqual(len(registry["models"]), 1)
        decision = route_model(registry, "causal_language_modeling")
        self.assertEqual(decision["status"], "BLOCKED_NO_ELIGIBLE_MODEL")
        self.assertIsNone(decision["selected_model_id"])
        self.assertFalse(decision["production_side_effects"])
        reasons = decision["blocked_candidates"][0]["reasons"]
        self.assertIn("route_disabled", reasons)
        self.assertIn("verified_weight_artifact_missing", reasons)
        self.assertIn("dataset_rights_not_verified", reasons)

    def test_complete_rights_lineage_and_benchmark_can_be_routed(self):
        registry = {"schema": "dreamco.buddy.model_registry.v1", "models": [eligible_candidate()]}
        decision = route_model(registry, "causal_language_modeling")
        self.assertEqual(decision["status"], "ELIGIBLE_FOR_ROUTING")
        self.assertEqual(decision["selected_model_id"], "dreamco/test-candidate")
        self.assertAlmostEqual(decision["weighted_relative_improvement"], (0.82 - 0.70) / 0.70)
        self.assertFalse(decision["production_side_effects"])

    def test_missing_training_authorization_blocks_routing(self):
        candidate = eligible_candidate()
        candidate["lineage"]["training_authorization_id"] = None
        decision = route_model({"schema": "dreamco.buddy.model_registry.v1", "models": [candidate]},
                               "causal_language_modeling")
        self.assertEqual(decision["status"], "BLOCKED_NO_ELIGIBLE_MODEL")
        self.assertIn("separate_training_authorization_missing", decision["blocked_candidates"][0]["reasons"])

    def test_benchmark_regression_blocks_routing(self):
        candidate = eligible_candidate()
        candidate["benchmark_evidence"][0]["candidate_score"] = 0.60
        decision = route_model({"schema": "dreamco.buddy.model_registry.v1", "models": [candidate]},
                               "causal_language_modeling")
        self.assertEqual(decision["status"], "BLOCKED_NO_ELIGIBLE_MODEL")
        self.assertIn("benchmark_regression", decision["blocked_candidates"][0]["reasons"])

    def test_lower_is_better_benchmark_uses_correct_direction(self):
        candidate = eligible_candidate()
        evidence = candidate["benchmark_evidence"][0]
        evidence["score_direction"] = "lower_is_better"
        evidence["baseline_score"] = 0.20
        evidence["candidate_score"] = 0.16
        decision = route_model({"schema": "dreamco.buddy.model_registry.v1", "models": [candidate]},
                               "causal_language_modeling")
        self.assertEqual(decision["status"], "ELIGIBLE_FOR_ROUTING")
        self.assertAlmostEqual(decision["weighted_relative_improvement"], 0.20)

    def test_unverified_model_license_blocks_routing(self):
        candidate = eligible_candidate()
        candidate["lineage"]["model_license_status"] = "UNKNOWN"
        decision = route_model({"schema": "dreamco.buddy.model_registry.v1", "models": [candidate]},
                               "causal_language_modeling")
        self.assertEqual(decision["status"], "BLOCKED_NO_ELIGIBLE_MODEL")
        self.assertIn("model_license_not_verified", decision["blocked_candidates"][0]["reasons"])

    def test_duplicate_model_ids_are_rejected(self):
        candidate = eligible_candidate()
        with self.assertRaises(ModelRegistryError):
            validate_registry({"schema": "dreamco.buddy.model_registry.v1",
                               "models": [candidate, copy.deepcopy(candidate)]})


if __name__ == "__main__":
    unittest.main()
