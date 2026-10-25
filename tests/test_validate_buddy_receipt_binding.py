"""Fictional metadata linkage tests; no actual model, dataset or holdout run."""
from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from tools.validate_buddy_receipt_binding import (
    BindingError, file_sha256, holdout_metadata_digest, validate_binding,
)
from tests.test_validate_buddy_dataset_splits import sample
from tests.test_validate_buddy_evaluation_receipt import example


class ReceiptBindingTests(unittest.TestCase):
    def linked(self):
        manifest = sample()
        receipt = example()
        receipt["dataset_manifest_sha256"] = "e" * 64
        receipt["holdout_set_sha256"] = holdout_metadata_digest(manifest)
        return receipt, manifest

    def test_metadata_binding_is_not_holdout_or_training_evidence(self):
        receipt, manifest = self.linked()
        report = validate_binding(receipt, manifest, "e" * 64)
        self.assertTrue(report["manifest_bytes_sha256_match"])
        self.assertTrue(report["holdout_metadata_sha256_match"])
        self.assertFalse(report["holdout_content_integrity_verified"])
        self.assertFalse(report["independent_evaluator_verified"])
        self.assertFalse(report["model_quality_verified"])
        self.assertFalse(report["eligible_for_model_promotion"])

    def test_reject_manifest_byte_digest_mismatch(self):
        receipt, manifest = self.linked()
        with self.assertRaisesRegex(BindingError, "dataset digest"):
            validate_binding(receipt, manifest, "f" * 64)

    def test_reject_holdout_metadata_change_even_with_same_manifest_hash(self):
        receipt, manifest = self.linked()
        manifest["splits"]["holdout"][0]["content_sha256"] = "f" * 64
        with self.assertRaisesRegex(BindingError, "holdout digest"):
            validate_binding(receipt, manifest, "e" * 64)

    def test_reject_sample_count_exceeding_holdout(self):
        receipt, manifest = self.linked()
        receipt["samples_evaluated"] = 2
        receipt["samples_correct"] = 1
        with self.assertRaisesRegex(BindingError, "sample count"):
            validate_binding(receipt, manifest, "e" * 64)

    def test_existing_split_isolation_rules_remain_mandatory(self):
        receipt, manifest = self.linked()
        manifest["splits"]["holdout"][0]["group_id"] = "group_train_001"
        with self.assertRaisesRegex(ValueError, "group leakage"):
            validate_binding(receipt, manifest, "e" * 64)

    def test_actual_manifest_bytes_digest(self):
        receipt, manifest = self.linked()
        with TemporaryDirectory() as directory:
            path = Path(directory) / "split-manifest.json"
            payload = json.dumps(manifest, sort_keys=True).encode("utf-8")
            path.write_bytes(payload)
            digest = file_sha256(path)
            self.assertEqual(digest, sha256(payload).hexdigest())
            receipt["dataset_manifest_sha256"] = digest
            self.assertTrue(validate_binding(receipt, manifest, digest)["manifest_bytes_sha256_match"])

    def test_workflow_watches_and_runs_binding_tests(self):
        workflow = (Path(__file__).resolve().parents[1] /
                    ".github/workflows/buddy-teacher-coverage-audit.yml").read_text()
        self.assertIn('"tools/validate_buddy_receipt_binding.py"', workflow)
        self.assertIn('"tests/test_validate_buddy_receipt_binding.py"', workflow)
        self.assertIn("tests.test_validate_buddy_receipt_binding", workflow)


if __name__ == "__main__":
    unittest.main()
