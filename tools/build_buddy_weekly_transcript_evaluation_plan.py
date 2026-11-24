#!/usr/bin/env python3
"""Create a weekly evaluation queue from rights-cleared transcript metadata only."""
import argparse,json
from pathlib import Path
from buddy.learning.transcript_evaluation_scheduler import build_weekly_transcript_evaluation_plan,validate_weekly_transcript_evaluation_plan

def main():
 p=argparse.ArgumentParser();p.add_argument("--catalog",default="config/generated/freecodecamp-youtube-catalog.json")
 p.add_argument("--output",default="artifacts/buddy-dataset-hub/weekly-transcript-evaluation-plan.json");p.add_argument("--week-start")
 a=p.parse_args();catalog=json.loads(Path(a.catalog).read_text(encoding="utf-8"))
 plan=build_weekly_transcript_evaluation_plan(catalog,a.week_start);validate_weekly_transcript_evaluation_plan(plan)
 out=Path(a.output);out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(plan,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
 print(json.dumps({"eligible_transcripts":plan["eligible_transcript_count"],"blocked_transcripts":plan["blocked_transcript_count"],
  "frequency":plan["frequency"],"status":plan["status"],"transcript_content_included":False,"buddy_evaluation_executed":False},indent=2))
if __name__=="__main__":main()
