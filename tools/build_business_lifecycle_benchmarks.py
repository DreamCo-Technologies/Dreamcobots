#!/usr/bin/env python3
from __future__ import annotations

import json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
CFG=json.loads((ROOT/'config/business-lifecycle-benchmark.json').read_text())
OUT=ROOT/'config/generated/business-lifecycle-benchmarks.json'
GAPS=ROOT/'config/generated/business-lifecycle-gap-workers.json'
def slug(v): return re.sub(r'[^a-z0-9]+','-',v.lower()).strip('-')
def main()->int:
    cases=[]; workers=[]
    for phase,steps in CFG['lifecycle_phases'].items():
        for step in steps:
            cid=f'business:{phase}:{slug(step)}'
            cases.append({'case_id':cid,'phase':phase,'step':step,'organization_styles':CFG['organization_styles'],'dimensions':CFG['benchmark_dimensions'],'status':'planned_not_run'})
            workers.append({'worker_id':f'gap-{slug(cid)}','case_id':cid,'primary_role':'business architect','parallel_roles':CFG['specialist_lanes'],'required_outputs':['workflow model','baseline','automation/assist fit','professional dependency','tool/integration map','sandbox tests','business value hypothesis','retest evidence'],'live_allowed':False})
    payload={'schema':'dreamco.business_lifecycle_benchmarks.v1','organization_style_count':len(CFG['organization_styles']),'phase_count':len(CFG['lifecycle_phases']),'case_count':len(cases),'cases':cases,'truth_boundary':CFG['truth_rule']}
    gap={'schema':'dreamco.business_lifecycle_gap_workers.v1','worker_count':len(workers),'workers':workers,'truth_boundary':'Every business lifecycle benchmark has a parallel specialist closure path and remains sandbox-only until evidence passes.'}
    OUT.parent.mkdir(parents=True,exist_ok=True); OUT.write_text(json.dumps(payload,indent=2)+'\n'); GAPS.write_text(json.dumps(gap,indent=2)+'\n')
    print(json.dumps({'ok':True,'styles':len(CFG['organization_styles']),'cases':len(cases),'gap_workers':len(workers)},indent=2)); return 0
if __name__=='__main__': raise SystemExit(main())
