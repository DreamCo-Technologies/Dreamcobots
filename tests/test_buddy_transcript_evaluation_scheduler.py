import unittest
from buddy.learning.transcript_evaluation_scheduler import build_weekly_transcript_evaluation_plan,validate_weekly_transcript_evaluation_plan

class WeeklyTranscriptEvaluationTests(unittest.TestCase):
    def test_weekly_plan_includes_each_rights_cleared_transcript_once(self):
        catalog={"videos":[
            {"video_id":"ok-1","rights_status":"rights_cleared","transcript_status":"rights_cleared_and_ingested",
             "transcript_sha256":"a"*64,"transcript_evaluation_authorized":True},
            {"video_id":"blocked-1","rights_status":"review_required","transcript_status":"not_ingested_rights_gate"}]}
        plan=build_weekly_transcript_evaluation_plan(catalog,"2026-11-23")
        validate_weekly_transcript_evaluation_plan(plan)
        self.assertEqual(plan["eligible_transcript_count"],1)
        self.assertEqual(plan["blocked_transcript_count"],1)
        self.assertEqual(plan["eligible"][0]["video_id"],"ok-1")
        self.assertEqual(plan["eligible"][0]["due_by"],"2026-11-29")
        self.assertEqual(plan["eligible"][0]["execution_status"],"PLAN_ONLY_NOT_EXECUTED")
        self.assertNotIn("transcript_text",plan["eligible"][0])

    def test_no_rights_cleared_transcript_is_not_claimed_as_tested(self):
        catalog={"videos":[{"video_id":"fcc-1","rights_status":"review_required",
            "transcript_status":"not_ingested_rights_gate","transcript_ingestion_allowed":False}]}
        plan=build_weekly_transcript_evaluation_plan(catalog,"2026-11-23")
        validate_weekly_transcript_evaluation_plan(plan)
        self.assertEqual(plan["eligible_transcript_count"],0)
        self.assertEqual(plan["blocked_transcript_count"],1)
        self.assertEqual(plan["status"],"BLOCKED_NO_RIGHTS_CLEARED_TRANSCRIPTS")
        self.assertFalse(plan["buddy_evaluation_executed"])
