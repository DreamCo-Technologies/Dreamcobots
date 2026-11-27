"""Tests for rights-aware Institute resource intake."""
import json
import tempfile
import unittest
from pathlib import Path

from scripts import buddy_resource_harvester as harvester


class BuddyResourceHarvesterTests(unittest.TestCase):
    def test_discovers_exactly_55_academic_divisions(self):
        divisions = harvester.load_divisions()
        self.assertEqual(len(divisions), 55)
        self.assertIn("dreamcyber", divisions)

    def test_empty_manifest_is_safe_and_never_creates_training_or_holdouts(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            manifest = root / "sources.json"
            output = root / "staging"
            manifest.write_text(json.dumps({
                "schema": "dreamco.buddy_resource_sources.v1",
                "sources": []
            }), encoding="utf-8")
            report = harvester.run(manifest, output)
            self.assertEqual(report["canonical_divisions"], 55)
            self.assertEqual(report["records_staged"], 0)
            self.assertFalse(report["training_corpora_written"])
            self.assertFalse(report["development_suites_written"])
            self.assertFalse(report["private_holdouts_written"])
            self.assertFalse(report["holdout_seals_modified"])
            self.assertTrue((output / "resource_intake_report.json").is_file())

    def test_unapproved_source_is_rejected_before_ingestion(self):
        divisions = harvester.load_divisions()
        with tempfile.TemporaryDirectory() as temp:
            manifest = Path(temp) / "sources.json"
            manifest.write_text(json.dumps({
                "schema": "dreamco.buddy_resource_sources.v1",
                "sources": [{
                    "division_id": next(iter(divisions)),
                    "source_type": "local_markdown",
                    "path": "README.md",
                    "expected_sha256": "0000000000000000000000000000000000000000000000000000000000000000",
                    "rights_status": "UNVERIFIED",
                    "approved_for_training": False,
                    "evidence_reference": ""
                }]
            }), encoding="utf-8")
            with self.assertRaises(PermissionError):
                harvester.load_sources(manifest, divisions)

    def test_source_requires_pinned_sha256_and_evidence(self):
        divisions = harvester.load_divisions()
        with tempfile.TemporaryDirectory() as temp:
            manifest = Path(temp) / "sources.json"
            manifest.write_text(json.dumps({
                "schema": "dreamco.buddy_resource_sources.v1",
                "sources": [{
                    "division_id": next(iter(divisions)),
                    "source_type": "local_markdown",
                    "path": "README.md",
                    "rights_status": "DREAMCO_ORIGINAL",
                    "approved_for_training": True,
                    "evidence_reference": "review-record"
                }]
            }), encoding="utf-8")
            with self.assertRaises(ValueError):
                harvester.load_sources(manifest, divisions)


if __name__ == "__main__":
    unittest.main()
