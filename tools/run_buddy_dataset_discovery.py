#!/usr/bin/env python3
"""Run a bounded rotating public dataset discovery scan across MasterBot lanes."""
from __future__ import annotations
import argparse,json
from pathlib import Path
from buddy.datasets.discovery_fleet import run_discovery_fleet
def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--lanes-per-run",type=int,default=5)
    parser.add_argument("--offset",type=int)
    parser.add_argument("--limit",type=int,default=3)
    parser.add_argument("--out",default="artifacts/buddy-dataset-hub/discovery-fleet.json")
    args=parser.parse_args()
    result=run_discovery_fleet(lanes_per_run=args.lanes_per_run,offset=args.offset,limit=args.limit)
    out=Path(args.out);out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps({"lanes_scanned":len(result["lanes_scanned"]),"candidates_recorded":result["candidates_recorded"],
      "source_error_categories":result["source_errors"],"files_downloaded":False,"training_approved":False,"weights_trained":False}))
if __name__=="__main__":main()
