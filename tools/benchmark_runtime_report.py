#!/usr/bin/env python3
from __future__ import annotations
import json,sys
from pathlib import Path

def main():
    src=Path(sys.argv[1] if len(sys.argv)>1 else 'benchmark-runtime.json')
    rows=json.loads(src.read_text()).get('runs',[]) if src.exists() else []
    total=sum(float(r.get('duration_seconds',0) or 0) for r in rows)
    useful=sum(float(r.get('useful_compute_seconds',0) or 0) for r in rows)
    completed=sum(1 for r in rows if r.get('status')=='completed')
    failed=sum(1 for r in rows if r.get('status')=='failed')
    report={'schema':'dreamco.benchmark_runtime_report.v1','runs':len(rows),'completed':completed,'failed':failed,'wall_seconds':total,'useful_compute_seconds':useful,'utilization_ratio':(useful/total if total else None),'policy':'optimize useful benchmark work; do not bypass limits'}
    print(json.dumps(report,indent=2))
if __name__=='__main__': main()
