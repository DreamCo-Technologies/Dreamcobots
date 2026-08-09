#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SUP=json.loads((ROOT/'config/buddy-runtime-supervisor.json').read_text())
UNIFIED=ROOT/'config/generated/unified-bot-system.json'
WORK=ROOT/'config/generated/universal-work-ai-catalog.json'
OUT=ROOT/'config/generated/runtime-sync-plan.json'

def load(path,default): return json.loads(path.read_text()) if path.exists() else default

def lane(worker_id:str,max_lanes:int)->int:
    return int(hashlib.sha256(worker_id.encode()).hexdigest()[:8],16)%max_lanes

def main()->int:
    unified=load(UNIFIED,{'canonical_bots':[],'legacy_candidates':[]})
    work=load(WORK,{'occupations':[],'tasks':[]})
    max_lanes=int(SUP['coordination']['maximum_parallel_lanes'])
    workers=[]
    for bot in unified.get('canonical_bots',[]):
        wid=bot['slug']; workers.append({'worker_id':wid,'worker_type':'canonical_bot','owner_division':bot['division'],'lane':lane(wid,max_lanes),'runtime_state':'eligible_for_supervised_runtime','live_boundary':'approval_gated_for_consequential_actions'})
    for row in unified.get('legacy_candidates',[]):
        wid=row.get('slug') or row['source']; workers.append({'worker_id':wid,'worker_type':'legacy_candidate','owner_division':'pending_owner_review','lane':lane(wid,max_lanes),'runtime_state':'sandbox_only','live_boundary':'not_live_until_promotion'})
    for occ in work.get('occupations',[]):
        wid=occ['worker_slug']; workers.append({'worker_id':wid,'worker_type':'occupation_specialist','owner_division':'DreamAgents','lane':lane(wid,max_lanes),'runtime_state':'sandbox_only','live_boundary':'not_live_until_task_evidence'})
    for task in work.get('tasks',[]):
        wid=task['worker_slug']; workers.append({'worker_id':wid,'worker_type':'task_specialist','owner_division':'DreamAgents','lane':lane(wid,max_lanes),'runtime_state':'sandbox_only','live_boundary':'not_live_until_task_evidence'})
    lane_counts={str(i):0 for i in range(max_lanes)}
    for w in workers: lane_counts[str(w['lane'])]+=1
    payload={'schema':'dreamco.runtime_sync_plan.v1','worker_count':len(workers),'parallel_lane_count':max_lanes,'lane_counts':lane_counts,'heartbeat_seconds':SUP['coordination']['heartbeat_seconds'],'lease_seconds':SUP['coordination']['lease_seconds'],'checkpoint_after_step':SUP['coordination']['checkpoint_after_step'],'idempotency_key_required':SUP['coordination']['idempotency_key_required'],'workers':workers,'truth_boundary':SUP['truth_rule']}
    OUT.parent.mkdir(parents=True,exist_ok=True); OUT.write_text(json.dumps(payload,indent=2)+'\n')
    print(json.dumps({'ok':True,'workers':len(workers),'lanes':max_lanes,'output':str(OUT.relative_to(ROOT))},indent=2)); return 0
if __name__=='__main__': raise SystemExit(main())
