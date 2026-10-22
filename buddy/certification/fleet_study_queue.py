"""Join fleet goals with independently verified task champions; emit bounded study queue.

Never treats declared bot profiles or unverified model scores as production evidence.
"""
import argparse
import json
from pathlib import Path

def make_queue(goals_report, champion_report, *, max_items=250):
    if goals_report.get("schema") != "dreamco.all_bot_goals.v1":
        raise ValueError("unexpected fleet goals schema")
    if champion_report.get("schema") != "dreamco.task_champions.v1":
        raise ValueError("unexpected task champions schema")
    if not 1 <= max_items <= 1000:
        raise ValueError("invalid queue budget")
    verified = {}
    for c in champion_report.get("champions", []):
        if c.get("selection_basis") != "independently_verified_comparable_trials":
            continue
        # Task ID must be explicitly mapped to a bot goal ID; never fuzzy-join model claims.
        if c.get("goal_id") and c.get("champion_model"):
            verified.setdefault(c["goal_id"], []).append(c)
    queue = []
    for goal in goals_report.get("goals", []):
        matches = verified.get(goal["id"], [])
        matches.sort(key=lambda c: (c.get("buddy_gap") is None,
                                    -(c.get("buddy_gap") or 0)))
        champion = matches[0] if matches else None
        gap = champion.get("buddy_gap") if champion else None
        if champion is None:
            action = "design_independent_executable_benchmark"
            priority = 1
        elif gap is None:
            action = "run_buddy_on_same_verified_task"
            priority = 2
        elif gap > 0:
            action = "study_and_retest_specific_failure"
            priority = 3
        else:
            action = "regression_and_reliability_checks"
            priority = 4
        queue.append({"goal_id":goal["id"],"bot_id":goal["bot_id"],
                      "division":goal["division"],"goal":goal["goal"],
                      "priority":priority,"next_action":action,
                      "champion_model":champion["champion_model"] if champion else None,
                      "buddy_gap":gap,
                      "study_sources":goal.get("declared_learning_plan",[]),
                      "tools_needed":goal.get("tools_needed",[]),
                      "status":"review_required","paid_execution_approved":False,
                      "training_started":False,"production_certified":False})
    queue.sort(key=lambda x:(x["priority"],x["division"],x["bot_id"],x["goal_id"]))
    return {"schema":"dreamco.fleet_study_queue.v1",
            "total_discovered":len(queue),"queued":min(len(queue),max_items),
            "remaining":max(0,len(queue)-max_items),
            "tasks":queue[:max_items],"automatic_paid_execution":False,
            "note":"No champion is inferred without an explicit verified goal mapping."}

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--max-items",type=int,default=250)
    args=parser.parse_args()
    root=Path(__file__).resolve().parents[2]
    goals=json.loads((root/"website/data/buddy-all-bot-goals.json").read_text())
    # Champion evidence is optional; missing means there are no verified task champions.
    p=root/"website/data/buddy-task-champions.json"
    champions=json.loads(p.read_text()) if p.exists() else {"schema":"dreamco.task_champions.v1","champions":[]}
    report=make_queue(goals,champions,max_items=args.max_items)
    out=root/"website/data/buddy-fleet-study-queue.json"
    out.write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps({"queued":report["queued"],"remaining":report["remaining"]}))

if __name__=="__main__":
    main()
