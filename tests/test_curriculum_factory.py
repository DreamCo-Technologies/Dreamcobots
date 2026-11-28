"""Offline regression tests for the deterministic curriculum factory."""
import hashlib
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "stages/02_curriculum/guide_factory.py"
SPEC = importlib.util.spec_from_file_location("dreamco_guide_factory_test", MODULE_PATH)
factory = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(factory)


def policy_registry():
    return {
        "schema": "dreamco.source_license_policy.v1",
        "sources": [{
            "source_id": "youtube-platform",
            "catalog_source_ids": ["freecodecamp"],
            "domains": ["youtube.com"],
            "allowed_url_prefixes": ["https://www.youtube.com/@freecodecamp", "https://www.youtube.com/playlist?list="],
            "tier": "FACT_EXTRACTION_ONLY",
            "verified": True,
            "fact_extraction_allowed": True,
            "transcript_extraction_allowed": False,
            "commercial_training_allowed": False,
        }],
    }


def source_record():
    record = {
        "schema": "dreamco.source_catalog_record.v1",
        "source_id": "freecodecamp",
        "source_url": "https://www.youtube.com/@freecodecamp",
        "video_id": "example",
        "license_tag": "CC-BY-4.0",
        "license_record_verified": True,
        "license_evidence_url": "https://www.youtube.com/t/terms",
        "license_evidence_path": "tests/fixtures/license-evidence.txt",
        "license_evidence_sha256": hashlib.sha256((ROOT / "tests/fixtures/license-evidence.txt").read_bytes()).hexdigest(),
        "license_review_status": "approved",
        "license_reviewer_id": "owner-reviewer-1",
        "license_reviewed_at": "2026-11-27T12:00:00+00:00",
        "commercial_training_permission": False,
    }
    record["metadata_sha256"] = factory._load_catalog_sync().canonical_hash(record)
    return record


def guide():
    return {
        "guide_id": "python-basics-001",
        "title": "Reasoning about Python data structures",
        "division_id": 1,
        "learning_objectives": ["Explain when to use lists and dictionaries"],
        "lesson": "A list stores ordered values while a dictionary maps keys to values. Choose a structure by the operations your program needs.",
        "practice_lab": "Build a small inventory using a list of dictionaries and test lookup, insertion, and update operations.",
        "assessment": "Given three inventory operations, select a suitable structure and explain the time and clarity tradeoffs.",
        "safety_notes": ["Use synthetic data and never place credentials in the exercise."],
        "owner_review_status": "draft",
    }


