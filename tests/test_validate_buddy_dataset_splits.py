"""Synthetic metadata tests, not model, consent, rights, or holdout evidence."""
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from tools.validate_buddy_dataset_splits import SplitManifestError, SCHEMA, parse_manifest, read_manifest, validate


def sample():
    return {
        "schema": SCHEMA, "dataset_id": "synthetic_test_dataset_001",
        "contains_raw_examples": False, "training_authorized": False,
        "provenance_review_receipt": None, "license_review_receipt": None,
        "consent_review_receipt": None, "privacy_review_receipt": None,
        "splits": {
            "train": [{"example_id": "example_train_001", "content_sha256": "a" * 64,
                       "group_id": "group_train_001"}],
            "validation": [{"example_id": "example_valid_001", "content_sha256": "b" * 64,
                            "group_id": "group_valid_001"}],
            "holdout": [{"example_id": "example_hidden_001", "content_sha256": "c" * 64,
                         "group_id": "group_hidden_001"}],
        },
    }


class SplitTests(unittest.TestCase):
    def test_metadata_only_not_training_approval(self):
        report = validate(sample())
        self.assertEqual(report["counts"], {"train": 1, "validation": 1, "holdout": 1})
        self.assertFalse(report["training_authorized"])
        self.assertFalse(report["independent_holdout_verified"])
        self.assertEqual(len(report["missing_review_receipt_ids"]), 4)

    def test_reject_same_content_different_ids(self):
        x = sample()
        x["splits"]["holdout"][0]["content_sha256"] = "a" * 64
        with self.assertRaisesRegex(SplitManifestError, "duplicate"):
            validate(x)

    def test_reject_group_leakage_even_with_distinct_hashes(self):
        x = sample()
        x["splits"]["holdout"][0]["group_id"] = "group_train_001"
        with self.assertRaisesRegex(SplitManifestError, "group leakage"):
            validate(x)

    def test_reject_raw_examples(self):
        x = sample()
        x["splits"]["train"][0]["prompt"] = "private prompt"
        with self.assertRaisesRegex(SplitManifestError, "raw text forbidden"):
            validate(x)

    def test_reject_authorization(self):
        x = sample()
        x["training_authorized"] = True
        with self.assertRaisesRegex(SplitManifestError, "authorization prohibited"):
            validate(x)

    def test_reject_missing_holdout(self):
        x = sample()
        del x["splits"]["holdout"]
        with self.assertRaisesRegex(SplitManifestError, "exact train"):
            validate(x)

    def test_reject_duplicate_json_keys(self):
        raw = json.dumps(sample()).replace('"training_authorized": false',
                                           '"training_authorized": true, "training_authorized": false')
        with self.assertRaisesRegex(SplitManifestError, "duplicate JSON key"):
            parse_manifest(raw)

    def test_reject_nonfinite_json(self):
        raw = json.dumps(sample()).replace('"training_authorized": false',
                                           '"training_authorized": NaN')
        with self.assertRaisesRegex(SplitManifestError, "nonfinite"):
            parse_manifest(raw)

    def test_reject_pii_like_group_id(self):
        x = sample()
        x["splits"]["train"][0]["group_id"] = "person@example.com"
        with self.assertRaisesRegex(SplitManifestError, "opaque"):
            validate(x)

    def test_reject_excessively_nested_json_without_traceback(self):
        raw = "[" * 1500 + "0" + "]" * 1500
        with self.assertRaisesRegex(SplitManifestError, "excessively nested"):
            parse_manifest(raw)

    def test_reject_invalid_unicode_before_parsing(self):
        with self.assertRaisesRegex(SplitManifestError, "invalid Unicode"):
            parse_manifest("\\ud800".encode("ascii").decode("unicode_escape"))

    def test_limit_in_memory_manifest_bytes(self):
        with patch("tools.validate_buddy_dataset_splits.MAX_MANIFEST_BYTES", 100):
            with self.assertRaisesRegex(SplitManifestError, "size limit"):
                parse_manifest(json.dumps(sample()))

    def test_bounded_file_read_rejects_oversized_and_invalid_utf8(self):
        with TemporaryDirectory() as directory:
            path = Path(directory) / "metadata.json"
            path.write_bytes(b"x" * 101)
            with patch("tools.validate_buddy_dataset_splits.MAX_MANIFEST_BYTES", 100):
                with self.assertRaisesRegex(SplitManifestError, "size limit"):
                    read_manifest(path)
            path.write_bytes(b"\\xff")
            with self.assertRaisesRegex(SplitManifestError, "valid UTF-8"):
                read_manifest(path)

    def test_receipt_pointers_are_not_verification(self):
        x = sample()
        for key in ("provenance_review_receipt", "license_review_receipt",
                    "consent_review_receipt", "privacy_review_receipt"):
            x[key] = "review_pending_0001"
        report = validate(x)
        self.assertEqual(report["missing_review_receipt_ids"], [])
        self.assertFalse(report["rights_and_consent_verified"])


if __name__ == "__main__":
    unittest.main()
