#!/usr/bin/env python3
"""Safe, bounded per-MasterBot training checkpoint runner.

Selects and checkpoints one eligible gap. Actual weight training or paid model
calls require a separately registered, explicitly approved execution adapter.
"""
from __future__ import annotations
import argparse, hashlib, json, os
from datetime import datetime, timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
REGISTRY=ROOT/"config/masterbot-65-registry.json"
GAPS=ROOT/"config/generated/masterbot-capability-gaps.json"
STATE_ROOT=ROOT/"artifacts/masterbot-training"

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--masterbot",required=True)
    ap.add_argument("--state-dir",type=Path)
    ap.add_argument("--max-items",type=int,default=1)
    ap.add_argument("--budget-seconds",type=int,default=45)
    ap.add_argument("--github-output",type=Path)
    args=ap.parse_args()
    if not 1<=args.max_items<=3 or not 5<=args.budget_seconds<=90:
        raise SystemExit("Bounds: max-items 1..3, budget-seconds 5..90.")
    registry=json.loads(REGISTRY.read_text(encoding="utf-8"))
    bots=registry["masterbots"]
    bot=next((b for b in bots if b["name"]==args.masterbot),None)
    if bot is None: raise SystemExit("Unknown MasterBot; registry is canonical.")
    gap_payload=json.loads(GAPS.read_text(encoding="utf-8")) if GAPS.exists() else {"queue":[]}
    gaps=[g for g in gap_payload.get("queue",[]) if g.get("masterbot")==args.masterbot or g.get("division")==args.masterbot]
    gaps.sort(key=lambda g:(int(g.get("priority",99)),str(g.get("id",""))))
    selected=gaps[:args.max_items]
    state_dir=args.state_dir or (STATE_ROOT/bot["name"])
    state_dir.mkdir(parents=True,exist_ok=True)
    state_path=state_dir/"latest-checkpoint.json"
    previous={}
    if state_path.exists():
        try: previous=json.loads(state_path.read_text(encoding="utf-8"))
        except (ValueError,OSError): previous={}
    checkpoint={
      "schema":"dreamco.masterbot_training_checkpoint.v2",
      "masterbot_id":bot["id"],"masterbot":bot["name"],"lane_id":bot["lane_id"],
      "type":bot["type"],"updated_at":datetime.now(timezone.utc).isoformat(),
      "commit":os.environ.get("GITHUB_SHA","local"),"run_id":os.environ.get("GITHUB_RUN_ID","local"),
      "sequence":int(previous.get("sequence",0))+1,
      "mode":"sandbox_first","logical_training_policy":"24x7_gap_closure",
      "queue_digest":hashlib.sha256(json.dumps(selected,sort_keys=True).encode()).hexdigest(),
      "eligible_gap_count":len(gaps),"selected_gaps":selected,
      "next_actions":["load current gap inventory","measure baseline","practice in isolated sandbox","run held-out benchmark","record repeatable evidence","requeue unresolved or regressed gaps"],
      "execution":{"status":"queued_for_registered_runner" if selected else "idle_no_eligible_gap","items_claimed":0,"items_executed":0,"budget_seconds":args.budget_seconds,"reason":"No approved executable training adapter is registered for this lane; this runner checkpoints and prioritizes work only."},
      "evidence":{"baseline":False,"held_out_benchmark":False,"repeat_pass":False,"regression_check":False},
      "mastery_claim":"not_claimed_without_repeatable_evidence",
      "safety":{"paid_services_called":False,"credentials_read":False,"production_side_effects":False,"automatic_model_promotion":False,"quota_bypass":False,"manufactured_work":False},
      "previous_checkpoint_sequence":previous.get("sequence",0)
    }
    state_path.write_text(json.dumps(checkpoint,indent=2)+"\n",encoding="utf-8")
    if args.github_output:
        with args.github_output.open("a",encoding="utf-8") as f:
            f.write("selected_gaps="+str(len(selected))+"\n")
            f.write("checkpoint_status="+checkpoint["execution"]["status"]+"\n")
    print(json.dumps({"masterbot":bot["name"],"lane":bot["lane_id"],"eligible_gaps":len(gaps),"selected":len(selected),"executed":0,"checkpoint":str(state_path)},indent=2))
if __name__=="__main__": main()
