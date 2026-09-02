#!/usr/bin/env python3
from __future__ import annotations

import argparse,json,subprocess,sys,time
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
CFG=json.loads((ROOT/'config/run-everything-now.json').read_text()); OUT=ROOT/'config/generated/run-everything-now-latest.json'; REPORT=ROOT/'reports/RUN_EVERYTHING_NOW.md'
MAX_STEPS=[
 ('legacy_recovery',[sys.executable,'tools/recover_legacy_bots.py']),('legacy_capability_merge_proposals',[sys.executable,'tools/build_legacy_capability_merge_proposals.py']),('legacy_promotion_backlog',[sys.executable,'tools/build_legacy_promotion_backlog.py']),('unified_bot_system',[sys.executable,'tools/build_unified_bot_system.py']),('runtime_sync_plan',[sys.executable,'tools/build_runtime_sync_plan.py']),('bot_accounting',[sys.executable,'tools/audit_all_bots_categories_and_agents.py']),
 ('universal_capability_benchmark',[sys.executable,'tools/build_universal_capability_benchmark.py']),('universal_app_computer_use_benchmarks',[sys.executable,'tools/build_universal_app_computer_use_benchmarks.py']),('buddy_211_government_service_benchmarks',[sys.executable,'tools/build_buddy_211_government_service_benchmarks.py']),('public_sector_ai_work_roles',[sys.executable,'tools/build_public_sector_ai_work_roles.py']),('business_lifecycle_benchmarks',[sys.executable,'tools/build_business_lifecycle_benchmarks.py']),('creative_mastery_benchmarks',[sys.executable,'tools/build_creative_mastery_benchmarks.py']),('government_public_sector_benchmarks',[sys.executable,'tools/build_government_public_sector_benchmarks.py']),('global_government_benchmarks',[sys.executable,'tools/build_global_government_benchmarks.py']),('government_department_improvement',[sys.executable,'tools/build_government_department_improvement_backlog.py']),('public_fiscal_refresh',[sys.executable,'tools/refresh_public_fiscal_data.py','--allow-offline']),('government_needs_spending_watch',[sys.executable,'tools/build_government_needs_spending_watch.py']),('government_signal_gap_backlog',[sys.executable,'tools/build_government_signal_gap_backlog.py']),('public_money_transparency',[sys.executable,'tools/build_public_money_transparency.py']),('continuous_value_discovery',[sys.executable,'tools/build_continuous_value_discovery_backlog.py']),('work_platform_benchmarks',[sys.executable,'tools/build_work_platform_benchmarks.py']),('manufacturing_productivity_benchmarks',[sys.executable,'tools/build_manufacturing_productivity_benchmarks.py']),('parallel_benchmark_gap_registry',[sys.executable,'tools/build_parallel_benchmark_gap_registry.py']),
 ('universal_task_sandbox',[sys.executable,'tools/build_universal_human_ai_task_sandbox.py']),('full_potential_sandbox',[sys.executable,'tools/build_full_potential_sandbox_catalog.py']),('bot_sandbox_curriculum',[sys.executable,'tools/build_bot_sandbox_curriculum.py']),('business_owner_curriculum',[sys.executable,'tools/build_bot_business_owner_curriculum.py']),('github_parity',[sys.executable,'tools/build_github_platform_benchmark.py']),('engineering_gap_plan',[sys.executable,'tools/build_engineering_gap_closure_plan.py']),('notes_to_code',[sys.executable,'tools/build_notes_to_code_backlog.py']),('resource_matrix',[sys.executable,'tools/build_resource_sandbox_matrix.py']),('connection_truth',[sys.executable,'tools/audit_runtime_connections.py']),('repository_connections',[sys.executable,'tools/audit_repository_connections.py']),('ontology_snapshot',[sys.executable,'tools/build_ontology_snapshot.py']),('trusted_code',[sys.executable,'tools/audit_trusted_code_delivery.py']),('maximum_sandbox',[sys.executable,'tools/build_maximum_sandbox_matrix.py']),
 ('production_verification',['node','--import','tsx','tools/run_universal_verification.ts','--production']),('fleet_e2e',['npm','run','buddy:fleet:e2e']),('maximum_sandbox_runtime',[sys.executable,'tools/audit_maximum_sandbox_runtime.py']),('speed_accuracy',[sys.executable,'tools/run_system_speed_accuracy_benchmarks.py']),('production_smoke',[sys.executable,'tools/smoke_production_runtime.py']),('full_certification',[sys.executable,'tools/build_full_system_certification.py']),('live_user_readiness',[sys.executable,'tools/build_live_user_testing_readiness.py']),('system_progress',[sys.executable,'tools/build_system_progress_status.py'])]
