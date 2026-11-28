"""Offline tests for signed-data guardrails and train/validation/holdout isolation."""
import importlib.util
import importlib
import hashlib
import json
import tempfile
import unittest
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "stages" / "05_model_foundry" / "guardrails.py"
SPEC = importlib.util.spec_from_file_location("dreamco_foundry_guardrails", MODULE_PATH)
GUARDRAILS = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(GUARDRAILS)
sys.path.insert(0, str(MODULE_PATH.parent))
TRAIN_WEIGHTS_SPEC = importlib.util.spec_from_file_location(
    "dreamco_foundry_train_weights", MODULE_PATH.parent / "train_weights.py"
)
TRAIN_WEIGHTS = importlib.util.module_from_spec(TRAIN_WEIGHTS_SPEC)
assert TRAIN_WEIGHTS_SPEC and TRAIN_WEIGHTS_SPEC.loader
TRAIN_WEIGHTS_SPEC.loader.exec_module(TRAIN_WEIGHTS)
HOLDOUT_HELPERS = importlib.import_module("stages.05_model_foundry.holdout")
HOLDOUT_RUNNER = importlib.import_module("stages.05_model_foundry.run_holdout_eval")
HOLDOUT_GATE = importlib.import_module("stages.05_model_foundry.eval_holdout")


