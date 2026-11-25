"""Check that every expanded revenue lane has a complete learning playbook blueprint."""
from __future__ import annotations
import argparse, json
from pathlib import Path
from typing import Any
ROOT = Path(__file__).resolve().parents[1]


def validate(lanes: dict[str, Any], playbooks: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    source = lanes.get("lanes")
    rows = playbooks.get("lanes")
    if not isinstance(source, list) or not isinstance(rows, list):
        return ["source lanes and playbook lanes must both be arrays"]
    source_ids = [row.get("id") for row in source if isinstance(row, dict)]
    playbook_ids = [row.get("lane_id") for row in rows if isinstance(row, dict)]
    if len(source_ids) != len(set(source_ids)):
        errors.append("source revenue lane IDs are not unique")
    if len(playbook_ids) != len(set(playbook_ids)):
        errors.append("playbook lane IDs are not unique")
    if set(source_ids) != set(playbook_ids):
        errors.append("playbook lane IDs must exactly match expanded revenue lanes")
    by_id = {row.get("lane_id"): row for row in rows if isinstance(row, dict)}
    for lane in source:
        if not isinstance(lane, dict): continue
        row = by_id.get(lane.get("id"))
        if not row: continue
        if row.get("value") != lane.get("value") or row.get("monetization") != lane.get("monetization"):
            errors.append(f"{lane.get('id')}: source value or monetization mismatch")
        for field in ("learning_objective", "lane_specific_tasks", "shared_execution_sequence",
                      "required_software_research", "required_benchmark", "guardrails",
                      "truth_rules", "completion_evidence"):
            if not row.get(field):
                errors.append(f"{lane.get('id')}: missing {field}")
        tasks = row.get("lane_specific_tasks", [])
        if not isinstance(tasks, list) or len(tasks) < 4 or not all(isinstance(x, str) and x.strip() for x in tasks):
            errors.append(f"{lane.get('id')}: at least four lane-specific tasks are required")
        sequence = row.get("shared_execution_sequence", [])
        if not isinstance(sequence, list) or len(sequence) < 5:
            errors.append(f"{lane.get('id')}: shared execution sequence is incomplete")
        if row.get("status") != "playbook_defined_lesson_authoring_pending":
            errors.append(f"{lane.get('id')}: status must not imply completed lesson authoring")
    policy = playbooks.get("common_policy", {})
    for key in ("source_rights_required", "production_actions_require_explicit_approval",
                "actual_revenue_requires_transaction_evidence"):
        if policy.get(key) is not True:
            errors.append(f"common policy must require {key}")
    return errors


def main() -> int:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lanes",type=Path,default=ROOT/"money_os/config/revenue_lanes_expanded.json")
    parser.add_argument("--playbooks",type=Path,default=ROOT/"money_os/config/revenue_lane_learning_playbooks.json")
    args=parser.parse_args()
    errors=validate(json.loads(args.lanes.read_text()),json.loads(args.playbooks.read_text()))
    print(json.dumps({"status":"invalid" if errors else "valid","errors":errors},indent=2))
    return 1 if errors else 0

if __name__=="__main__": raise SystemExit(main())
