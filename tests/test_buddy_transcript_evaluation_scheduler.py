from buddy.learning.transcript_evaluation_scheduler import build_weekly_transcript_evaluation_plan,validate_weekly_transcript_evaluation_plan

def test_weekly_plan_includes_each_rights_cleared_transcript_once():
 catalog={"videos":[{"video_id":"ok-1","rights_status":"rights_cleared","transcript_status":"rights_cleared_and_ingested","transcript_sha256":"a"*64,"transcript_evaluation_authorized":True},
 {"video_id":"blocked-1","rights_status":"review_required","transcript_status":"not_ingested_rights_gate"}]}
 plan=build_weekly_transcript_evaluation_plan(catalog,"2026-11-23");validate_weekly_transcript_evaluation_plan(plan)
 assert plan["eligible_transcript_count"]==1 and plan["blocked_transcript_count"]==1
 assert plan["eligible"][0]["video_id"]=="ok-1" and plan["eligible"][0]["due_by"]=="2026-11-29"
 assert plan["eligible"][0]["execution_status"]=="PLAN_ONLY_NOT_EXECUTED"
 assert "transcript_text" not in plan["eligible"][0]

def test_no_rights_cleared_transcript_is_not_claimed_as_tested():
 catalog={"videos":[{"video_id":"fcc-1","rights_status":"review_required","transcript_status":"not_ingested_rights_gate","transcript_ingestion_allowed":False}]}
 plan=build_weekly_transcript_evaluation_plan(catalog,"2026-11-23");validate_weekly_transcript_evaluation_plan(plan)
 assert plan["eligible_transcript_count"]==0 and plan["blocked_transcript_count"]==1
 assert plan["status"]=="BLOCKED_NO_RIGHTS_CLEARED_TRANSCRIPTS"
 assert plan["buddy_evaluation_executed"] is False
