import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from scripts.benchmark_vs_baselines import (
    evaluate_model,
    percentile,
    validate_candidate,
    validate_fixtures,
    validate_schema,
)


class CompetitiveBenchmarkTests(unittest.TestCase):
    def test_percentile_interpolates(self):
        self.assertEqual(percentile([1.0, 2.0, 3.0, 4.0], 0.5), 2.5)
        self.assertEqual(percentile([], 0.95), None)

    def test_schema_validator_rejects_missing_and_extra_fields(self):
        schema = {"type": "object", "required": ["ok"], "properties": {"ok": {"type": "boolean"}}, "additionalProperties": False}
        self.assertTrue(validate_schema({"ok": True}, schema))
        self.assertFalse(validate_schema({"ok": "yes"}, schema))
        self.assertFalse(validate_schema({"ok": True, "extra": 1}, schema))

    def test_fixture_validation_requires_both_splits_and_rights(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "fixtures.json"
            case = {
                "case_id": "case-1", "division_id": "dreamcyber", "task_id": "triage",
                "split": "development", "input": {"event": "x"},
                "expected_result": {"priority": "high"}, "expected_route": "human_ai",
                "output_schema": {"type": "object", "required": ["priority"], "properties": {"priority": {"type": "string"}}}
            }
            path.write_text(json.dumps({
                "schema": "dreamco.competitive_benchmark_fixtures.v1",
                "provenance": {"rights_status": "DREAMCO_ORIGINAL", "evidence_reference": "authoring-record-1"},
                "cases": [case, {**case, "case_id": "case-2", "split": "private_holdout"}]
            }), encoding="utf-8")
            self.assertEqual(len(validate_fixtures(path, "dreamcyber")), 2)
            payload = json.loads(path.read_text())
            payload["provenance"]["rights_status"] = "UNKNOWN"
            path.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaises(PermissionError):
                validate_fixtures(path, "dreamcyber")

    def test_candidate_must_have_canonical_parameter_count_and_hashed_checkpoint(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            checkpoint = root / "weights.bin"
            checkpoint.write_bytes(b"model-weights")
            digest = hashlib.sha256(checkpoint.read_bytes()).hexdigest()
            manifest = {
                "schema": "dreamco.model_candidate_manifest.v1",
                "model_id": "dreamcyber-45m", "model_version": "0.1.0", "division_id": "dreamcyber",
                "training_run_id": "run-1", "training_authorization_reference": "approval-123",
                "evaluation_authorized": True,
                "architecture": {"parameter_count": 45038208, "config_sha256": "a" * 64},
                "tokenizer": {"revision": "tokenizer-v1", "sha256": "b" * 64},
                "checkpoint": {"path": "weights.bin", "sha256": digest},
                "adapter": {"command": ["python", "-c", "print('{}')"]}
            }
            path = root / "candidate.json"
            path.write_text(json.dumps(manifest), encoding="utf-8")
            self.assertEqual(validate_candidate(path, "dreamcyber")["model_id"], "dreamcyber-45m")
            manifest["architecture"]["parameter_count"] = 45000000
            path.write_text(json.dumps(manifest), encoding="utf-8")
            with self.assertRaises(ValueError):
                validate_candidate(path, "dreamcyber")

    def test_runner_does_not_send_expected_answer_and_measures_contracts(self):
        case = {
            "case_id": "case-1", "division_id": "dreamcyber", "task_id": "triage",
            "split": "development", "input": {"event": "x"},
            "expected_result": {"priority": "high"}, "expected_route": "human_ai",
            "output_schema": {"type": "object", "required": ["priority"], "properties": {"priority": {"type": "string"}}}
        }
        command = ["python", "-c", "import json,sys; x=json.load(sys.stdin); assert 'expected_result' not in x; print(json.dumps({'result':{'priority':'high'},'route':'human_ai'}))"]
        result = evaluate_model({"model_id": "test", "division_id": "dreamcyber", "_command": command}, [case], 2, 3)
        self.assertEqual(result["contract_pass_rate"], 1.0)
        self.assertEqual(result["task_exact_match_rate"], 1.0)
        self.assertEqual(result["routing_accuracy"], 1.0)
        self.assertEqual(result["deterministic_repeat_rate"], 1.0)
        self.assertIsNone(result["cost_per_million_tokens_usd"])


if __name__ == "__main__":
    unittest.main()
