#!/usr/bin/env python3
"""Select a fair rotating slice from the canonical 65 logical MasterBot lanes."""
from __future__ import annotations
import argparse,json
from datetime import datetime,timezone
from pathlib import Path
from validate_masterbot_registry import validate

def select(at:datetime,count:int):
    data=validate()
    bots=data["masterbots"]
    if count<1 or count>len(bots): raise ValueError("count must be between 1 and fleet size")
    slot=int(at.astimezone(timezone.utc).timestamp()//300)
    start=(slot*count)%len(bots)
    selected=[bots[(start+i)%len(bots)]["name"] for i in range(count)]
    return {"slot":slot,"start":start,"count":count,"fleet_size":len(bots),"masterbots":selected}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--count",type=int,default=5)
    ap.add_argument("--at",help="Timezone-aware ISO timestamp for deterministic tests")
    ap.add_argument("--github-output",type=Path)
    args=ap.parse_args()
    at=datetime.fromisoformat(args.at.replace("Z","+00:00")) if args.at else datetime.now(timezone.utc)
    if at.tzinfo is None: raise SystemExit("--at must include timezone")
    result=select(at,args.count)
    if args.github_output:
        with args.github_output.open("a",encoding="utf-8") as f:
            f.write("masterbots="+json.dumps(result["masterbots"],separators=(",",":"))+"\n")
            f.write("rotation_slot="+str(result["slot"])+"\n")
            f.write("rotation_start="+str(result["start"])+"\n")
    print(json.dumps(result,indent=2))
if __name__=="__main__": main()
