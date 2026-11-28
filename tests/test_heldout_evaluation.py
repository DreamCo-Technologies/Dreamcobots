import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_tool(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


evaluator = load_tool("dreamco_eval", "tools/run_heldout_evaluation.py")
validator = load_tool("dreamco_checkpoint_validator", "tools/validate_checkpoint.py")


class HeldoutEvaluationTests(unittest.TestCase):
    def setUp(self):
        self.suite = json.loads((ROOT / "evals/suites/dreamcodelab_execution_v1.json").read_text())

    def test_perfect_predictions_pass(self):
        predictions = [{"task_id": task["task_id"], "output": task["expected"]} for task in self.suite["tasks"]]
        report = evaluator.evaluate(self.suite, predictions, "test-model")
        self.assertTrue(report["passed"])
        self.assertEqual(report["accuracy"], 1.0)
        self.assertEqual(report["training_use"], "NEVER_TRAIN")
        self.assertEqual(report["split"], "public_evaluation_smoke")

    def test_missing_prediction_fails_closed(self):
        report = evaluator.evaluate(self.suite, [], "test-model")
        self.assertFalse(report["passed"])
        self.assertEqual(report["passed_tasks"], 0)

    def test_duplicate_prediction_rejected(self):
        task = self.suite["tasks"][0]
        with self.assertRaisesRegex(ValueError, "duplicate"):
            evaluator.evaluate(self.suite, [{"task_id": task["task_id"], "output": task["expected"]}] * 2, "test-model")

    def test_unknown_prediction_rejected(self):
        with self.assertRaisesRegex(ValueError, "unknown"):
            evaluator.evaluate(self.suite, [{"task_id": "UNKNOWN", "output": "x"}], "test-model")

    def test_suite_must_be_training_isolated(self):
        suite = dict(self.suite)
        suite["training_use"] = "ALLOWED"
        with self.assertRaisesRegex(ValueError, "isolated from training"):
            evaluator.evaluate(suite, [], "test-model")

    def test_checkpoint_authentication_requires_rights_eval_and_measured_parameters(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            checkpoint = root / "weights.bin"
            checkpoint.write_bytes(b"not-real-weights-test-fixture")
            evaluation = root / "evaluation.json"
            evaluation.write_text(json.dumps({
                "schema": "dreamco.heldout_evaluation_report.v1",
                "evaluator": {
                    "tool": "tools/run_heldout_evaluation.py",
                    "sha256": validator.sha256_file(ROOT / "tools/run_heldout_evaluation.py"),
                },
                "split": "private_independent_holdout",
                "training_use": "NEVER_TRAIN",
                "passed": True,
                "accuracy": 1.0,
                "required_accuracy": 0.85,
                "total_tasks": 1,
                "passed_tasks": 1,
                "suite_id": "suite",
                "suite_sha256": __import__("hashlib").sha256(b"suite").hexdigest(),
                "model_version": "dreamcodelab-candidate-001",
            }))
            config = root / "training.json"
            config.write_text(json.dumps({
                "seed": 7,
                "code_revision": "abc123",
                "base_model": "approved-base",
                "candidate_model_version": "dreamcodelab-candidate-001",
            }))
            dataset = root / "dataset.json"
            dataset.write_text(json.dumps({"training_authorized":True,"rights_review_status":"APPROVED"}))
            metrics = root / "metrics.json"
            metrics.write_text(json.dumps({"parameter_count":45_000_000,"validation_perplexity":4.2,"tokens_per_second":120,"peak_ram_mb":1024,"peak_vram_mb":0}))
            manifest = validator.build_manifest(checkpoint,evaluation,config,dataset,metrics,45_000_000,"a"*40,"test-key-1")
            self.assertEqual(manifest["status"],"VERIFIED_CHECKPOINT_EVIDENCE")
            self.assertEqual(manifest["authentication"]["algorithm"],"HMAC-SHA256")
            self.assertEqual(manifest["authentication"]["key_id"],"test-key-1")
            self.assertTrue(validator.verify_manifest_authentication(manifest,"a"*40,"test-key-1"))
            tampered = json.loads(json.dumps(manifest))
            tampered["metrics"]["tokens_per_second"] = 999
            self.assertFalse(validator.verify_manifest_authentication(tampered,"a"*40,"test-key-1"))
            self.assertFalse(validator.verify_manifest_authentication(manifest,"a"*40,"wrong-key-id"))
            dataset.write_text(json.dumps({"training_authorized":False,"rights_review_status":"PENDING"}))
            with self.assertRaisesRegex(ValueError,"dataset rights"):
                validator.build_manifest(checkpoint,evaluation,config,dataset,metrics,45_000_000,"a"*40,"test-key-1")
            dataset.write_text(json.dumps({"training_authorized":True,"rights_review_status":"APPROVED"}))
            public_report = json.loads(evaluation.read_text())
            public_report["split"] = "public_evaluation_smoke"
            evaluation.write_text(json.dumps(public_report))
            with self.assertRaisesRegex(ValueError, "private independent holdout"):
                validator.build_manifest(checkpoint,evaluation,config,dataset,metrics,45_000_000,"a"*40,"test-key-1")
            public_report["split"] = "private_independent_holdout"
            public_report["model_version"] = "different-candidate"
            evaluation.write_text(json.dumps(public_report))
            with self.assertRaisesRegex(ValueError, "model version"):
                validator.build_manifest(checkpoint,evaluation,config,dataset,metrics,45_000_000,"a"*40,"test-key-1")
            public_report["model_version"] = "dreamcodelab-candidate-001"
            public_report["evaluator"]["sha256"] = "0" * 64
            evaluation.write_text(json.dumps(public_report))
            with self.assertRaisesRegex(ValueError, "evaluator code hash"):
                validator.build_manifest(checkpoint,evaluation,config,dataset,metrics,45_000_000,"a"*40,"test-key-1")


if __name__ == "__main__":
    unittest.main()
