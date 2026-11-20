#!/usr/bin/env python3
"""Run an explicitly approved open-weight model comparison."""
from __future__ import annotations
import argparse,json
from buddy.datasets.benchmark_runner import execute_benchmark

def main():
 p=argparse.ArgumentParser();p.add_argument("--job",required=True);p.add_argument("--compute-approval-id",required=True)
 p.add_argument("--output-root",default="artifacts/buddy-model-benchmarks");p.add_argument("--execute-approved",action="store_true")
 p.add_argument("--allow-model-download",action="store_true");a=p.parse_args()
 if not a.execute_approved: raise SystemExit("Refusing benchmark execution without --execute-approved")
 result=execute_benchmark(a.job,a.compute_approval_id,a.output_root,a.allow_model_download)
 print(json.dumps({"job_id":result["job_id"],"models_scored":sum(x["status"]=="SCORED" for x in result["results"]),"result_path":result["result_path"],"production_promotion":False}))
if __name__=="__main__":main()
