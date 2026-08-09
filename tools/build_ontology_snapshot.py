#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
ONTOLOGY=json.loads((ROOT/'config/dreamco-operational-ontology.json').read_text())
UNIFIED=ROOT/'config/generated/unified-bot-system.json'
WORK=ROOT/'config/generated/universal-work-ai-catalog.json'
GAPS=ROOT/'config/generated/engineering-gap-closure-plan.json'
CONN=ROOT/'config/generated/runtime-connection-readiness.json'
OUT=ROOT/'config/generated/dreamco-ontology-snapshot.json'

def load(path,default): return json.loads(path.read_text()) if path.exists() else default

def stable_id(value:str)->str: return hashlib.sha256(value.encode('utf-8')).hexdigest()[:16]

def main()->int:
    unified=load(UNIFIED,{'canonical_bots':[],'legacy_candidates':[]})
    work=load(WORK,{'occupations':[],'tasks':[]})
    gaps=load(GAPS,{'gaps':[]})
    conn=load(CONN,{'connections':[]})
    objects=[]; links=[]
    for bot in unified.get('canonical_bots',[]):
        bid=f"bot:{bot['slug']}"; objects.append({'id':bid,'type':'Bot','name':bot.get('display_name'),'state':bot.get('status'),'source':bot.get('source')})
        did=f"division:{bot['division']}"; links.append({'type':'BOT_BELONGS_TO_DIVISION','from':bid,'to':did})
        for cap in bot.get('capabilities',[]):
            cid=f"capability:{bot['slug']}:{stable_id(cap)}"; objects.append({'id':cid,'type':'Capability','name':cap}); links.append({'type':'BOT_HAS_CAPABILITY','from':bid,'to':cid})
    divisions=sorted({b['division'] for b in unified.get('canonical_bots',[])})
    for division in divisions: objects.append({'id':f'division:{division}','type':'Division','name':division})
    for row in unified.get('legacy_candidates',[]): objects.append({'id':f"legacy:{row.get('slug') or stable_id(row['source'])}",'type':'SpecialistAgent','name':row.get('slug') or row['source'],'state':'legacy_pending_promotion','source':row['source']})
    for occ in work.get('occupations',[]): objects.append({'id':f"occupation:{occ['occupation_id']}",'type':'Occupation','name':occ['title'],'source':'O*NET'})
    for task in work.get('tasks',[]):
        tid=f"human-task:{task['task_id']}"; objects.append({'id':tid,'type':'HumanTask','name':task['task'],'state':task['automation_level'],'source':'O*NET'}); links.append({'type':'JOB_ROLE_CONTAINS_HUMAN_TASK','from':f"occupation:{task['occupation_id']}",'to':tid})
    for gap in gaps.get('gaps',[]): objects.append({'id':f"gap:{gap['gap_id']}",'type':'Gap','name':gap.get('capability'),'state':gap.get('status'),'owner':gap.get('primary_owner')})
    for c in conn.get('connections',[]): objects.append({'id':f"connection:{c['connection_id']}",'type':'Connection','name':c.get('label'),'state':c.get('state')})
    payload={'schema':'dreamco.ontology_snapshot.v1','object_count':len(objects),'link_count':len(links),'object_type_counts':{},'objects':objects,'links':links,'ontology_schema_version':ONTOLOGY['version'],'truth_boundary':ONTOLOGY['truth_rule']}
    for obj in objects: payload['object_type_counts'][obj['type']]=payload['object_type_counts'].get(obj['type'],0)+1
    OUT.parent.mkdir(parents=True,exist_ok=True); OUT.write_text(json.dumps(payload,indent=2)+'\n')
    print(json.dumps({'ok':True,'objects':len(objects),'links':len(links),'types':payload['object_type_counts'],'output':str(OUT.relative_to(ROOT))},indent=2)); return 0
if __name__=='__main__': raise SystemExit(main())
