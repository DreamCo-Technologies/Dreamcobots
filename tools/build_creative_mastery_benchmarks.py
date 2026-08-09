#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
CFG=json.loads((ROOT/'config/creative-studio-mastery-benchmarks.json').read_text())
OUT=ROOT/'config/generated/creative-studio-mastery-benchmarks.json'
GAPS=ROOT/'config/generated/creative-studio-gap-workers.json'

def slug(v:str)->str: return re.sub(r'[^a-z0-9]+','-',v.lower()).strip('-')

def main()->int:
    cases=[]; workers=[]
    medium_workers={'film':'film benchmark director','books':'book benchmark editor','music':'music benchmark producer'}
    for medium in ('film','books','music'):
        for step in CFG[medium]:
            cid=f'{medium}:{slug(step)}'
            cases.append({'case_id':cid,'medium':medium,'step':step,'dimensions':CFG['benchmark_dimensions'],'rights_rule':CFG['rights_rule'],'status':'planned_not_run'})
            workers.append({'worker_id':f'creative-gap-{slug(cid)}','case_id':cid,'primary_role':medium_workers[medium],'parallel_roles':CFG['gap_workers'],'required_outputs':['brief fixture','baseline','quality score','technical checks','rights/provenance check','gap plan','retest evidence'],'live_allowed':False})
    payload={'schema':'dreamco.creative_studio_mastery.generated.v1','case_count':len(cases),'medium_counts':{m:sum(c['medium']==m for c in cases) for m in ('film','books','music')},'cases':cases,'truth_boundary':CFG['truth_rule']}
    gap={'schema':'dreamco.creative_studio_gap_workers.v1','worker_count':len(workers),'workers':workers,'truth_boundary':'Every creative benchmark case has parallel quality, continuity, rights, platform and tool-building lanes; no gap closes without human/technical evidence.'}
    OUT.parent.mkdir(parents=True,exist_ok=True); OUT.write_text(json.dumps(payload,indent=2)+'\n'); GAPS.write_text(json.dumps(gap,indent=2)+'\n')
    print(json.dumps({'ok':True,'cases':len(cases),'gap_workers':len(workers),'output':str(OUT.relative_to(ROOT))},indent=2)); return 0
if __name__=='__main__': raise SystemExit(main())
