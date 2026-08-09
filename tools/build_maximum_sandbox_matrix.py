#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
UNIFIED=ROOT/'config/generated/unified-bot-system.json'
WORK=ROOT/'config/generated/universal-work-ai-catalog.json'
TASKS=ROOT/'config/generated/universal-human-ai-task-sandbox.json'
OUT=ROOT/'config/generated/maximum-sandbox-matrix.json'

OVERLAYS=['happy_path','negative','boundary','malformed_input','permission','privacy','security','recovery','idempotency','concurrency_when_applicable','speed','accuracy','cost','observability','rollback_when_applicable']


def ensure(path:Path,cmd:list[str]):
    if not path.exists(): subprocess.run(cmd,cwd=ROOT,check=True)


def main()->int:
    ensure(UNIFIED,[sys.executable,'tools/build_unified_bot_system.py'])
    ensure(TASKS,[sys.executable,'tools/build_universal_human_ai_task_sandbox.py'])
    unified=json.loads(UNIFIED.read_text())
    tasks=json.loads(TASKS.read_text())
    work=json.loads(WORK.read_text()) if WORK.exists() else {'occupations':[],'tasks':[],'source':{'status':'not_loaded'}}
    workers=[]
    for bot in unified.get('canonical_bots',[]): workers.append({'worker_id':bot['slug'],'worker_type':'canonical_bot','source':bot['source'],'status':bot['status']})
    for bot in unified.get('legacy_candidates',[]): workers.append({'worker_id':bot.get('slug') or bot['source'],'worker_type':'legacy_candidate','source':bot['source'],'status':bot['status']})
    for occ in work.get('occupations',[]): workers.append({'worker_id':occ['worker_slug'],'worker_type':'occupation_specialist','source':'O*NET','status':'sandbox_only'})
    for task in work.get('tasks',[]): workers.append({'worker_id':task['worker_slug'],'worker_type':'task_specialist','source':'O*NET','status':'sandbox_only'})
    payload={
      'schema':'dreamco.maximum_sandbox_matrix.v1',
      'worker_count':len(workers),
      'canonical_workers':sum(w['worker_type']=='canonical_bot' for w in workers),
      'legacy_candidate_workers':sum(w['worker_type']=='legacy_candidate' for w in workers),
      'occupation_workers':sum(w['worker_type']=='occupation_specialist' for w in workers),
      'task_workers':sum(w['worker_type']=='task_specialist' for w in workers),
      'universal_task_base_count':tasks.get('base_category_count',tasks.get('category_count',0)),
      'test_overlays':OVERLAYS,
      'minimum_test_dimensions_per_applicable_case':len(OVERLAYS),
      'workers':workers,
      'application_rule':'Each worker maps only to applicable task/domain/tool/API/resource/job cases, but every applicable case receives all relevant overlays. Shared infrastructure tests are inherited with dependency evidence rather than duplicated pointlessly.',
      'live_user_gate':'No worker graduates to live-user autonomous operation until applicable runtime tests, security/privacy/permission checks, recovery, speed and accuracy thresholds pass.',
      'truth_boundary':'This matrix defines maximum required coverage. Planned mappings are not counted as passed until executable test evidence exists.'
    }
    OUT.parent.mkdir(parents=True,exist_ok=True); OUT.write_text(json.dumps(payload,indent=2)+'\n')
    print(json.dumps({'ok':True,'workers':len(workers),'overlays':len(OVERLAYS),'work_source_status':work.get('source',{}).get('status'),'output':str(OUT.relative_to(ROOT))},indent=2))
    return 0

if __name__=='__main__': raise SystemExit(main())
