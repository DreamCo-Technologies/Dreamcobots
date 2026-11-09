#!/usr/bin/env python3
"""Generate a public-safe, read-only DreamCo GitHub portfolio snapshot."""
from __future__ import annotations
import argparse, json, os, sys, urllib.error, urllib.parse, urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SCHEMA = "dreamco.github_control_tower.v1"
PUBLIC_REPOSITORIES = (
    "DreamCo-Technologies/Dreamcobots",
    "ireanjordan24/Dreamcobots-frontier-trust",
    "ireanjordan24/Dreamcobots-Grok-Revolutionary",
)
API = "https://api.github.com"

class GitHubApiError(RuntimeError): pass

def api_get(path: str, token: str | None) -> Any:
    headers = {"Accept":"application/vnd.github+json","User-Agent":"DreamCo-Control-Tower","X-GitHub-Api-Version":"2022-11-28"}
    if token: headers["Authorization"] = "Bearer " + token
    req = urllib.request.Request(API + path, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=25) as response:
            return json.loads(response.read().decode("utf-8"))
    except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError) as exc:
        raise GitHubApiError(f"GET {path}: {exc}") from exc

def summarize_checks(check_runs: list[dict[str, Any]]) -> dict[str, Any]:
    counts: dict[str,int] = {}; failures=[]; pending=[]
    for c in check_runs:
        status=str(c.get("status") or "unknown"); conclusion=c.get("conclusion")
        bucket=str(conclusion) if status=="completed" and conclusion else status
        counts[bucket]=counts.get(bucket,0)+1
        item={"name":str(c.get("name") or "unnamed"),"status":status}
        if conclusion: item["conclusion"]=str(conclusion)
        if status!="completed": pending.append(item)
        elif conclusion not in ("success","neutral","skipped"): failures.append(item)
    readiness=("checks_failing" if failures else "checks_pending" if pending else
               "no_check_runs" if not check_runs else "checks_passed_review_still_required")
    return {"total":len(check_runs),"counts":dict(sorted(counts.items())),
            "failures":failures,"pending":pending,"readiness":readiness}

def summarize_status(payload: dict[str,Any]) -> dict[str,Any]:
    contexts=[{"context":str(x.get("context") or "unnamed"),"state":str(x.get("state") or "unknown"),
               "target_url":x.get("target_url")} for x in payload.get("statuses",[])]
    return {"state":str(payload.get("state") or "unknown"),"total":len(contexts),"contexts":contexts}

def api_repo_path(repo: str) -> str: return urllib.parse.quote(repo,safe="/")

