"""Fail-closed release gate for DreamCo's fleet and executable evidence.

A successful catalog build is not a production certification.
"""
import argparse
import json
from pathlib import Path

REQUIRED=("model_comparison_verified","coding_sandbox_verified",
          "research_sources_verified","tool_execution_verified",
          "security_review_passed","deployment_smoke_passed")

def evaluate_release(goals, evidence):
    rows=goals.get("goals",[])
    if goals.get("schema")!="dreamco.all_bot_goals.v1":
        raise ValueError("unknown goal inventory")
    receipts=evidence.get("goals",{})
    ready=[]; blocked=[]
    for goal in rows:
        checks=receipts.get(goal["id"],{})
        missing=[k for k in REQUIRED if checks.get(k) is not True]
        if missing:
            blocked.append({"goal_id":goal["id"],"missing":missing})
        else:
            ready.append(goal["id"])
    return {"schema":"dreamco.production_release_gate.v1",
            "total_goals":len(rows),"evidence_ready_goals":len(ready),
            "blocked_goals":len(blocked),
            "fleet_production_ready":bool(rows) and not blocked,
            "ready_goal_ids":ready,
            "blocked_sample":blocked[:100],
            "requirements":list(REQUIRED),
            "note":"This gate checks supplied attestations, not their authenticity. Independent signed evidence validation is still required."}

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--evidence",default="website/data/buddy-production-evidence.json")
    args=parser.parse_args()
    root=Path(__file__).resolve().parents[2]
    goals=json.loads((root/"website/data/buddy-all-bot-goals.json").read_text())
    path=root/args.evidence
    evidence=json.loads(path.read_text()) if path.exists() else {"goals":{}}
    report=evaluate_release(goals,evidence)
    dest=root/"website/data/buddy-production-release-gate.json"
    dest.write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps({k:report[k] for k in ("total_goals","evidence_ready_goals","blocked_goals","fleet_production_ready")}))

if __name__=="__main__":
    main()
