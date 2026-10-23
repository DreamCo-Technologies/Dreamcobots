"""Fail-closed reviewer provenance for hash-bound benchmark gap receipts.

Synthetic fixtures test validator behavior only; they do not certify mastery.
"""
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from tools.benchmark_gap_closure import plan


class BenchmarkGapReviewerIntegrityTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        source = self.root / "suite.json"
        source.write_text('{"fixture":true}\n', encoding="utf-8")
        receipt = {
            "division_id": "fixture-division",
            "benchmark_id": "fixture-suite",
            "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
            "status": "passed",
            "regression_status": "passed",
            "tests_run": 3,
            "tests_failed": 0,
            "score": 70,
            "target": 60,
            "baseline": 40,
        }
        artifact = self.root / "receipt.json"
        artifact.write_text(json.dumps(receipt), encoding="utf-8")
        self.record = {
            "division_id": "fixture-division",
            "benchmark_id": "fixture-suite",
            "baseline": 40,
            "target": 60,
            "evidence": {
                "review_status": "reviewed",
                "reviewer": "fixture-reviewer",
                "source": source.name,
                "artifact": artifact.name,
                "artifact_sha256": hashlib.sha256(artifact.read_bytes()).hexdigest(),
            },
        }

    def test_valid_synthetic_reviewed_receipt_remains_supported(self):
        decision = plan(self.record, self.root)
        self.assertEqual(decision["status"], "closed")
        self.assertTrue(decision["evidence_verified"])

    def test_malformed_or_blank_reviewer_never_closes_gap(self):
        for reviewer in (True, 42, {"name": "fixture"}, ["fixture"], "", " \t "):
            with self.subTest(reviewer=reviewer):
                self.record["evidence"]["reviewer"] = reviewer
                decision = plan(self.record, self.root)
                self.assertEqual(decision["status"], "open")
                self.assertFalse(decision["evidence_verified"])

    def test_missing_review_remains_unverified(self):
        self.record["evidence"]["review_status"] = "requires_suite_specific_review"
        self.assertFalse(plan(self.record, self.root)["evidence_verified"])

    def test_hash_tampering_remains_unverified(self):
        (self.root / "receipt.json").write_text("{}", encoding="utf-8")
        self.assertFalse(plan(self.record, self.root)["evidence_verified"])

    def test_registry_template_never_certifies_even_with_fixture_receipt(self):
        self.record["suite_id"] = "fixture-suite"
        decision = plan(self.record, self.root, registry_only=True)
        self.assertEqual(decision["status"], "blocked")
        self.assertFalse(decision["evidence_verified"])


if __name__ == "__main__":
    unittest.main()
