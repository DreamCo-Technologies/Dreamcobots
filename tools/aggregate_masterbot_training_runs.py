#!/usr/bin/env python3
"""Aggregate per-division run records into a provenance-preserving shared queue."""
from __future__ import annotations
import argparse, json
from datetime import datetime, timezone
from pathlib import Path

def main() -> int:
    p=argparse.ArgumentParser()
    p.add_argument("--input", required=True)
    p.add_argument("--output", required=True)
    a=p.parse_args()
    root=Path(a.input)
    records=[]
    paths = set(root.rglob("latest-plan.json")) | set(root.rglob("latest-checkpoint.json"))
    for path in sorted(paths):
        try:
            record=json.loads(path.read_text(encoding="utf-8"))
            records.append({
                "masterbot_id":record.get("masterbot_id"),
                "masterbot":record.get("masterbot"),
                "run_id":record.get("run_id"),
                "run_attempt":record.get("run_attempt"),
                "record_path":str(path),
                "lifecycle_status":record.get("status","PLAN_ONLY_NOT_EXECUTED"),
                "next_actions":record.get("next_actions",[]),
                "shareable_lesson_refs":record.get("shareable_lesson_refs",[]),
                "weights_trained":record.get("weights_trained",False),
                "mastery_claim":record.get("mastery_claim","not_claimed_without_evidence")
            })
        except (OSError, json.JSONDecodeError) as exc:
            records.append({"record_path":str(path),"error":str(exc)})
    names={r.get("masterbot") for r in records if r.get("masterbot")}
    payload={
        "schema":"dreamco.cross_division_learning_queue.v1",
        "created_at":datetime.now(timezone.utc).isoformat(),
        "records_received":len(records),
        "unique_divisions_reported":len(names),
        "expected_divisions":65,
        "missing_divisions_count":max(0,65-len(names)),
        "shared_learning_policy":"Share only versioned lesson metadata, benchmark learnings and verified fixes; consumers must recheck rights and compatibility.",
        "raw_dataset_pooling":False,
        "automatic_weight_merging":False,
        "records":records,
        "status":"AGGREGATED_RUN_EVIDENCE_NOT_MODEL_TRAINING"
    }
    out=Path(a.output); out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(payload,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({k:payload[k] for k in ("records_received","unique_divisions_reported","missing_divisions_count","status")},indent=2))
    return 0
if __name__=="__main__":
    raise SystemExit(main())
