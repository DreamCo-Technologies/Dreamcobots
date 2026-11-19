#!/usr/bin/env python3
"""Build a conservative Markdown requirement-to-evidence traceability report."""
from __future__ import annotations
import argparse, hashlib, json, re, subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
MAP=ROOT/"config/requirement-evidence-map.json"
OUT=ROOT/"artifacts/requirement-traceability"
HEADING=re.compile(r"^#{1,6}\s+(.+?)\s*#*\s*$")
TASK=re.compile(r"^\s*[-*] \[([ xX])\]\s+(.+)$")

def tracked_specs():
    raw=subprocess.run(["git","ls-files","-z"],cwd=ROOT,check=True,capture_output=True).stdout
    return [ROOT/p for p in raw.decode().split("\0") if p and Path(p).suffix.lower() in {".md",".mdx"} and (ROOT/p).is_file()]

def extract():
    rows=[]
    for path in tracked_specs():
        rel=path.relative_to(ROOT).as_posix()
        text=path.read_text(encoding="utf-8",errors="replace")
        current="(document)"
        for number,line in enumerate(text.splitlines(),1):
            h=HEADING.match(line)
            if h:
                current=h.group(1).strip()
                kind="heading"
                label=current
            else:
                task=TASK.match(line)
                if not task: continue
                kind="task"
                label=task.group(2).strip()
            key=hashlib.sha256(f"{rel}::{kind}::{label}".encode()).hexdigest()[:16]
            rows.append({"requirement_id":"REQ-"+key,"source_path":rel,"line":number,"section":current,"kind":kind,"requirement":label})
    return rows

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--out-dir",type=Path,default=OUT)
    args=ap.parse_args()
    mapping=json.loads(MAP.read_text(encoding="utf-8")) if MAP.exists() else {"requirements":[]}
    mapped={x["requirement_id"]:x for x in mapping.get("requirements",[])}
    rows=[]
    for req in extract():
        m=mapped.get(req["requirement_id"],{})
        impl=m.get("implementation_paths",[])
        tests=m.get("test_paths",[])
        routes=m.get("runtime_route_paths",[])
        bench=m.get("benchmark_evidence_paths",[])
        exists=lambda xs:[p for p in xs if (ROOT/p).is_file()]
        missing=lambda xs:[p for p in xs if not (ROOT/p).is_file()]
        ie,te,rex,bex=exists(impl),exists(tests),exists(routes),exists(bench)
        if not m: status="documented_unmapped"
        elif missing(impl) or missing(tests) or missing(routes) or missing(bench): status="evidence_path_missing"
        elif not (ie and te and rex and bex): status="evidence_incomplete"
        else: status="evidence_artifacts_present_requires_review"
        rows.append({**req,"status":status,"implementation_paths":impl,"implementation_paths_present":ie,"missing_implementation_paths":missing(impl),"test_paths":tests,"test_paths_present":te,"missing_test_paths":missing(tests),"runtime_route_paths":routes,"runtime_route_paths_present":rex,"missing_runtime_route_paths":missing(routes),"benchmark_evidence_paths":bench,"benchmark_evidence_paths_present":bex,"missing_benchmark_evidence_paths":missing(bench),"verification_note":"Path existence is not a passing test, live route execution or verified benchmark. Human/CI evidence review is still required."})
    counts={}
    for row in rows: counts[row["status"]]=counts.get(row["status"],0)+1
    report={"schema":"dreamco.requirement_traceability.v1","source_specifications":len(tracked_specs()),"requirement_units":len(rows),"mapped_units":sum(r["status"]!="documented_unmapped" for r in rows),"status_counts":counts,"requirements":rows,"policy":"No semantic implementation, test pass, runtime success or benchmark result is inferred from filenames or prose."}
    args.out_dir.mkdir(parents=True,exist_ok=True)
    (args.out_dir/"requirement-traceability.json").write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
    lines=["# Markdown Requirement Traceability","",f"- Source specifications: {report['source_specifications']}",f"- Requirement units: {report['requirement_units']}",f"- Explicitly mapped: {report['mapped_units']}","", "## Evidence states",""]
    lines.extend(f"- {k}: {v}" for k,v in sorted(counts.items()))
    lines += ["","## Unmapped and incomplete requirements",""]
    lines.extend(f"- `{r['requirement_id']}` — `{r['source_path']}:{r['line']}` — {r['requirement']} — **{r['status']}**" for r in rows if r["status"]!="evidence_artifacts_present_requires_review")
    lines += ["","A path existing is not proof of a passing test, live runtime route or benchmark. Evidence must be independently reviewed."]
    (args.out_dir/"requirement-traceability.md").write_text("\n".join(lines)+"\n",encoding="utf-8")
    print(json.dumps({"specifications":report["source_specifications"],"requirements":len(rows),"mapped":report["mapped_units"],"status_counts":counts},indent=2))
if __name__=="__main__": main()
