#!/usr/bin/env python3
"""Register a reviewed dataset card and optional local data file in the DreamCo Hub."""
from __future__ import annotations
import argparse,json
from pathlib import Path
from buddy.datasets.hub import DatasetHub

def main():
 parser=argparse.ArgumentParser()
 parser.add_argument("--card",required=True)
 parser.add_argument("--file")
 args=parser.parse_args()
 card=json.loads(Path(args.card).read_text(encoding="utf-8"))
 result=DatasetHub().register(card,args.file)
 print(json.dumps({"dataset_id":result["dataset_id"],"version":result["version"],"training_status":result["training_status"],"content_sha256":result["content_sha256"]}))
if __name__=="__main__":main()