def run(name,command):
    started=time.perf_counter(); p=subprocess.run(command,cwd=ROOT,capture_output=True,text=True); return {'name':name,'command':command,'exit_code':p.returncode,'duration_seconds':round(time.perf_counter()-started,3),'stdout_tail':p.stdout[-4000:],'stderr_tail':p.stderr[-4000:]}

def write_snapshot(mode, step_count, results, in_progress):
    failures=[r for r in results if r['exit_code']!=0]
    payload={
        'schema':'dreamco.run_everything_now_result.v16',
        'generated_at':datetime.now(timezone.utc).isoformat(),
        'mode':mode,
        'step_count':len(results),
        'total_planned_steps':step_count,
        'completed_steps':len(results),
        'pending_steps':max(step_count-len(results),0),
        'in_progress':in_progress,
        'passed':sum(r['exit_code']==0 for r in results),
        'failed':len(failures),
        'results':results,
        'first_failure':failures[0] if failures else None,
        'truth_boundary':CFG['truth_rule'],
    }
    OUT.parent.mkdir(parents=True,exist_ok=True); REPORT.parent.mkdir(parents=True,exist_ok=True); OUT.write_text(json.dumps(payload,indent=2)+'\n')
    lines=['# Run Everything Now','',f"- Mode: **{mode}**",f"- Completed: **{len(results)}/{step_count}**",f"- Passed: **{payload['passed']}/{len(results)}**",f"- Failed: **{len(failures)}**",f"- In progress: **{in_progress}**",'','| Step | Seconds | Result |','| --- | ---: | --- |']
    for r in results: lines.append(f"| {r['name']} | {r['duration_seconds']} | {'PASS' if r['exit_code']==0 else 'FAIL'} |")
    if failures: lines += ['','## First root-cause candidate','',f"`{failures[0]['name']}`",'','```text',(failures[0]['stderr_tail'] or failures[0]['stdout_tail'])[-3000:],'```']
    REPORT.write_text('\n'.join(lines)+'\n')
    return payload
def main()->int:
    ap=argparse.ArgumentParser(); ap.add_argument('--mode',choices=['quick','standard','maximum'],default='maximum'); args=ap.parse_args(); steps=MAX_STEPS
    if args.mode=='quick': steps=MAX_STEPS[:23]+MAX_STEPS[-3:]
    elif args.mode=='standard': steps=MAX_STEPS[:36]+MAX_STEPS[-6:]
    results=[]
    write_snapshot(args.mode, len(steps), results, True)
    for index,(name,command) in enumerate(steps, start=1):
        print(f'\n[run-everything] {name}: {" ".join(command)}',flush=True)
        results.append(run(name,command))
        write_snapshot(args.mode, len(steps), results, index < len(steps))
    failures=[r for r in results if r['exit_code']!=0]; payload=write_snapshot(args.mode, len(steps), results, False)
    print(json.dumps({'ok':not failures,'passed':payload['passed'],'failed':len(failures),'first_failure':failures[0]['name'] if failures else None,'output':str(OUT.relative_to(ROOT))},indent=2)); return 0 if not failures else 1
if __name__=='__main__': raise SystemExit(main())
