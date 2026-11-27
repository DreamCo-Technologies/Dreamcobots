#!/usr/bin/env python3
"""Run a single approved Buddy model-training manifest."""
from __future__ import annotations
import argparse,json
from buddy.datasets.transformers_runner import execute_job

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--job",required=True)
    parser.add_argument("--compute-approval-id",required=True)
    parser.add_argument("--output-root",default="artifacts/buddy-trained-models")
    parser.add_argument("--execute-approved",action="store_true",help="Required to execute training")
    parser.add_argument("--allow-model-download",action="store_true",help="Also requires DREAMCO_ALLOW_MODEL_DOWNLOAD=1")
    args=parser.parse_args()
    if not args.execute_approved:
        raise SystemExit("Refusing to train without --execute-approved")
    result=execute_job(args.job,args.compute_approval_id,args.output_root,args.allow_model_download)
    print(json.dumps({"job_id":result["job_id"],"weights_trained":result["weights_trained"],"artifact_dir":result["artifact_dir"],"production_promoted":False}))
if __name__=="__main__":
    main()
