#!/usr/bin/env python3
"""Evidence-first DreamCo production readiness gate.

This tool deliberately refuses to infer runtime capability from documentation alone.
It inventories evidence-bearing repository assets and emits a machine-readable report.
It never marks a capability verified merely because a design document exists.
"""
from __future__ import annotations
import json, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "config/production-readiness-contract.json"
OUT = ROOT / "data/production-readiness-report.json"

def exists_any(patterns: list[str]) -> list[str]:
    found=[]
    for p in patterns:
        if any(ROOT.glob(p)):
            found.append(p)
    return found

def git_sha() -> str:
    try:
        return subprocess.check_output(["git","rev-parse","HEAD"], cwd=ROOT, text=True).strip()
    except Exception:
        return "unknown"

def main() -> int:
    contract=json.loads(CONTRACT.read_text())
    reports=[]
    common={
        "buddy_orchestration":["buddy_os/**","tools/*buddy*","tests/*buddy*"],
        "benchmark_framework":["docs/*BENCHMARK*","tools/*benchmark*","tests/*benchmark*"],
        "capability_genome":["*capability*","config/*capability*","tests/*capability*"],
        "model_research":["docs/*MODEL*","tools/*model*","config/*model*"],
        "teacher_model":["*teacher*","docs/*DISTILL*","tools/*distill*"],
        "experiment_engine":["*experiment*","tools/*experiment*","tests/*experiment*"],
        "ablation":["*ablation*","tools/*ablation*","tests/*ablation*"],
        "distillation":["*distill*","tools/*distill*","tests/*distill*"],
        "free_first":["*resource*","*budget*","tools/*resource*","tests/*resource*"],
        "resource_optimization":["*vram*","*ram*","*resource*","tools/*resource*"],
        "regression":["tests/**",".github/workflows/**"],
        "security":["SECURITY.md",".github/workflows/**","*license*","*security*"],
        "actions":["client/**","tests/actions*",".github/workflows/actions*"],
        "daily_scan":[".github/workflows/*daily*",".github/workflows/*scan*","tools/*scan*"],
        "source_ingestion":["*source*","*ingest*","tools/*source*","tools/*ingest*"],
        "superbot":["*superbot*","*module*","tools/*fleet*","tests/*fleet*"],
        "deployment":["app.yaml","cloudbuild.yaml","Dockerfile*","firebase.json","vercel.json",".github/workflows/*deploy*"],
        "observability":["*observability*","*telemetry*","*tracing*","tools/*observ*"],
        "cost_accounting":["*cost*","*billing*","*usage*","tools/*cost*","tools/*usage*"]
    }
    for area in contract["areas"]:
        found=exists_any(common.get(area["id"],[]))
        status="partial" if found else "unknown"
        reports.append({"id":area["id"],"label":area["label"],"status":status,"repository_evidence":found,"required_evidence":area["required"]})
    critical=[r for r in reports if r["status"]=="unknown" and r["id"] in {"buddy_orchestration","benchmark_framework","security","deployment","observability"}]
    report={"schema_version":1,"generated_at":datetime.now(timezone.utc).isoformat(),"commit":git_sha(),"policy":"evidence-first","release_status":"blocked" if critical else "not_certified","areas":reports,"blocking_unknowns":[r["id"] for r in critical],"note":"Partial/unknown is intentional until executable evidence is attached. This report is not a claim of production certification."}
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps(report,indent=2))
    return 1 if critical else 0

if __name__ == "__main__":
    raise SystemExit(main())
