#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
APP=ROOT/'App_bots'
RECOVERY=ROOT/'config/generated/legacy-bot-recovery-manifest.json'
OUT=ROOT/'config/generated/unified-bot-system.json'


def ensure_recovery():
    if not RECOVERY.exists(): subprocess.run([sys.executable,'tools/recover_legacy_bots.py'],cwd=ROOT,check=True)


def main()->int:
    ensure_recovery(); recovery=json.loads(RECOVERY.read_text())
    canonical=[]
    for path in sorted(APP.glob('*.json')):
        payload=json.loads(path.read_text())
        division=payload.get('division') or path.stem
        for bot in payload.get('bots',[]):
            canonical.append({
                'slug':bot.get('slug'),'display_name':bot.get('displayName'),'division':division,'category':bot.get('category'),
                'capabilities':bot.get('capabilities',[]),'status':'canonical_active','source':str(path.relative_to(ROOT)),
                'sandbox_required':True,'business_curriculum_required':True,'runtime_route_required':True
            })
    candidates=[]
    for row in recovery.get('items',[]):
        if row.get('state')=='recoverable_new_bot':
            for slug in row.get('candidate_slugs',[]) or [None]:
                candidates.append({
                    'slug':slug,'source':row.get('path'),'status':'legacy_pending_promotion','promotion_gate':recovery['promotion_gate'],
                    'candidate_names':row.get('candidate_names',[]),'extracted':row.get('extracted',{}),
                    'sandbox_required':True,'runtime_route_required':True,'canonical_counted':False
                })
    payload={
      'schema':'dreamco.unified_bot_system.v1','canonical_bot_count':len(canonical),'legacy_pending_candidate_count':len(candidates),
      'total_accounted_worker_records':len(canonical)+len(candidates),'canonical_bots':canonical,'legacy_candidates':candidates,
      'legacy_state_counts':recovery.get('state_counts',{}),
      'truth_boundary':'Canonical bot count only includes App_bots. Legacy candidates are fully accounted for but cannot become live fleet members until the promotion gate passes.'
    }
    OUT.parent.mkdir(parents=True,exist_ok=True); OUT.write_text(json.dumps(payload,indent=2)+'\n')
    print(json.dumps({'ok':True,'canonical':len(canonical),'legacy_candidates':len(candidates),'output':str(OUT.relative_to(ROOT))},indent=2))
    return 0

if __name__=='__main__': raise SystemExit(main())
