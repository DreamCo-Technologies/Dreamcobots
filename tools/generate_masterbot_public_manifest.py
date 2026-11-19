#!/usr/bin/env python3
"""Generate the public Actions fleet manifest from the canonical registry."""
from __future__ import annotations
import argparse,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
REG=ROOT/"config/masterbot-65-registry.json"
OUT=ROOT/"website/data/masterbot-fleet.json"

def build():
    reg=json.loads(REG.read_text(encoding="utf-8"))
    bots=reg["masterbots"]
    return {
      "schema":"dreamco.masterbot_public_fleet.v1",
      "summary":{"total":len(bots),"domain":sum(b["type"]=="domain" for b in bots),"platform":sum(b["type"]=="platform" for b in bots),"maxParallel":reg["matrix_policy"]["max_parallel"],"lanesPerTick":reg["matrix_policy"]["lanes_per_tick"],"fleetCycleMinutes":reg["matrix_policy"]["full_fleet_cycle_minutes"],"schedule":"Every five minutes (GitHub best-effort)"},
      "policy":{"training":"24x7 logical gap-closure; execute only when eligible work and runner capacity exist.","evidence":"No mastery claim without repeatable benchmark evidence.","capacity":"Bounded public Actions capacity; no quota bypass or manufactured work."},
      "bootcamp":{"url":"buddy-bootcamp.html","config":"../config/buddy-bootcamp-65.json","levels":8},
      "workflow":"https://github.com/DreamCo-Technologies/Dreamcobots/actions/workflows/buddy-65-masterbot-training.yml",
      "masterbots":bots
    }

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--check",action="store_true")
    args=ap.parse_args()
    content=json.dumps(build(),indent=2)+"\n"
    if args.check:
        if not OUT.exists() or OUT.read_text(encoding="utf-8")!=content:
            raise SystemExit("Public MasterBot manifest is stale; regenerate it.")
    else:
        OUT.parent.mkdir(parents=True,exist_ok=True)
        OUT.write_text(content,encoding="utf-8")
    print(json.dumps({"public_manifest":str(OUT.relative_to(ROOT)),"masterbots":65}))
if __name__=="__main__": main()
