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
        holdout_spec = importlib.util.spec_from_file_location(
            "dreamco_foundry_holdout", MODULE_PATH.parent / "holdout.py"
        )
        holdout_module = importlib.util.module_from_spec(holdout_spec)
        assert holdout_spec and holdout_spec.loader
        holdout_spec.loader.exec_module(holdout_module)
        ids = [f"task-{i}" for i in range(1000)]
        self.assertEqual(
            [holdout_module.bucket(value) for value in ids],
            [GUARDRAILS.split_bucket(value) for value in ids],
        )
        with self.assertRaises(ValueError):
            holdout_module.split_tasks([{"task_id": "x"}], holdout_percent=20)

    def test_sft_rows_require_assistant_or_tool_targets(self):
        rows = [
            {"messages": [{"role": "user", "content": "question"}]},
            {"messages": [{"role": "assistant", "content": "verified answer"}]},
            {"messages": [{"role": "tool", "content": "tool result"}]},
        ]
        selected = TRAIN_WEIGHTS.sft_rows(rows)
        self.assertEqual(len(selected), 2)


if __name__ == "__main__":
    unittest.main()
