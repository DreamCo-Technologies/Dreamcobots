#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
CFG=json.loads((ROOT/'config/run-everything-now.json').read_text())
OUT=ROOT/'config/generated/run-everything-now-latest.json'
REPORT=ROOT/'reports/RUN_EVERYTHING_NOW.md'

MAX_STEPS=[
 ('legacy_recovery',[sys.executable,'tools/recover_legacy_bots.py']),
 ('legacy_capability_merge_proposals',[sys.executable,'tools/build_legacy_capability_merge_proposals.py']),
 ('legacy_promotion_backlog',[sys.executable,'tools/build_legacy_promotion_backlog.py']),
 ('unified_bot_system',[sys.executable,'tools/build_unified_bot_system.py']),
 ('bot_accounting',[sys.executable,'tools/audit_all_bots_categories_and_agents.py']),
 ('work_platform_benchmarks',[sys.executable,'tools/build_work_platform_benchmarks.py']),
 ('manufacturing_productivity_benchmarks',[sys.executable,'tools/build_manufacturing_productivity_benchmarks.py']),
 ('universal_task_sandbox',[sys.executable,'tools/build_universal_human_ai_task_sandbox.py']),
 ('full_potential_sandbox',[sys.executable,'tools/build_full_potential_sandbox_catalog.py']),
 ('bot_sandbox_curriculum',[sys.executable,'tools/build_bot_sandbox_curriculum.py']),
 ('business_owner_curriculum',[sys.executable,'tools/build_bot_business_owner_curriculum.py']),
 ('github_parity',[sys.executable,'tools/build_github_platform_benchmark.py']),
 ('engineering_gap_plan',[sys.executable,'tools/build_engineering_gap_closure_plan.py']),
 ('notes_to_code',[sys.executable,'tools/build_notes_to_code_backlog.py']),
 ('resource_matrix',[sys.executable,'tools/build_resource_sandbox_matrix.py']),
 ('connection_truth',[sys.executable,'tools/audit_runtime_connections.py']),
 ('ontology_snapshot',[sys.executable,'tools/build_ontology_snapshot.py']),
 ('trusted_code',[sys.executable,'tools/audit_trusted_code_delivery.py']),
 ('maximum_sandbox',[sys.executable,'tools/build_maximum_sandbox_matrix.py']),
 ('production_verification',['node','--import','tsx','tools/run_universal_verification.ts','--production']),
 ('fleet_e2e',['npm','run','buddy:fleet:e2e']),
 ('maximum_sandbox_runtime',[sys.executable,'tools/audit_maximum_sandbox_runtime.py']),
 ('speed_accuracy',[sys.executable,'tools/run_system_speed_accuracy_benchmarks.py']),
 ('production_smoke',[sys.executable,'tools/smoke_production_runtime.py']),
 ('full_certification',[sys.executable,'tools/build_full_system_certification.py']),
 ('live_user_readiness',[sys.executable,'tools/build_live_user_testing_readiness.py']),
 ('system_progress',[sys.executable,'tools/build_system_progress_status.py']),
]

def run(name,command):
    started=time.perf_counter()
    proc=subprocess.run(command,cwd=ROOT,capture_output=True,text=True)
    return {'name':name,'command':command,'exit_code':proc.returncode,'duration_seconds':round(time.perf_counter()-started,3),'stdout_tail':proc.stdout[-4000:],'stderr_tail':proc.stderr[-4000:]}

def main()->int:
    ap=argparse.ArgumentParser(); ap.add_argument('--mode',choices=['quick','standard','maximum'],default='maximum'); args=ap.parse_args()
    steps=MAX_STEPS
    if args.mode=='quick': steps=MAX_STEPS[:8]+MAX_STEPS[-3:]
    elif args.mode=='standard': steps=MAX_STEPS[:17]+MAX_STEPS[-6:]
    results=[]
    for name,command in steps:
        print(f'\n[run-everything] {name}: {" ".join(command)}',flush=True)
        results.append(run(name,command))
    failures=[r for r in results if r['exit_code']!=0]
    payload={'schema':'dreamco.run_everything_now_result.v5','generated_at':datetime.now(timezone.utc).isoformat(),'mode':args.mode,'step_count':len(results),'passed':sum(r['exit_code']==0 for r in results),'failed':len(failures),'results':results,'first_failure':failures[0] if failures else None,'truth_boundary':CFG['truth_rule']}
    OUT.parent.mkdir(parents=True,exist_ok=True); REPORT.parent.mkdir(parents=True,exist_ok=True); OUT.write_text(json.dumps(payload,indent=2)+'\n')
    lines=['# Run Everything Now','',f"- Mode: **{args.mode}**",f"- Passed: **{payload['passed']}/{len(results)}**",f"- Failed: **{len(failures)}**",'', '| Step | Seconds | Result |','| --- | ---: | --- |']
    for r in results: lines.append(f"| {r['name']} | {r['duration_seconds']} | {'PASS' if r['exit_code']==0 else 'FAIL'} |")
    if failures:
        lines += ['', '## First root-cause candidate','',f"`{failures[0]['name']}`",'', '```text',(failures[0]['stderr_tail'] or failures[0]['stdout_tail'])[-3000:],'```']
    REPORT.write_text('\n'.join(lines)+'\n')
    print(json.dumps({'ok':not failures,'passed':payload['passed'],'failed':len(failures),'first_failure':failures[0]['name'] if failures else None,'output':str(OUT.relative_to(ROOT))},indent=2))
    return 0 if not failures else 1

if __name__=='__main__': raise SystemExit(main())
