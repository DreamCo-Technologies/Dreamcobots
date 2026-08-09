#!/usr/bin/env python3
from __future__ import annotations

import json,re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
CFG=json.loads((ROOT/'config/universal-human-computer-ai-benchmark.json').read_text())
GOV=json.loads((ROOT/'config/government-nonprofit-contract-readiness.json').read_text())
CREATIVE=json.loads((ROOT/'config/creative-studio-mastery-benchmarks.json').read_text())
WORK=ROOT/'config/generated/universal-work-ai-catalog.json'
OUT=ROOT/'config/generated/universal-capability-benchmark.json'
GAPS=ROOT/'config/generated/universal-capability-gap-workers.json'

def slug(v): return re.sub(r'[^a-z0-9]+','-',v.lower()).strip('-')
def load(path,default): return json.loads(path.read_text()) if path.exists() else default

def main()->int:
    cases=[]
    for domain,intents in CFG['domains'].items():
        for intent in intents:
            cases.append({'case_id':f'{domain}:{slug(intent)}','domain':domain,'intent':intent,'source':'universal_computer_ai_map','dimensions':CFG['benchmark_dimensions']})
    for family in GOV['government_job_families']:
        cases.append({'case_id':f'government-job:{slug(family)}','domain':'government_job','intent':family,'source':'government_program','dimensions':GOV['benchmark_dimensions']})
    for journey in GOV['citizen_service_journeys']:
        cases.append({'case_id':f'government-service:{slug(journey)}','domain':'government_service','intent':journey,'source':'government_program','dimensions':GOV['benchmark_dimensions']})
    for step in GOV['contracting_lifecycle']:
        cases.append({'case_id':f'government-contract:{slug(step)}','domain':'government_contracting','intent':step,'source':'government_program','dimensions':GOV['benchmark_dimensions']})
    for step in GOV['nonprofit_lifecycle']:
        cases.append({'case_id':f'nonprofit:{slug(step)}','domain':'nonprofit','intent':step,'source':'government_program','dimensions':GOV['benchmark_dimensions']})
    for medium in ('film','books','music'):
        for step in CREATIVE[medium]:
            cases.append({'case_id':f'{medium}:{slug(step)}','domain':medium,'intent':step,'source':'creative_studio','dimensions':CREATIVE['benchmark_dimensions']})
    work=load(WORK,{'occupations':[],'tasks':[]})
    for occ in work.get('occupations',[]):
        cases.append({'case_id':f"occupation:{occ['occupation_id']}",'domain':'occupation','intent':occ['title'],'source':'O*NET','dimensions':CFG['benchmark_dimensions']})
    for task in work.get('tasks',[]):
        cases.append({'case_id':f"task:{task['task_id']}",'domain':'human_task','intent':task['task'],'source':'O*NET','dimensions':task.get('benchmark_dimensions',CFG['benchmark_dimensions'])})
    workers=[]
    for case in cases:
        workers.append({'worker_id':f"gap-{slug(case['case_id'])}",'case_id':case['case_id'],'status':'sandbox_backlog','parallel_roles':CFG['gap_parallel_workers'],'required_outputs':['baseline score','gap evidence','owner','fix/build proposal','sandbox tests','retest evidence'],'live_allowed':False})
    payload={'schema':'dreamco.universal_capability_benchmark.generated.v1','case_count':len(cases),'domain_count':len(set(c['domain'] for c in cases)),'cases':cases,'discovery_loop':CFG['discovery_loop'],'continuous_opportunity_loops':CFG['continuous_opportunity_loops'],'truth_boundary':CFG['truth_rule']}
    gap={'schema':'dreamco.universal_capability_gap_workers.v1','worker_count':len(workers),'workers':workers,'truth_boundary':CFG['gap_rule']}
    OUT.parent.mkdir(parents=True,exist_ok=True); OUT.write_text(json.dumps(payload,indent=2)+'\n'); GAPS.write_text(json.dumps(gap,indent=2)+'\n')
    print(json.dumps({'ok':True,'cases':len(cases),'domains':payload['domain_count'],'gap_workers':len(workers),'output':str(OUT.relative_to(ROOT))},indent=2)); return 0
if __name__=='__main__': raise SystemExit(main())
