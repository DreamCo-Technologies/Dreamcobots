#!/usr/bin/env python3
"""Create a governed cross-model benchmark manifest from reviewed candidate metadata."""
from __future__ import annotations
import argparse,json
from buddy.datasets.hub import DatasetHub
from buddy.datasets.benchmark_jobs import create_benchmark_job

def main():
 p=argparse.ArgumentParser();p.add_argument("--request",required=True);p.add_argument("--output-dir",default="artifacts/buddy-model-benchmarks")
 a=p.parse_args();request=json.loads(open(a.request,encoding="utf-8").read())
 job=create_benchmark_job(DatasetHub(request.get("dataset_hub_path")),request["dataset_id"],
  int(request["masterbot_id"]),request["candidates"],request["compute_approval_id"],a.output_dir)
 print(json.dumps({"job_id":job["job_id"],"status":job["status"],"execution_status":job["execution_status"],"manifest_path":job["manifest_path"]}))
if __name__=="__main__":main()
