#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
RECOVERY=ROOT/'config/generated/legacy-bot-recovery-manifest.json'
OUT=ROOT/'config/generated/legacy-bot-promotion-backlog.json'
REPORT=ROOT/'reports/LEGACY_BOT_PROMOTION_BACKLOG.md'

DIVISION_HINTS={
 'code':'DreamCodeLab','dev':'DreamCodeLab','debug':'DreamCodeLab','sales':'DreamSalesPro','lead':'DreamSalesPro','finance':'DreamFinance','payment':'DreamPayments','loan':'DreamLoans','real-estate':'DreamRealEstate','property':'DreamRealEstate','legal':'DreamLegal','health':'DreamHealth','education':'DreamEducation','construction':'DreamConstruction','transport':'DreamTransport','food':'DreamFood','science':'DreamScience','art':'DreamArts','security':'DreamCyber','cyber':'DreamCyber','agriculture':'DreamAgriculture','maintenance':'DreamMaintenance','production':'DreamProduction','social':'DreamSocial','admin':'DreamAdmin','crypto':'DreamCrypto','manufactur':'DreamTrade','trade':'DreamTrade','market':'DreamMarket','content':'DreamContent','automation':'DreamAutomation','data':'DreamData','agent':'DreamAgents'
}

def infer_owner(slug:str)->tuple[str,list[str]]:
    lower=slug.lower(); hits=[(k,v) for k,v in DIVISION_HINTS.items() if k in lower]
    if not hits: return 'CommandCore',[]
    owners=[]
    for _k,v in hits:
        if v not in owners: owners.append(v)
    return owners[0],owners[1:]

def main()->int:
    if not RECOVERY.exists():
        raise SystemExit('Run tools/recover_legacy_bots.py first')
    recovery=json.loads(RECOVERY.read_text())
    rows=[]
    seen=set()
    for item in recovery.get('items',[]):
        if item.get('state')!='recoverable_new_bot': continue
        for slug in item.get('candidate_slugs',[]) or []:
            key=(slug,item['path'])
            if key in seen: continue
            seen.add(key)
            owner,collabs=infer_owner(slug)
            rows.append({
              'candidate_slug':slug,'source_path':item['path'],'primary_owner':owner,'collaborator_divisions':collabs,
              'status':'needs_owner_review','canonical_counted':False,
              'required_gates':['identity_unique','owner_confirmed','category_normalized','runtime_route','sandbox_curriculum','focused_tests','fleet_regression','Code Trust','accounting_regeneration'],
              'promotion_action':'merge unique capability into existing owner when equivalent; create a new canonical bot only when identity/work scope is genuinely distinct'
            })
    payload={'schema':'dreamco.legacy_bot_promotion_backlog.v1','candidate_count':len(rows),'candidates':rows,'truth_boundary':'This is a promotion backlog, not a live fleet expansion. No candidate is canonical until all gates pass.'}
    OUT.parent.mkdir(parents=True,exist_ok=True); REPORT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(payload,indent=2)+'\n')
    lines=['# Legacy Bot Promotion Backlog','',f'- Candidates: **{len(rows)}**','', '| Candidate | Owner | Source | Status |','| --- | --- | --- | --- |']
    for row in rows[:1000]: lines.append(f"| `{row['candidate_slug']}` | {row['primary_owner']} | `{row['source_path']}` | {row['status']} |")
    REPORT.write_text('\n'.join(lines)+'\n')
    print(json.dumps({'ok':True,'candidates':len(rows),'output':str(OUT.relative_to(ROOT))},indent=2)); return 0
if __name__=='__main__': raise SystemExit(main())
