#!/usr/bin/env python3
"""Generate public Buddy Bootcamp data from the canonical curriculum config."""
from __future__ import annotations
import argparse,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"config/buddy-bootcamp-65.json"
OUTPUT=ROOT/"website/data/buddy-bootcamp.json"

def build():
    source=json.loads(SOURCE.read_text(encoding="utf-8"))
    if len(source.get("levels",[]))!=8:
        raise ValueError("Buddy Bootcamp must define exactly eight levels.")
    if [x.get("id") for x in source["levels"]]!=list(range(1,9)):
        raise ValueError("Bootcamp levels must be ordered 1 through 8.")
    return {"schema":"dreamco.buddy_bootcamp_public.v1","name":source["name"],"levels":source["levels"],"sandbox_modes":source["sandbox_modes"],"mastery_policy":source["mastery_policy"],"user_privacy":source.get("user_privacy",{}),"daily_loop":source.get("daily_loop",[])}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--check",action="store_true")
    args=ap.parse_args()
    content=json.dumps(build(),indent=2)+"\n"
    if args.check:
        if not OUTPUT.exists() or OUTPUT.read_text(encoding="utf-8")!=content:
            raise SystemExit("Public Bootcamp data is stale; regenerate it.")
    else:
        OUTPUT.parent.mkdir(parents=True,exist_ok=True)
        OUTPUT.write_text(content,encoding="utf-8")
    print(json.dumps({"levels":8,"sandbox_modes":len(build()["sandbox_modes"])}))
if __name__=="__main__": main()
