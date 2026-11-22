#!/usr/bin/env python3
"""Run Buddy's unknown-problem router and persist a reviewable research task."""
from __future__ import annotations
import argparse, json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from buddy.datasets.unknown_router import route_problem

def main() -> int:
    parser=argparse.ArgumentParser()
    parser.add_argument("--problem",required=True)
    parser.add_argument("--external",action="store_true",help="Search metadata APIs; requires DREAMCO_ALLOW_SOURCE_NETWORK=1")
    parser.add_argument("--out",default="artifacts/buddy-dataset-hub/unknown-problem-route.json")
    args=parser.parse_args()
    result=route_problem(args.problem,external=args.external)
    out=Path(args.out); out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps({"status":result["status"],"masterbot_candidates":len(result["masterbot_candidates"]),"local_datasets":len(result["local_dataset_candidates"]),"external_candidates":len(result["external_metadata_candidates"]),"problem_solved":False,"weights_trained":False}))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
