"""Create a bounded, review-only Buddy training backlog from measured gap evidence."""
import argparse
import json
from pathlib import Path

def propose(plan, daily):
    if plan.get("schema") != "dreamco.unified_build_training_plan.v1":
        raise ValueError("unexpected build plan schema")
    if daily.get("schema") != "dreamco.daily_capability_lab.v1":
        raise ValueError("unexpected evidence schema")
    tasks = []
    for row in daily.get("results", []):
        if row.get("duplicate_of"):
            continue
        gaps = row.get("gaps", [])
        if not gaps:
            continue
        tasks.append({"id": "train-review:" + row["id"], "capability_id": row["id"],
                      "kind": row["kind"], "status": "proposal_only",
                      "observed_gaps": gaps,
                      "next_step": "Obtain executable baseline and independent heldout benchmark",
                      "candidate_methods": plan["training_loop"]["methods"][:3],
                      "required_approvals": ["dataset_rights", "owner", "compute_budget", "promotion_review"],
                      "training_started": False, "production_certified": False})
    return {"schema": "dreamco.training_backlog.v1", "tasks": tasks,
            "total": len(tasks), "automatic_execution": False}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--plan", default="config/buddy/unified-build-training-plan.json")
    parser.add_argument("--evidence", default="website/data/buddy-daily-lab.json")
    parser.add_argument("--output", default="website/data/buddy-training-backlog.json")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[2]
    plan = json.loads((root / args.plan).read_text(encoding="utf-8"))
    daily = json.loads((root / args.evidence).read_text(encoding="utf-8"))
    output = (root / args.output).resolve()
    if not output.is_relative_to(root / "website" / "data"):
        parser.error("output must be under website/data")
    output.parent.mkdir(parents=True, exist_ok=True)
    report = propose(plan, daily)
    output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"proposed": report["total"], "training_started": 0}))

if __name__ == "__main__":
    main()
