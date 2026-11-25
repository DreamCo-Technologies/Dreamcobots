#!/usr/bin/env python3
"""Build a human-approved sales and public-procurement work queue.

Inputs must be sourced O*NET task curricula and official opportunity records.
The tool never contacts buyers, submits bids, or fabricates eligibility.
"""
from __future__ import annotations
import argparse, json
from datetime import date
from pathlib import Path
from typing import Any

def build(task_doc:dict[str,Any],opp_doc:dict[str,Any],today:date)->dict[str,Any]:
    tasks=[]
    for occ in task_doc.get("occupations",[]):
        for task in occ.get("tasks",[]):
            tasks.append({"occupation_code":occ.get("occupation_code"),"occupation_title":occ.get("occupation_title"),
              "task_id":task.get("task_id"),"task":task.get("task"),
              "pipeline_stage":"offer_research","status":"needs_capability_and_buyer_validation",
              "sales_actions":["identify buyer segment","validate real customer need","verify required credentials and insurance",
                "define scope and exclusions","build cost and price model","prepare truthful capability evidence"],
              "human_approval_required":True})
    opportunities=[]
    for item in opp_doc.get("opportunities",[]):
        due=None
        due_date_error=None
        try:
            due=date.fromisoformat(str(item.get("due_date",""))[:10])
        except ValueError as exc:
            due_date_error=f"invalid or missing due_date: {exc}"
        due_date_valid=due is not None
        active=item.get("active") is True
        expired=bool(due_date_valid and due<today)
        not_expired=due_date_valid and not expired
        eligible=item.get("eligibility_verified") is True
        capability=item.get("capability_match_verified") is True
        compliance=item.get("compliance_review_passed") is True
        score=sum((active,due_date_valid,not_expired,eligible,capability,compliance))
        status="bid_review_ready" if score==6 else ("expired_or_inactive" if expired or not active else "human_review_required")
        opportunities.append({"opportunity_id":item.get("opportunity_id"),"title":item.get("title"),
          "agency":item.get("agency"),"due_date":item.get("due_date"),"url":item.get("url"),
          "naics":item.get("naics"),"readiness_score":score,"readiness_checks":6,"due_date_valid":due_date_valid,"due_date_error":due_date_error,"status":status,
          "missing_checks":[name for name,ok in [("active",active),("due_date_valid",due_date_valid),("not_expired",not_expired),("eligibility_verified",eligible),("capability_match_verified",capability),("compliance_review_passed",compliance)] if not ok],
          "next_actions":["review solicitation and amendments","build compliance matrix","calculate fully burdened cost and risk","confirm partner/subcontract roles","human approval before bid submission"],
          "human_approval_required":True})
    return {"schema":"dreamco.sales_and_procurement_pipeline.v1",
      "counts":{"onet_task_playbooks":len(tasks),"opportunities":len(opportunities),
        "bid_review_ready":sum(x["status"]=="bid_review_ready" for x in opportunities),
        "human_review_required":sum(x["status"]=="human_review_required" for x in opportunities)},
      "task_playbooks":tasks,"government_opportunities":opportunities,
      "policy":{"no_auto_outreach":True,"no_auto_bid_submission":True,"no_guaranteed_awards_or_income":True,
        "benefits_or_grant_eligibility_requires_official_review":True}}

def main()->int:
    p=argparse.ArgumentParser()
    p.add_argument("--onet",required=True); p.add_argument("--opportunities",required=True)
    p.add_argument("--out",required=True); p.add_argument("--today",default=date.today().isoformat())
    a=p.parse_args()
    result=build(json.loads(Path(a.onet).read_text()),json.loads(Path(a.opportunities).read_text()),date.fromisoformat(a.today))
    Path(a.out).parent.mkdir(parents=True,exist_ok=True)
    Path(a.out).write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps(result["counts"],indent=2))
    return 0
if __name__=="__main__": raise SystemExit(main())
