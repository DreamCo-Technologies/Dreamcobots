#!/usr/bin/env python3
"""Create a governed Buddy training job from an operator-reviewed request JSON."""
from __future__ import annotations
import argparse,json
from buddy.datasets.hub import DatasetHub
from buddy.datasets.training_jobs import create_training_job

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--request",required=True)
    parser.add_argument("--output-dir",default="artifacts/buddy-training-jobs")
    args=parser.parse_args()
    request=json.loads(open(args.request,encoding="utf-8").read())
    hub=DatasetHub(request.get("dataset_hub_path"))
    job=create_training_job(hub,dataset_id=request["dataset_id"],masterbot_id=int(request["masterbot_id"]),
        model_id=request["model_id"],base_model_revision=request["base_model_revision"],
        compute_approval_id=request["compute_approval_id"],model_license=request["model_license"],
        model_license_url=request["model_license_url"],model_license_status=request["model_license_status"],
        model_license_evidence=request["model_license_evidence"],training_method=request.get("training_method","sft"),
        max_steps=int(request.get("max_steps",100)),output_dir=args.output_dir)
    print(json.dumps({"job_id":job["job_id"],"status":job["status"],"execution_status":job["execution_status"],"manifest_path":job["manifest_path"]}))
if __name__=="__main__":
    main()
