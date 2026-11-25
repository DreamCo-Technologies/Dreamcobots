import hashlib
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from tools.build_freecodecamp_transcript_intake import build_intake, audit_weekly_tests


def catalog(status="partial"):
    return {
        "schema": "dreamco.freecodecamp_catalog.v1",
        "source": {"channel_id": "UC8butISFwT-Wl7EV0hUK0BQ"},
        "inventory_status": status,
        "videos": [
            {"video_id": "video-1", "title": "Course one", "url": "https://www.youtube.com/watch?v=video-1"},
            {"video_id": "video-2", "title": "Course two", "url": "https://www.youtube.com/watch?v=video-2"},
        ],
    }


def manifest(records=None):
    return {
        "schema": "dreamco.authorized_transcript_manifest.v1",
        "transcripts": records or [],
        "rights_policy": {
            "automatic_caption_scraping": False,
            "automatic_transcript_download": False,
            "automatic_model_training": False,
        },
    }


def weekly_evidence(records=None):
    return {
        "schema": "dreamco.freecodecamp_weekly_buddy_test_evidence.v1",
        "records": records or [],
    }


class FreeCodeCampTranscriptIntakeTests(unittest.TestCase):
    def test_partial_catalog_creates_permission_queue_and_blocks_weekly_coverage(self):
        intake = build_intake(catalog("partial"), manifest())
        self.assertEqual(intake["catalog_video_count"], 2)
        self.assertEqual(intake["permission_request_count"], 2)
        self.assertEqual(intake["authorized_transcript_count"], 0)
        self.assertFalse(intake["content_downloaded"])
        self.assertFalse(intake["model_training_started"])
        audit = audit_weekly_tests(intake, weekly_evidence(), now=datetime(2026, 11, 25, tzinfo=timezone.utc))
        self.assertEqual(audit["status"], "BLOCKED_PARTIAL_SOURCE_CATALOG")
        self.assertEqual(audit["tested_transcript_count"], 0)
        self.assertFalse(audit["buddy_test_execution_performed_by_audit"])

    def test_complete_catalog_with_no_authorized_transcripts_is_not_claimed_as_tested(self):
        intake = build_intake(catalog("complete"), manifest())
        audit = audit_weekly_tests(intake, weekly_evidence(), now=datetime(2026, 11, 25, tzinfo=timezone.utc))
        self.assertEqual(audit["status"], "BLOCKED_NO_AUTHORIZED_TRANSCRIPTS")

    def test_authorized_transcript_and_recent_buddy_test_evidence_pass(self):
        now = datetime(2026, 11, 25, 12, 0, tzinfo=timezone.utc)
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            relative = "data/freecodecamp/authorized-transcripts/video-1.txt"
            transcript = root / relative
            transcript.parent.mkdir(parents=True)
            content = b"Creator-authorized transcript fixture."
            transcript.write_bytes(content)
            digest = hashlib.sha256(content).hexdigest()
            record = {
                "video_id": "video-1",
                "source_url": "https://www.youtube.com/watch?v=video-1",
                "transcript_path": relative,
                "transcript_sha256": digest,
                "rights_status": "VERIFIED",
                "rights_evidence_ref": "creator-permission-fixture-001",
                "study_permission": True,
                "evaluation_permission": True,
                "training_permission": False,
            }
            intake = build_intake(catalog("complete"), manifest([record]), root=root)
            self.assertEqual(intake["authorized_transcript_count"], 1)
            self.assertFalse(intake["queue"][0]["model_training_authorized"])
            evidence = weekly_evidence([{
                "video_id": "video-1",
                "tested_at": now.isoformat(),
                "status": "PASS",
                "buddy_model_id": "buddy-local",
                "buddy_model_version": "0.1.0",
                "run_id": "run-001",
                "suite_id": "freecodecamp-transcript-weekly-v1",
                "evaluation_permission_ref": "creator-permission-fixture-001",
                "result_sha256": "d" * 64,
            }])
            audit = audit_weekly_tests(intake, evidence, now=now)
            self.assertEqual(audit["status"], "COMPLETE")
            self.assertEqual(audit["tested_transcript_count"], 1)
            self.assertFalse(audit["model_training_authorized"])

    def test_missing_stale_or_failed_weekly_evidence_does_not_pass(self):
        now = datetime(2026, 11, 25, 12, 0, tzinfo=timezone.utc)
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            relative = "data/freecodecamp/authorized-transcripts/video-1.txt"
            transcript = root / relative
            transcript.parent.mkdir(parents=True)
            content = b"Authorized transcript fixture."
            transcript.write_bytes(content)
            record = {
                "video_id": "video-1",
                "source_url": "https://www.youtube.com/watch?v=video-1",
                "transcript_path": relative,
                "transcript_sha256": hashlib.sha256(content).hexdigest(),
                "rights_status": "VERIFIED",
                "rights_evidence_ref": "creator-permission-fixture-002",
                "study_permission": True,
                "evaluation_permission": True,
                "training_permission": False,
            }
            intake = build_intake(catalog("complete"), manifest([record]), root=root)
            self.assertEqual(audit_weekly_tests(intake, weekly_evidence(), now=now)["status"], "BLOCKED_MISSING_WEEKLY_BUDDY_TESTS")
            stale = weekly_evidence([{
                "video_id": "video-1", "tested_at": (now - timedelta(days=8)).isoformat(),
                "status": "PASS", "buddy_model_id": "buddy-local", "buddy_model_version": "0.1.0",
                "run_id": "run-old", "suite_id": "suite-v1",
                "evaluation_permission_ref": "creator-permission-fixture-002", "result_sha256": "e" * 64,
            }])
            self.assertEqual(audit_weekly_tests(intake, stale, now=now)["status"], "FAILED_WEEKLY_BUDDY_TEST_EVIDENCE")

    def test_reports_evidence_for_video_ids_outside_catalog(self):
        intake = build_intake(catalog("complete"), manifest())
        evidence = weekly_evidence([{
            "video_id": "not-in-catalog",
            "tested_at": "2026-11-25T12:00:00+00:00",
            "status": "PASS",
            "buddy_model_id": "buddy-local",
            "buddy_model_version": "0.1.0",
            "run_id": "run-unknown",
            "suite_id": "freecodecamp-transcript-weekly-v1",
            "evaluation_permission_ref": "unknown-rights-ref",
            "result_sha256": "f" * 64,
        }])
        audit = audit_weekly_tests(intake, evidence, now=datetime(2026, 11, 25, 12, 0, tzinfo=timezone.utc))
        self.assertEqual(audit["unknown_evidence_video_ids"], ["not-in-catalog"])
        self.assertEqual(audit["tested_transcript_count"], 0)

    def test_path_traversal_and_unverified_rights_are_blocked(self):
        base = {
            "video_id": "video-1",
            "source_url": "https://www.youtube.com/watch?v=video-1",
            "transcript_path": "data/freecodecamp/authorized-transcripts/../../secret.txt",
            "transcript_sha256": "a" * 64,
            "rights_status": "VERIFIED",
            "rights_evidence_ref": "creator-permission-fixture-003",
            "study_permission": True,
            "evaluation_permission": True,
            "training_permission": False,
        }
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            intake = build_intake(catalog("complete"), manifest([base]), root=root)
            self.assertEqual(intake["queue"][0]["status"], "BLOCKED_TRANSCRIPT_PATH")
        unverified = {**base, "transcript_path": "data/freecodecamp/authorized-transcripts/video-1.txt", "rights_status": "REVIEW_REQUIRED"}
        with tempfile.TemporaryDirectory() as temp:
            intake = build_intake(catalog("complete"), manifest([unverified]), root=Path(temp))
            self.assertEqual(intake["queue"][0]["status"], "BLOCKED_RIGHTS_UNVERIFIED")

    def test_automatic_caption_scraping_and_duplicate_catalog_ids_are_rejected(self):
        bad_policy = manifest()
        bad_policy["rights_policy"]["automatic_caption_scraping"] = True
        with self.assertRaisesRegex(ValueError, "automatic caption scraping"):
            build_intake(catalog(), bad_policy)
        duplicate = catalog()
        duplicate["videos"].append(dict(duplicate["videos"][0]))
        with self.assertRaisesRegex(ValueError, "catalog video IDs must be unique"):
            build_intake(duplicate, manifest())


if __name__ == "__main__":
    unittest.main()