class CurriculumFactoryTests(unittest.TestCase):
    def test_eightgram_gate_passes_independent_draft_and_marks_review_required(self):
        refs = ["This unrelated reference explains a different concept with separate wording and examples for learners."]
        result = factory.build_guide(
            source_record=source_record(), policy_registry=policy_registry(),
            authored_content=guide(), similarity_references=refs,
        )
        self.assertEqual(result["release_status"], "draft_review_required")
        self.assertTrue(result["quality_report"]["originality_passed"])
        self.assertFalse(result["quality_report"]["commercial_release_authorized"])
        self.assertTrue(result["quality_report"]["human_rights_review_required"])
        self.assertEqual(result["provenance"]["source_use"], "fact_extraction_only")
        self.assertFalse(result["provenance"]["transcript_downloaded"])

    def test_exact_reuse_is_quarantined(self):
        draft = guide()
        candidate = " ".join([draft["title"], *draft["learning_objectives"], draft["lesson"],
                              draft["practice_lab"], draft["assessment"], *draft["safety_notes"]])
        result = factory.build_guide(
            source_record=source_record(), policy_registry=policy_registry(),
            authored_content=draft, similarity_references=[candidate],
        )
        self.assertEqual(result["release_status"], "quarantined_similarity_review")
        self.assertFalse(result["quality_report"]["originality_passed"])

    def test_missing_item_license_evidence_fails_closed(self):
        record = source_record()
        record["license_record_verified"] = False
        with self.assertRaises(PermissionError):
            factory.build_guide(source_record=record, policy_registry=policy_registry(),
                                authored_content=guide(), similarity_references=["A sufficiently long unrelated reference."])

    def test_tampered_catalog_metadata_fingerprint_fails_closed(self):
        record = source_record()
        record["duration"] = 99
        with self.assertRaises(ValueError):
            factory.build_guide(source_record=record, policy_registry=policy_registry(),
                                authored_content=guide(), similarity_references=["An unrelated reference with enough words for comparison."])

    def test_tampered_license_snapshot_fails_closed(self):
        record = source_record()
        record["license_evidence_sha256"] = "0" * 64
        with self.assertRaises(PermissionError):
            factory.build_guide(source_record=record, policy_registry=policy_registry(),
                                authored_content=guide(), similarity_references=["An unrelated reference with enough words for comparison."])

    def test_missing_license_snapshot_evidence_fails_closed(self):
        record = source_record()
        record.pop("license_evidence_sha256")
        with self.assertRaises(PermissionError):
            factory.build_guide(source_record=record, policy_registry=policy_registry(),
                                authored_content=guide(), similarity_references=["An unrelated reference with enough words for comparison."])

    def test_fcc_fact_extraction_only_does_not_authorize_transcripts_or_commercial_training(self):
        record = source_record()
        decision = factory._load_policy_gate().evaluate_source(record, policy_registry(), "fact_extraction")
        self.assertTrue(decision["allowed"])
        transcript = factory._load_policy_gate().evaluate_source(record, policy_registry(), "transcript_extraction")
        commercial = factory._load_policy_gate().evaluate_source(record, policy_registry(), "commercial_training")
        self.assertFalse(transcript["allowed"])
        self.assertFalse(commercial["allowed"])

    def test_short_originality_reference_fails_closed(self):
        with self.assertRaises(ValueError):
            factory.build_guide(source_record=source_record(), policy_registry=policy_registry(),
                                authored_content=guide(), similarity_references=["too few tokens here"])

    def test_unregistered_source_id_on_allowed_domain_is_blocked(self):
        record = source_record()
        record["source_id"] = "unregistered-channel"
        with self.assertRaises(PermissionError):
            factory.build_guide(source_record=record, policy_registry=policy_registry(),
                                authored_content=guide(), similarity_references=["An unrelated reference with enough words for comparison."])

    def test_short_candidate_guide_fails_closed(self):
        short = {"guide_id": "short", "title": "One", "learning_objectives": ["Two"],
                 "lesson": "Three", "practice_lab": "Four", "assessment": "Five",
                 "safety_notes": ["Six"]}
        with self.assertRaises(ValueError):
            factory.build_guide(source_record=source_record(), policy_registry=policy_registry(),
                                authored_content=short, similarity_references=["An unrelated reference with enough words for comparison."])

    def test_missing_originality_references_fails_closed(self):
        with self.assertRaises(PermissionError):
            factory.build_guide(source_record=source_record(), policy_registry=policy_registry(),
                                authored_content=guide(), similarity_references=[])

    def test_invalid_division_and_unverified_onet_values_are_not_silently_accepted(self):
        draft = guide()
        draft["division_id"] = 66
        with self.assertRaises(ValueError):
            factory.build_guide(source_record=source_record(), policy_registry=policy_registry(),
                                authored_content=draft, similarity_references=["An unrelated reference with enough words for comparison."])

    def test_bundle_writes_separate_non_overwriting_artifacts(self):
        result = factory.build_guide(
            source_record=source_record(), policy_registry=policy_registry(),
            authored_content=guide(),
            similarity_references=["A separate source note with entirely different vocabulary for comparison."],
        )
        with tempfile.TemporaryDirectory() as tmp:
            paths = factory.write_guide_bundle(result, Path(tmp))
            self.assertEqual(len(paths), 3)
            self.assertTrue(all(path.exists() for path in paths))
            with self.assertRaises(FileExistsError):
                factory.write_guide_bundle(result, Path(tmp))
            self.assertEqual(json.loads(paths[0].read_text())["owner_review_status"], "draft")


if __name__ == "__main__":
    unittest.main()
