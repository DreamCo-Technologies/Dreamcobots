"""Tests for the fail-closed commercial model license gate."""
from __future__ import annotations
import hashlib, tempfile, unittest
from pathlib import Path
from buddy.media.model_license_gate import verify_model_record

class ModelLicenseGateTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        evidence = self.root / "licenses" / "model.txt"
        evidence.parent.mkdir()
        evidence.write_text("SPDX-License-Identifier: MIT\n", encoding="utf-8")
        self.record = {
            "model_id": "example/model",
            "checkpoint_sha256": "a" * 64,
            "license_id": "MIT",
            "license_evidence_path": "licenses/model.txt",
            "license_evidence_sha256": hashlib.sha256(evidence.read_bytes()).hexdigest(),
            "model_card_url": "https://example.invalid/model-card",
            "commercial_use_allowed": True,
            "redistribution_allowed": True,
            "dependencies": [{"name": "runtime-lib", "license_id": "Apache-2.0", "reviewed": True}],
        }

    def tearDown(self):
        self.temp.cleanup()

    def test_complete_permissive_record_is_approved(self):
        result = verify_model_record(self.record, self.root)
        self.assertEqual(result["decision"], "approved")
        self.assertEqual(result["reasons"], [])

    def test_unknown_or_noncommercial_license_is_blocked(self):
        self.record["license_id"] = "CC-BY-NC-4.0"
        self.assertEqual(verify_model_record(self.record, self.root)["decision"], "blocked")

    def test_missing_commercial_permission_is_blocked(self):
        self.record["commercial_use_allowed"] = False
        self.assertIn("commercial_use_not_explicitly_allowed",
                      verify_model_record(self.record, self.root)["reasons"])

    def test_evidence_hash_mismatch_is_blocked(self):
        self.record["license_evidence_sha256"] = "0" * 64
        self.assertIn("license_evidence_hash_mismatch",
                      verify_model_record(self.record, self.root)["reasons"])

    def test_unreviewed_dependency_is_blocked(self):
        self.record["dependencies"][0]["reviewed"] = False
        self.assertIn("dependency_0_not_reviewed",
                      verify_model_record(self.record, self.root)["reasons"])

    def test_path_traversal_is_blocked(self):
        self.record["license_evidence_path"] = "../outside.txt"
        self.assertIn("license_evidence_path_escapes_evidence_root",
                      verify_model_record(self.record, self.root)["reasons"])

if __name__ == "__main__":
    unittest.main()
