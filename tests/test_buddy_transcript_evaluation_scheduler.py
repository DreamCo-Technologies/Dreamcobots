import json
import unittest
from pathlib import Path

from buddy.learning.transcript_evaluation_scheduler import (
    build_weekly_transcript_evaluation_plan,
    validate_weekly_transcript_evaluation_plan,
)


class WeeklyTranscriptEvaluationTests(unittest.TestCase):
    def test_only_rights_cleared_hashed_authorized_transcripts_are_eligible(self):
        catalog = {"videos": [
            {"video_id": "ok-1", "rights_status": "rights_cleared",
             "transcript_status": "rights_cleared_and_ingested",
             "transcript_sha256": "a" * 64, "transcript_evaluation_authorized": True},
            {"video_id": "blocked-1", "rights_status": "review_required",
             "transcript_status": "not_ingested_rights_gate"},
        ]}
        plan = build_weekly_transcript_evaluation_plan(catalog, "2026-11-23")
        validate_weekly_transcript_evaluation_plan(plan)
        self.assertEqual(plan["eligible_transcript_count"], 1)
        self.assertEqual(plan["blocked_transcript_count"], 1)
        self.assertEqual(plan["eligible"][0]["due_by"], "2026-11-29")
        self.assertEqual(plan["eligible"][0]["execution_status"], "PLAN_ONLY_NOT_EXECUTED")
        self.assertNotIn("transcript_text", plan["eligible"][0])
        self.assertFalse(plan["buddy_evaluation_executed"])
        self.assertFalse(plan["model_training_allowed"])

    def test_current_catalog_blocks_unlicensed_transcripts(self):
        root = Path(__file__).resolve().parents[1]
        catalog_path = root / "config/generated/freecodecamp-youtube-catalog.json"
        if not catalog_path.exists():
            self.skipTest("generated FreeCodeCamp catalog is absent in this checkout")
        catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
        plan = build_weekly_transcript_evaluation_plan(catalog, "2026-11-23")
        validate_weekly_transcript_evaluation_plan(plan)
        self.assertEqual(plan["eligible_transcript_count"], 0)
        self.assertEqual(plan["blocked_transcript_count"], len(catalog["videos"]))
        self.assertEqual(plan["status"], "BLOCKED_NO_RIGHTS_CLEARED_TRANSCRIPTS")

    def test_missing_hash_or_explicit_authorization_blocks_record(self):
        catalog = {"videos": [
            {"video_id": "no-hash", "rights_status": "rights_cleared",
             "transcript_status": "rights_cleared_and_ingested",
             "transcript_evaluation_authorized": True},
            {"video_id": "no-auth", "rights_status": "rights_cleared",
             "transcript_status": "rights_cleared_and_ingested",
             "transcript_sha256": "b" * 64, "transcript_evaluation_authorized": False},
        ]}
        plan = build_weekly_transcript_evaluation_plan(catalog, "2026-11-23")
        self.assertEqual(plan["eligible_transcript_count"], 0)
        self.assertEqual(plan["blocked_transcript_count"], 2)
        validate_weekly_transcript_evaluation_plan(plan)

    def test_duplicate_video_ids_fail_closed(self):
        with self.assertRaisesRegex(ValueError, "duplicate video_id"):
            build_weekly_transcript_evaluation_plan(
                {"videos": [{"video_id": "same"}, {"video_id": "same"}]},
                "2026-11-23",
            )

    def test_invalid_hash_in_eligible_record_is_blocked(self):
        plan = build_weekly_transcript_evaluation_plan({"videos": [{
            "video_id": "bad-hash", "rights_status": "rights_cleared",
            "transcript_status": "rights_cleared_and_ingested",
            "transcript_sha256": "not-a-hash", "transcript_evaluation_authorized": True,
        }]}, "2026-11-23")
        self.assertEqual(plan["eligible_transcript_count"], 0)
        self.assertEqual(plan["blocked_transcript_count"], 1)
        validate_weekly_transcript_evaluation_plan(plan)

    def test_empty_catalog_has_explicit_status(self):
        plan = build_weekly_transcript_evaluation_plan({"videos": []}, "2026-11-23")
        self.assertEqual(plan["status"], "NO_TRANSCRIPT_RECORDS")
        validate_weekly_transcript_evaluation_plan(plan)


if __name__ == "__main__":
    unittest.main()
