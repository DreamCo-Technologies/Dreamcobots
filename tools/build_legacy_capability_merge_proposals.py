#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
RECOVERY=ROOT/'config/generated/legacy-bot-recovery-manifest.json'
OUT=ROOT/'config/generated/legacy-capability-merge-proposals.json'
REPORT=ROOT/'reports/LEGACY_CAPABILITY_MERGE_PROPOSALS.md'

def norm(value:str)->str: return ' '.join(value.lower().replace('_',' ').replace('-',' ').split())

def canonical_index():
    idx={}
    for path in sorted((ROOT/'App_bots').glob('*.json')):
        payload=json.loads(path.read_text()); division=payload.get('division') or path.stem
        for bot in payload.get('bots',[]):
            slug=bot.get('slug')
            if slug: idx[slug]={'division':division,'capabilities':bot.get('capabilities',[]),'source':str(path.relative_to(ROOT))}
    return idx

def main()->int:
    if not RECOVERY.exists(): raise SystemExit('Run legacy recovery first')
    recovery=json.loads(RECOVERY.read_text()); canonical=canonical_index(); proposals=[]
    for item in recovery.get('items',[]):
        if item.get('state')!='legacy_duplicate': continue
        legacy_caps=item.get('extracted',{}).get('capabilities',[]) or []
        for slug in item.get('canonical_matches',[]):
            owner=canonical.get(slug)
            if not owner: continue
            existing={norm(x) for x in owner['capabilities']}
            additions=[cap for cap in legacy_caps if norm(cap) and norm(cap) not in existing]
            proposals.append({
              'canonical_slug':slug,'canonical_division':owner['division'],'canonical_source':owner['source'],'legacy_source':item['path'],
              'legacy_capability_count':len(legacy_caps),'new_capability_candidates':additions,
              'status':'no_unique_capabilities' if not additions else 'review_and_test_before_merge',
              'required_evidence':['capability meaning distinct','not already provided by shared infrastructure','runtime implementation exists or builder plan created','sandbox tests','fleet regression','Code Trust']
            })
    payload={'schema':'dreamco.legacy_capability_merge_proposals.v1','proposal_count':len(proposals),'proposals':proposals,'truth_boundary':'Duplicate legacy bots are merged by useful capability evidence, not by duplicating canonical identities. Capability candidates are proposals until implementation and tests pass.'}
    OUT.parent.mkdir(parents=True,exist_ok=True); REPORT.parent.mkdir(parents=True,exist_ok=True); OUT.write_text(json.dumps(payload,indent=2)+'\n')
    lines=['# Legacy Capability Merge Proposals','',f'- Duplicate-source proposals: **{len(proposals)}**','']
    for row in proposals[:1000]: lines.append(f"- `{row['legacy_source']}` → `{row['canonical_slug']}` ({len(row['new_capability_candidates'])} candidate additions; {row['status']})")
    REPORT.write_text('\n'.join(lines)+'\n')
    print(json.dumps({'ok':True,'proposals':len(proposals),'with_additions':sum(bool(r['new_capability_candidates']) for r in proposals),'output':str(OUT.relative_to(ROOT))},indent=2)); return 0
if __name__=='__main__': raise SystemExit(main())
