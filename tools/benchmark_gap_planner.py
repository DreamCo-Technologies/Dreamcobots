#!/usr/bin/env python3
"""Create a deterministic next-work queue for all 65 MasterBots.

Input may be a JSON scorecard with entries containing division, benchmark,
score, target, status, and evidence_count. Missing measurements are queued for
measurement rather than treated as failures or successes.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--scores",default="benchmark-scores.json"); ap.add_argument("--out",default="benchmark-gap-queue.json"); a=ap.parse_args()
    p=Path(a.scores); data=json.loads(p.read_text()) if p.exists() else {"results":[]}
    registry=json.loads((Path(__file__).resolve().parents[1]/"config/masterbot-65-registry.json").read_text())
    names={r["name"]:r["id"] for r in registry["divisions"]}
    valid_ids=set(names.values())
    results=data.get("results", data.get("divisionResults", [])); by={}; rejected=[]
    for r in results:
        value=r.get("division_id", r.get("division"))
        d=names.get(value) if isinstance(value,str) else value
        if isinstance(d,str) and d.isdigit(): d=int(d)
        if type(d) is not int or d not in valid_ids:
            rejected.append({"division":value,"reason":"unknown division identity"}); continue
        by.setdefault(d,[]).append(r)
    queue=[]
    for d in range(1,66):
        rs=by.get(d,[])
        if not rs: queue.append({"division":d,"priority":0,"action":"RUN_BENCHMARKS","reason":"no measured evidence"}); continue
        for r in rs:
            score=r.get("score"); target=r.get("target")
            if score is None or target is None: priority=0; action="RUN_BENCHMARKS"; reason="incomplete measurement"
            elif float(score)<float(target):
                gap=float(target)-float(score); priority=1 if r.get("status")=="failed" else 2; action="CLOSE_GAPS"; reason=f"gap={gap:g}"
            else: priority=3; action="RETEST_FAILURES" if r.get("status")=="regression" else "RUN_SANDBOX"; reason="at/above target; verify repeatability"
            queue.append({"division":d,"benchmark":r.get("benchmark"),"priority":priority,"action":action,"reason":reason})
    queue.sort(key=lambda x:(x["priority"],x["division"],x.get("benchmark") or ""))
    out={"rejected":rejected,"complete":not rejected,"schema":"dreamco.benchmark_gap_queue.v1","divisions":65,"queue":queue,"measurement_policy":"unknown is not failure","mastery_policy":"repeatable evidence required"}
    Path(a.out).write_text(json.dumps(out,indent=2)+"\n")
    print(json.dumps({"divisions":65,"queue_items":len(queue),"unmeasured_divisions":sum(not by.get(d) for d in range(1,66))},indent=2))
    return 2 if rejected else 0
if __name__=="__main__": raise SystemExit(main())