class FoundryGuardrailTests(unittest.TestCase):
    def test_split_is_deterministic_and_disjoint(self):
        ids = [f"task-{i}" for i in range(10000)]
        buckets = [GUARDRAILS.split_bucket(value) for value in ids]
        self.assertEqual(buckets, [GUARDRAILS.split_bucket(value) for value in ids])
        self.assertTrue(all(GUARDRAILS.split_name(value) == "train" for value in ids if GUARDRAILS.split_bucket(value) < 90))
        self.assertTrue(all(GUARDRAILS.split_name(value) == "validation" for value in ids if 90 <= GUARDRAILS.split_bucket(value) < 95))
        self.assertTrue(all(GUARDRAILS.split_name(value) == "holdout" for value in ids if GUARDRAILS.split_bucket(value) >= 95))

    def test_unsigned_or_tampered_manifest_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            data = root / "records.jsonl"
            data.write_text('{"task_id":"t1","content":"safe"}\n', encoding="utf-8")
            manifest = {
                "schema": "dreamco.foundry.authorization.v1",
                "datasets": [{
                    "dataset_id": "d1",
                    "path": "records.jsonl",
                    "sha256": hashlib.sha256(data.read_bytes()).hexdigest(),
                    "license_tier": "DREAMCO_ORIGINAL",
                    "commercial_use": True,
                    "policy_decision_id": "PD-1",
                    "category": "study_guides",
                }],
            }
            manifest_path = root / "manifest.json"
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
            signature_path = root / "manifest.sig"
            signature_path.write_text("", encoding="ascii")
            public_key_path = root / "pub.pem"
            public_key_path.write_text("not-a-key", encoding="ascii")
            with self.assertRaises(Exception):
                GUARDRAILS.verify_signed_manifest(manifest_path, signature_path, public_key_path)

    def test_holdout_cannot_be_requested_with_training_splits(self):
        with self.assertRaises(PermissionError):
            list(GUARDRAILS.iter_authorized_records(
                {"datasets": []}, splits={"train", "holdout"}
            ))

    def test_dpo_accepts_only_lab_pass_teachback_against_lab_failure(self):
        rows = [
            {"prompt": "p", "chosen": "good", "rejected": "bad",
             "chosen_status": "LAB_PASSED", "teach_back_verified": True,
             "rejected_status": "LAB_FAILED"},
            {"prompt": "p", "chosen": "unverified", "rejected": "bad",
             "chosen_status": "LAB_PASSED", "teach_back_verified": False,
             "rejected_status": "LAB_FAILED"},
        ]
        pairs = TRAIN_WEIGHTS.validated_preferences(rows)
        self.assertEqual(len(pairs), 1)
        self.assertEqual(pairs[0]["chosen"], "good")

    def test_open_weight_requires_exact_signed_license_evidence(self):
        approved = {
            "models": [{
                "model_id": "example/model",
                "revision": "a" * 40,
                "license_tier": "PERMISSIVE_COMMERCIAL",
                "commercial_use": True,
                "policy_decision_id": "POLICY-1",
                "license_evidence_id": "LICENSE-1",
                "approved_by": "Policy Owner",
            }]
        }
        result = GUARDRAILS.require_model_authorization(approved, "example/model", "a" * 40)
        self.assertEqual(result["license_evidence_id"], "LICENSE-1")
        with self.assertRaises(PermissionError):
            GUARDRAILS.require_model_authorization(approved, "example/model", "b" * 40)

    def test_holdout_helpers_use_same_fixed_split_as_guardrails(self):
        ids = [f"task-{i}" for i in range(1000)]
        self.assertEqual(
            [HOLDOUT_HELPERS.bucket(value) for value in ids],
            [GUARDRAILS.split_bucket(value) for value in ids],
        )
        with self.assertRaises(ValueError):
            HOLDOUT_HELPERS.split_tasks([{"task_id": "x"}], holdout_percent=20)

    def test_holdout_runner_uses_deterministic_text_normalization(self):
        self.assertEqual(HOLDOUT_RUNNER.normalized("Hello, WORLD!"), "hello world")
        self.assertEqual(HOLDOUT_RUNNER.normalized("  A   B  "), "a b")

    def test_holdout_gate_requires_exact_suite_and_config_evidence(self):
        report = {
            "evaluation_split": "holdout",
            "source_manifest_sha256": "a" * 64,
            "benchmark_suite_sha256": "b" * 64,
            "evaluation_config_sha256": "c" * 64,
            "checkpoint_sha256": "d" * 64,
            "evaluated_task_ids": ["task-1"],
            "pass_rate": 0.95,
            "safety_gate_pass_rate": 1.0,
        }
        HOLDOUT_GATE.validate_report(report, ["task-1"], "a" * 64, "b" * 64, "candidate")
        with self.assertRaises(ValueError):
            HOLDOUT_GATE.validate_report(report, ["task-2"], "a" * 64, "b" * 64, "candidate")

    def test_sft_rows_require_assistant_or_tool_targets(self):
        rows = [
            {"messages": [{"role": "user", "content": "question"}]},
            {"messages": [{"role": "assistant", "content": "verified answer"}]},
            {"messages": [{"role": "tool", "content": "tool result"}]},
        ]
        selected = TRAIN_WEIGHTS.sft_rows(rows)
        self.assertEqual(len(selected), 2)

    def test_self_play_pairs_only_use_verified_lab_and_teachback_preferences(self):
        path = ROOT / "stages" / "05_model_foundry" / "generate_self_play_pairs.py"
        spec = importlib.util.spec_from_file_location("dreamco_self_play_pairs", path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        common = {
            "task_id": "task-1", "prompt": "Solve this",
            "test_suite_sha256": "a" * 64, "rubric_sha256": "b" * 64,
            "grader_attestation_sha256": "c" * 64, "grader_version": "grader-v1",
        }
        rows = [
            {**common, "candidate_id": "good", "response": "correct",
             "sandbox_status": "LAB_PASSED", "teach_back_status": "TEACH_BACK_VERIFIED",
             "sandbox_run_id": "run-good"},
            {**common, "candidate_id": "bad", "response": "incorrect",
             "sandbox_status": "LAB_FAILED", "teach_back_status": "NOT_VERIFIED",
             "sandbox_run_id": "run-bad"},
            {**common, "candidate_id": "weak", "response": "unverified",
             "sandbox_status": "LAB_PASSED", "teach_back_status": "NOT_VERIFIED",
             "sandbox_run_id": "run-weak"},
        ]
        pairs, report = module.build_pairs(rows)
        self.assertEqual(len(pairs), 1)
        self.assertEqual(pairs[0]["chosen"], "correct")
        self.assertEqual(pairs[0]["rejected"], "incorrect")
        self.assertFalse(report["training_started"])

    def test_self_play_pairs_reject_mismatched_test_suite_revisions(self):
        path = ROOT / "stages" / "05_model_foundry" / "generate_self_play_pairs.py"
        spec = importlib.util.spec_from_file_location("dreamco_self_play_pairs_mismatch", path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        common = {"task_id":"t","grader_version":"v1","rubric_sha256":"b"*64,
                  "grader_attestation_sha256":"c"*64}
        rows = [
            {**common,"candidate_id":"a","response":"good","sandbox_status":"LAB_PASSED",
             "teach_back_status":"TEACH_BACK_VERIFIED","sandbox_run_id":"1","test_suite_sha256":"a"*64},
            {**common,"candidate_id":"b","response":"bad","sandbox_status":"LAB_FAILED",
             "teach_back_status":"NOT_VERIFIED","sandbox_run_id":"2","test_suite_sha256":"d"*64},
        ]
        pairs, _ = module.build_pairs(rows)
        self.assertEqual(pairs, [])

    def test_shared_cache_requires_explicit_public_redistribution(self):
        path = ROOT / "stages" / "05_model_foundry" / "cache_policy.py"
        module = importlib.import_module("stages.05_model_foundry.cache_policy")
        self.assertTrue(module.public_cache_allowed({"datasets":[
            {"cache_visibility":"public","redistribution_allowed":True}
        ]}))
        self.assertFalse(module.public_cache_allowed({"datasets":[
            {"cache_visibility":"private","redistribution_allowed":False}
        ]}))
        self.assertFalse(module.public_cache_allowed({"datasets":[]}))

    def test_self_play_pairs_require_same_prompt_for_all_candidates(self):
        path = ROOT / "stages" / "05_model_foundry" / "generate_self_play_pairs.py"
        spec = importlib.util.spec_from_file_location("dreamco_self_play_prompt_check", path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        common = {"task_id":"t","grader_version":"v1","test_suite_sha256":"a"*64,
                  "rubric_sha256":"b"*64,"grader_attestation_sha256":"c"*64}
        rows = [
            {**common,"candidate_id":"a","prompt":"prompt one","response":"good",
             "sandbox_status":"LAB_PASSED","teach_back_status":"TEACH_BACK_VERIFIED","sandbox_run_id":"1"},
            {**common,"candidate_id":"b","prompt":"prompt two","response":"bad",
             "sandbox_status":"LAB_FAILED","teach_back_status":"NOT_VERIFIED","sandbox_run_id":"2"},
        ]
        pairs, _ = module.build_pairs(rows)
        self.assertEqual(pairs, [])

    def test_holdout_promotion_validator_requires_exact_signed_task_coverage(self):
        evaluator = importlib.import_module("stages.05_model_foundry.eval_holdout")
        report = {
            "schema": "dreamco.foundry.model_holdout_report.v1",
            "holdout_access": "evaluation_only",
            "training_access": False,
            "evaluation_split": "holdout",
            "source_manifest_sha256": "a" * 64,
            "benchmark_suite_sha256": "b" * 64,
            "evaluation_config_sha256": "c" * 64,
            "checkpoint_sha256": "d" * 64,
            "evaluated_task_ids": ["task-a", "task-b"],
            "pass_rate": 0.95,
            "safety_gate_pass_rate": 1.0,
        }
        evaluator.validate_report(report, ["task-a", "task-b"], "a" * 64, "b" * 64, "candidate")
        with self.assertRaises(ValueError):
            evaluator.validate_report(report, ["task-a", "task-b", "task-c"], "a" * 64, "b" * 64, "candidate")


if __name__ == "__main__":
    unittest.main()
