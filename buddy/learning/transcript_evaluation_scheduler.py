"""Weekly Buddy transcript evaluation planning with strict rights and provenance gates."""
from datetime import date, datetime, timedelta, timezone

def monday_of_week(value: str | None = None) -> date:
    day = date.fromisoformat(value) if value else datetime.now(timezone.utc).date()
    return day - timedelta(days=day.weekday())

def build_weekly_transcript_evaluation_plan(catalog: dict, week_start: str | None = None) -> dict:
    monday=monday_of_week(week_start); due=monday+timedelta(days=6); eligible=[]; blocked=[]
    for video in catalog.get("videos", []):
        allowed=(video.get("rights_status")=="rights_cleared" and video.get("transcript_status")=="rights_cleared_and_ingested"
            and bool(video.get("transcript_sha256")) and video.get("transcript_evaluation_authorized") is True)
        if allowed:
            eligible.append({"video_id":video.get("video_id"),"transcript_sha256":video["transcript_sha256"],
                "week_start":monday.isoformat(),"due_by":due.isoformat(),"status":"queued_for_weekly_buddy_evaluation",
                "execution_status":"PLAN_ONLY_NOT_EXECUTED","evaluation_suite":["transcript_comprehension",
                "source_grounded_question_answering","factual_consistency","citation_and_provenance","retention_and_transfer"]})
        else:
            blocked.append({"video_id":video.get("video_id"),"status":"blocked_transcript_rights_or_provenance",
                "reason":"requires_rights_cleared_ingested_transcript_hash_and_evaluation_authorization"})
    return {"schema":"dreamco.weekly_transcript_evaluation_plan.v1","frequency":"weekly","week_start":monday.isoformat(),
        "due_by":due.isoformat(),"every_eligible_transcript_once_per_week":True,"eligible_transcript_count":len(eligible),
        "blocked_transcript_count":len(blocked),"status":"PLAN_ONLY_NOT_EXECUTED" if eligible else
        ("BLOCKED_NO_RIGHTS_CLEARED_TRANSCRIPTS" if blocked else "NO_TRANSCRIPT_RECORDS"),"eligible":eligible,"blocked":blocked,
        "transcript_content_included":False,"model_training_allowed":False,"buddy_evaluation_executed":False}

def validate_weekly_transcript_evaluation_plan(plan: dict) -> None:
    if plan.get("frequency")!="weekly" or plan.get("every_eligible_transcript_once_per_week") is not True:
        raise ValueError("weekly transcript coverage contract missing")
    if plan.get("transcript_content_included") is not False or plan.get("model_training_allowed") is not False:
        raise ValueError("transcript content and training must remain gated")
    for item in plan.get("eligible", []):
        if not item.get("transcript_sha256") or item.get("execution_status")!="PLAN_ONLY_NOT_EXECUTED":
            raise ValueError("eligible transcript must have immutable hash and remain plan-only")
