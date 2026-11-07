from __future__ import annotations

import sys
import unittest

ROOT = __import__("pathlib").Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from buddy.frontier.learning_orchestrator import EvaluationFailure, LearningAction, propose_learning_jobs
from buddy.learning.research_benchmark_bridge import (ResearchBridgeError, learning_points_award,
                                                        record_learning_points_award, summarize_learning_points,
                                                        research_benchmark_failure_to_learning_jobs,
                                                        research_item_to_benchmark_candidate)


class ResearchBenchmarkBridgeTests(unittest.TestCase):
    def finding(self, **updates):
        value = {"title": "Camera gesture recognition on a mobile robot", "source_url": "https://arxiv.org/abs/2601.12345",
                 "source_date": "2026-11-01", "huggingface_category": "Computer Vision", "task_name": "Keypoint Detection",
                 "evidence_type": "real_robot", "demonstrated_capability": "The authors report a gesture classifier evaluated on a mobile robot.",
                 "limitations": "One lab environment and a limited participant group.",
                 "proposed_test": "Evaluate recognition and false activations under held-out lighting and camera angles."}
        value.update(updates)
        return value

    def passing_runs(self):
        return [{"run_id": f"run-{index}", "benchmark_version": "sha256:" + "a" * 64,
                 "verified": True, "task_score_floor_passed": True, "hidden_holdout_passed": True,
                 "regression_passed": True, "safety_passed": True, "native_success": True,
                 "external_assistance": False} for index in range(1, 4)]

    def test_research_becomes_benchmark_candidate_not_score_or_training_data(self):
        candidate = research_item_to_benchmark_candidate(self.finding())
        self.assertEqual(candidate["status"], "needs_fixture_and_adapter_review")
        self.assertIn("gesture_recognition", candidate["benchmark"]["candidate_domains"])
        self.assertIsNone(candidate["benchmark_score"])
        self.assertFalse(candidate["mastery_claimed"])
        self.assertFalse(candidate["training_started"])
        self.assertEqual(candidate["points_awarded"], 0)

    def test_unrecognized_new_huggingface_category_still_maps_to_generic_benchmark(self):
        candidate = research_item_to_benchmark_candidate(self.finding(huggingface_category="New Hub Category"))
        self.assertEqual(candidate["benchmark"]["candidate_domains"], ["task_specific_benchmark"])

    def test_invalid_source_or_evidence_type_is_rejected(self):
        with self.assertRaisesRegex(ResearchBridgeError, "HTTPS"):
            research_item_to_benchmark_candidate(self.finding(source_url="http://example.org/paper"))
        with self.assertRaisesRegex(ResearchBridgeError, "evidence type"):
            research_item_to_benchmark_candidate(self.finding(evidence_type="peer_reviewed_and_proven"))

    def test_verified_code_gap_creates_reverse_engineering_steps_without_execution(self):
        output = research_benchmark_failure_to_learning_jobs({
            "benchmark_id": "code-trace", "run_id": "run-1", "capability": "code_tracking",
            "failure_mode": "missing_trace", "passed": False, "verified": True,
            "regression_passed": False, "safety_passed": True, "evidence_refs": ["reports/run-1.json"],
        })
        job = output["jobs"][0]
        self.assertEqual(job["action"], "reverse_engineer")
        self.assertFalse(job["execution_started"])
        self.assertFalse(job["source_code_copied"])
        self.assertFalse(output["training_started"])
        self.assertTrue(any("commit" in step.lower() for step in job["proposed_steps"]))

    def test_training_gap_creates_gated_distillation_plan_without_changing_weights(self):
        job = propose_learning_jobs([EvaluationFailure("eval-1", "gesture_model_training", "checkpoint_training_gap", 0.5, 0.3)])[0]
        self.assertEqual(job.action, LearningAction.DISTILL)
        self.assertFalse(job.execution_started)
        self.assertFalse(job.model_weights_changed)
        self.assertTrue(any("data rights" in step.lower() for step in job.proposed_steps))

    def test_explicit_training_area_routes_generic_low_score_to_distillation_diagnosis(self):
        output = research_benchmark_failure_to_learning_jobs({
            "benchmark_id": "training-score", "run_id": "run-2", "capability": "camera_perception",
            "failure_mode": "loss_drift", "system_area": "training", "passed": False, "verified": True,
            "evidence_refs": ["reports/training-run-2.json"],
        })
        self.assertEqual(output["jobs"][0]["action"], "distill")
        self.assertFalse(output["jobs"][0]["model_weights_changed"])

    def test_only_explicitly_approved_verified_mastery_awards_non_cash_points_once(self):
        arguments = {"benchmark_id": "gesture-vision", "benchmark_version": "sha256:" + "a" * 64,
                     "capability_id": "gesture_recognition", "owner_approved": True, "runs": self.passing_runs()}
        award = learning_points_award(arguments, user_id="user-1")
        self.assertEqual(award["points"], 10)
        self.assertFalse(award["transferable"])
        self.assertEqual(award["cash_value"], 0)
        self.assertFalse(award["crypto_or_blockchain_transfer"])
        self.assertFalse(award["persisted_to_wallet"])
        duplicate = learning_points_award(arguments, user_id="user-1")
        self.assertEqual(award["idempotency_key"], duplicate["idempotency_key"])
        self.assertEqual(award["event_id"], duplicate["event_id"])

    def test_points_ledger_persists_idempotently_per_user_without_financial_transfer(self):
        award = learning_points_award({"benchmark_id": "gesture-vision", "benchmark_version": "sha256:" + "a" * 64,
            "capability_id": "gesture_recognition", "owner_approved": True, "runs": self.passing_runs()}, user_id="user-1")
        with __import__("tempfile").TemporaryDirectory() as folder:
            first = record_learning_points_award(folder, award)
            second = record_learning_points_award(folder, award)
            self.assertTrue(first["recorded"])
            self.assertTrue(second["duplicate"])
            self.assertEqual(summarize_learning_points(folder, "user-1")["balance"], 10)
            self.assertEqual(summarize_learning_points(folder, "user-2")["balance"], 0)

    def test_points_ledger_rejects_financial_or_path_like_events(self):
        award = learning_points_award({"benchmark_id": "gesture-vision", "benchmark_version": "sha256:" + "a" * 64,
            "capability_id": "gesture_recognition", "owner_approved": True, "runs": self.passing_runs()}, user_id="user-1")
        with __import__("tempfile").TemporaryDirectory() as folder:
            with self.assertRaisesRegex(ResearchBridgeError, "non-transferable"):
                record_learning_points_award(folder, {**award, "transferable": True})
            with self.assertRaisesRegex(ResearchBridgeError, "idempotent"):
                record_learning_points_award(folder, {**award, "event_id": "learning-award-../../escape"})

    def test_learning_points_block_without_approval_repeats_or_all_gates(self):
        args = {"benchmark_id": "gesture", "benchmark_version": "sha256:" + "a" * 64, "capability_id": "gesture",
                "owner_approved": False, "runs": self.passing_runs()}
        with self.assertRaisesRegex(ResearchBridgeError, "approval"):
            learning_points_award(args, user_id="user-1")
        args["owner_approved"] = True
        args["runs"] = args["runs"][:2]
        with self.assertRaisesRegex(ResearchBridgeError, "repeated"):
            learning_points_award(args, user_id="user-1")
        args["runs"] = self.passing_runs()
        args["runs"][1]["hidden_holdout_passed"] = False
        with self.assertRaisesRegex(ResearchBridgeError, "gate failed"):
            learning_points_award(args, user_id="user-1")


if __name__ == "__main__":
    unittest.main()
