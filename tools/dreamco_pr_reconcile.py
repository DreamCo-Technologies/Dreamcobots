#!/usr/bin/env python3
"""Read-only PR divergence and three-way conflict reconnaissance.

Fetches open PR heads and their declared base branches, then uses Git's merge
base and merge-tree machinery without changing the checkout or any remote ref.
"""
from __future__ import annotations
import json, subprocess, sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
INVENTORY=ROOT/"artifacts"/"dreamco-reconciliation"/"pull-request-inventory.json"
OUT=ROOT/"artifacts"/"dreamco-reconciliation"/"pull-request-reconciliation.json"

def git(*args: str, check: bool=True) -> subprocess.CompletedProcess:
    return subprocess.run(["git",*args],cwd=ROOT,text=True,capture_output=True,check=check)

def ref_for_branch(branch: str) -> str:
    safe="".join(c if c.isalnum() or c in "-_." else "-" for c in branch)
    return "refs/remotes/dreamco/base/"+safe

def inspect_pr(pr: dict) -> dict:
    number=int(pr["number"]); base=pr["base"]; head_ref=f"refs/remotes/dreamco/pr/{number}"
    result={"number":number,"url":pr.get("html_url"),"base":base,"head":pr.get("head"),
            "status":"blocked","overlapping_paths":[],"conflicting_paths":[]}
    try:
        git("fetch","--no-tags","origin",f"+refs/heads/{base}:{ref_for_branch(base)}")
        git("fetch","--no-tags","origin",f"+refs/pull/{number}/head:{head_ref}")
        b=ref_for_branch(base)
        merge_base=git("merge-base",b,head_ref).stdout.strip()
        result["merge_base"]=merge_base
        result["ahead_by"]=len(git("rev-list","--count",f"{b}..{head_ref}").stdout.strip())
        result["behind_by"]=len(git("rev-list","--count",f"{head_ref}..{b}").stdout.strip())
        base_paths=set(git("diff","--name-only",f"{merge_base}..{b}").stdout.splitlines())
        head_paths=set(git("diff","--name-only",f"{merge_base}..{head_ref}").stdout.splitlines())
        result["overlapping_paths"]=sorted(base_paths & head_paths)
        mt=git("merge-tree","--write-tree",b,head_ref,check=False)
        if mt.returncode==0:
            result["status"]="clean_merge_tree"
        else:
            result["status"]="conflicts_or_merge_tree_error"
            result["merge_tree_exit_code"]=mt.returncode
            # Git merge-tree conflict records contain path lines after the tree header.
            result["conflicting_paths"]=sorted({line.split("\t")[-1] for line in mt.stdout.splitlines()
                                                  if "\t" in line and not line.startswith("changed in")})
            result["diagnostic"]=mt.stderr[-3000:]
    except Exception as exc:
        result["status"]="blocked"
        result["diagnostic"]=str(exc)[:3000]
    return result

def main() -> int:
    if not INVENTORY.exists():
        print("Missing PR inventory; run dreamco_global_reconciliation.py first",file=sys.stderr); return 2
    prs=json.loads(INVENTORY.read_text(encoding="utf-8")).get("pull_requests",[])
    open_prs=[p for p in prs if p.get("state")=="open"]
    reports=[inspect_pr(p) for p in open_prs]
    OUT.write_text(json.dumps({"open_pr_count":len(open_prs),"reports":reports},indent=2)+"\n",encoding="utf-8")
    counts={}
    for r in reports: counts[r["status"]]=counts.get(r["status"],0)+1
    print(json.dumps({"open_pr_count":len(open_prs),"status_counts":counts,"report":str(OUT.relative_to(ROOT))},indent=2))
    # Conflicts are findings, not tool failures. Blocked fetches fail the job so they are visible.
    return 1 if any(r["status"]=="blocked" for r in reports) else 0
if __name__=="__main__": sys.exit(main())
