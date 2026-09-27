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


def build_unified_system(root: Path, recovery: dict) -> dict:
    canonical=[]; supplemental=[]
    for path in sorted((root/'App_bots').glob('*.json')):
        payload=json.loads(path.read_text())
        division=payload.get('division') or path.stem
        growth=payload.get('growth') is True
        cohort=supplemental if growth else canonical
        for bot in payload.get('bots',[]):
            cohort.append({
                'slug':bot.get('slug'),'display_name':bot.get('displayName'),'division':division,'category':bot.get('category'),
                'capabilities':bot.get('capabilities',[]),'status':'supplemental_sandbox_only' if growth else 'canonical_active','source':str(path.relative_to(root)),
                'cohort':'supplemental' if growth else 'canonical',
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
    return {
      'schema':'dreamco.unified_bot_system.v2','canonical_bot_count':len(canonical),'supplemental_bot_count':len(supplemental),
      'total_profile_count':len(canonical)+len(supplemental),'legacy_pending_candidate_count':len(candidates),
      'total_accounted_worker_records':len(canonical)+len(supplemental)+len(candidates),
      'canonical_bots':canonical,'supplemental_bots':supplemental,'legacy_candidates':candidates,
      'legacy_state_counts':recovery.get('state_counts',{}),
      'truth_boundary':'Canonical profiles are App_bots divisions without growth:true; supplemental growth profiles are counted separately and remain sandbox-only. Profiles and declared capabilities are not proof of live operation. Legacy candidates cannot become live fleet members until the promotion gate passes.'
    }


def main()->int:
    ensure_recovery()
    payload=build_unified_system(ROOT,json.loads(RECOVERY.read_text()))
    OUT.parent.mkdir(parents=True,exist_ok=True); OUT.write_text(json.dumps(payload,indent=2)+'\n')
    print(json.dumps({'ok':True,'canonical':payload['canonical_bot_count'],'supplemental':payload['supplemental_bot_count'],'legacy_candidates':payload['legacy_pending_candidate_count'],'output':str(OUT.relative_to(ROOT))},indent=2))
    return 0

if __name__=='__main__': raise SystemExit(main())
