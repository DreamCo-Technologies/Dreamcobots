"""Offline tests for signed-data guardrails and train/validation/holdout isolation."""
import importlib.util
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "stages" / "05_model_foundry" / "guardrails.py"
SPEC = importlib.util.spec_from_file_location("dreamco_foundry_guardrails", MODULE_PATH)
GUARDRAILS = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(GUARDRAILS)


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


if __name__ == "__main__":
    unittest.main()