def build_repository(repo: str, token: str | None) -> dict[str,Any]:
    path=api_repo_path(repo); result={"full_name":repo,"visibility_scope":"public"}
    try:
        meta=api_get(f"/repos/{path}",token)
        result.update({k:meta.get(k) for k in ("html_url","default_branch","description","updated_at","pushed_at","open_issues_count","stargazers_count")})
        result["archived"]=bool(meta.get("archived")); result["fork"]=bool(meta.get("fork"))
    except GitHubApiError as exc:
        result["repository_error"]=str(exc); result["pull_requests"]=[]; result["workflow_runs"]=[]; return result
    try:
        pulls=api_get(f"/repos/{path}/pulls?state=open&per_page=100&sort=updated&direction=desc",token)
        if not isinstance(pulls,list): raise GitHubApiError("PR response was not a list")
        result["open_pull_requests_total"]=len(pulls); result["pull_requests_truncated"]=len(pulls)==100
        rows=[]
        for pr in pulls:
            number=int(pr["number"]); sha=str((pr.get("head") or {}).get("sha") or "")
            row={"number":number,"title":pr.get("title"),"html_url":pr.get("html_url"),"draft":bool(pr.get("draft")),
                 "updated_at":pr.get("updated_at"),"base_branch":(pr.get("base") or {}).get("ref"),
                 "head_branch":(pr.get("head") or {}).get("ref"),"head_sha":sha,
                 "author":(pr.get("user") or {}).get("login"),"labels":[str(x.get("name")) for x in pr.get("labels",[])]}
            try:
                detail=api_get(f"/repos/{path}/pulls/{number}",token)
                row.update({"mergeable":detail.get("mergeable"),"mergeable_state":detail.get("mergeable_state"),
                            "changed_files":detail.get("changed_files"),"commits":detail.get("commits"),
                            "requested_reviewers":[str(x.get("login")) for x in detail.get("requested_reviewers",[])]})
            except GitHubApiError as exc: row["detail_error"]=str(exc)
            if sha:
                try: row["checks"]=summarize_checks(api_get(f"/repos/{path}/commits/{sha}/check-runs?per_page=100",token).get("check_runs",[]))
                except GitHubApiError as exc: row["checks_error"]=str(exc); row["checks"]=summarize_checks([])
                try: row["commit_status"]=summarize_status(api_get(f"/repos/{path}/commits/{sha}/status",token))
                except GitHubApiError as exc: row["commit_status_error"]=str(exc)
            else: row["checks"]=summarize_checks([])
            rows.append(row)
        result["pull_requests"]=rows
    except GitHubApiError as exc: result["pull_requests_error"]=str(exc); result["pull_requests"]=[]
    try:
        runs=api_get(f"/repos/{path}/actions/runs?per_page=20",token)
        result["workflow_runs"]=[{k:x.get(k) for k in ("id","name","display_title","event","status","conclusion","created_at","updated_at","html_url","head_branch","head_sha")} for x in runs.get("workflow_runs",[])]
    except GitHubApiError as exc: result["workflow_runs_error"]=str(exc); result["workflow_runs"]=[]
    return result

def build_report(token: str | None) -> dict[str,Any]:
    repos=[build_repository(r,token) for r in PUBLIC_REPOSITORIES]
    prs=[p for r in repos for p in r.get("pull_requests",[])]
    readiness={}
    for p in prs:
        k=(p.get("checks") or {}).get("readiness","unknown"); readiness[k]=readiness.get(k,0)+1
    return {"schema":SCHEMA,"generated_at":datetime.now(timezone.utc).isoformat(),"source":"GitHub REST API",
      "scope":{"repositories":list(PUBLIC_REPOSITORIES),"repository_count":len(repos),"open_pull_requests":len(prs),
       "pull_request_limit_per_repository":100,"private_repositories":"excluded from public Pages",
       "logs_and_artifacts":"not copied; links only",
       "safety_note":"Passing checks are not merge approval. Required reviews, branch protection, conflicts and owner approval remain authoritative."},
      "summary":{"repositories_with_errors":sum(bool(r.get("repository_error")) for r in repos),
       "open_pull_requests":len(prs),"checks_failing":readiness.get("checks_failing",0),
       "checks_pending":readiness.get("checks_pending",0),
       "checks_passed_review_still_required":readiness.get("checks_passed_review_still_required",0),
       "no_check_runs":readiness.get("no_check_runs",0)},
      "readiness_counts":readiness,"repositories":repos}

def main() -> int:
    parser=argparse.ArgumentParser(); parser.add_argument("--output",default="website/data/control-tower/github-status.json")
    parser.add_argument("--check",action="store_true"); args=parser.parse_args(); out=Path(args.output)
    if args.check:
        try:
            data=json.loads(out.read_text(encoding="utf-8"))
            assert data.get("schema")==SCHEMA and isinstance(data.get("repositories"),list) and isinstance(data.get("summary"),dict)
            for r in data["repositories"]:
                for p in r.get("pull_requests",[]):
                    assert p.get("checks",{}).get("readiness") in {"checks_failing","checks_pending","checks_passed_review_still_required","no_check_runs"}
        except (OSError,ValueError,AssertionError,AttributeError) as exc:
            print(f"Control Tower report invalid: {exc}",file=sys.stderr); return 1
        print(f"Control Tower report valid: {out}"); return 0
    report=build_report(os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN"))
    out.parent.mkdir(parents=True,exist_ok=True); out.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(report["summary"],sort_keys=True)); print(f"Wrote {out}"); return 0

if __name__=="__main__": raise SystemExit(main())
