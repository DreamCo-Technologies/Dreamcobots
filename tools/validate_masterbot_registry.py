#!/usr/bin/env python3
"""Validate the canonical 65-MasterBot registry and expose its matrix."""
from __future__ import annotations
import argparse, json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
REGISTRY=ROOT/"config/masterbot-65-registry.json"

def validate():
    data=json.loads(REGISTRY.read_text(encoding="utf-8"))
    bots=data.get("masterbots",[])
    if data.get("canonical_count") != 65 or len(bots) != 65:
        raise ValueError("Canonical registry must contain exactly 65 MasterBots.")
    ids=[b.get("id") for b in bots]; keys=[b.get("key") for b in bots]; lanes=[b.get("lane_id") for b in bots]
    if len(set(ids))!=65 or len(set(keys))!=65 or len(set(lanes))!=65:
        raise ValueError("MasterBot IDs, keys and dedicated lane IDs must be unique.")
    if sum(b.get("type")=="domain" for b in bots)!=45 or sum(b.get("type")=="platform" for b in bots)!=20:
        raise ValueError("Registry must define exactly 45 domain and 20 platform MasterBots.")
    if any(not b.get(k) for b in bots for k in ("dashboard","command_center","prospectus","training_queue","mission")):
        raise ValueError("Every MasterBot needs dashboard, command center, prospectus, queue and mission references.")
    if data.get("training_policy",{}).get("per_masterbot_dedicated_lane") is not True:
        raise ValueError("Each MasterBot must own a dedicated logical training lane.")
    if data.get("matrix_policy",{}).get("max_parallel") != 5:
        raise ValueError("Matrix parallelism must remain bounded at five.")
    return data

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--github-output", type=Path)
    ap.add_argument("--check",action="store_true")
    args=ap.parse_args()
    data=validate()
    payload=json.dumps([b["name"] for b in data["masterbots"]],separators=(",",":"))
    if args.github_output:
        with args.github_output.open("a",encoding="utf-8") as f: f.write("masterbots="+payload+"\n")
    print(json.dumps({"masterbots":65,"domain_masterbots":45,"platform_masterbots":20,"max_parallel":5}))
if __name__=="__main__": main()
