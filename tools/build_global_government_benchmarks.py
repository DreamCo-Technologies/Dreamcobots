#!/usr/bin/env python3
from __future__ import annotations

import hashlib,json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
MODEL=json.loads((ROOT/'config/global-government-operating-model.json').read_text())
CFG=json.loads((ROOT/'config/government-nonprofit-contract-readiness.json').read_text())
SOURCES=json.loads((ROOT/'config/global-government-source-adapters.json').read_text())
OUT=ROOT/'config/generated/global-government-benchmarks.json'
GAPS=ROOT/'config/generated/global-government-gap-workers.json'

def slug(v): return re.sub(r'[^a-z0-9]+','-',v.lower()).strip('-')
def stable(v): return hashlib.sha256(v.encode()).hexdigest()[:16]

def main()->int:
    cases=[]
    for fn in MODEL['reference_taxonomy']['functions']:
        for level in CFG['government_levels']:
            cases.append({'case_id':f'function:{slug(fn)}:{slug(level)}','domain':'government_function','functional_class':fn,'government_level':level,'status':'planned_not_run','dimensions':CFG['benchmark_dimensions']})
    for family in CFG['government_job_families']:
        cases.append({'case_id':f'job:{slug(family)}','domain':'government_job','job_family':family,'government_levels':CFG['government_levels'],'status':'planned_not_run','required_analysis':['task inventory','AI assist fit','AI automation fit','human authority boundary','time/cost/error baseline','tool/system inventory','sandbox tests','before/after evidence']})
    for service in CFG['citizen_service_journeys']:
        cases.append({'case_id':f'service:{slug(service)}','domain':'citizen_service','service_journey':service,'status':'planned_not_run','simplification_metrics':CFG['service_simplification_metrics'],'required_analysis':['official service source','eligibility source','forms/documents','fees if any','processing guidance','status tracking','accessibility/language','steps/handoffs','time/cost baseline','simplification prototype']})
    for lane in CFG['local_economic_development']:
        cases.append({'case_id':f'econdev:{slug(lane)}','domain':'local_economic_development','intent':lane,'status':'planned_not_run','required_analysis':['current local data','peer benchmark','funding/incentive sources','implementation owners','economic metric','before/after measurement']})
    for lane in CFG['housing_real_estate_intelligence']:
        cases.append({'case_id':f'housing:{slug(lane)}','domain':'housing_real_estate','intent':lane,'status':'planned_not_run','required_analysis':['official property/program source','current eligibility/fee terms where applicable','geography','freshness','professional/user workflow','risk/legal boundary']})
    for lane in MODEL['priority_improvement_lanes']:
        cases.append({'case_id':f'improvement:{slug(lane)}','domain':'government_improvement','intent':lane,'status':'planned_not_run','improvement_dimensions':MODEL['improvement_dimensions']})
    for source in SOURCES['sources']:
        cases.append({'case_id':f"source:{source['id']}",'domain':'global_government_source_adapter','source_id':source['id'],'jurisdiction':source['jurisdiction'],'runtime_state':source['runtime_state'],'status':'planned_not_run','quality_checks':SOURCES['quality_checks']})
    workers=[]
    parallel=['department benchmark bot','government job/task bot','citizen service UX bot','fiscal transparency bot','economic development bot','housing intelligence bot','data/API integration bot','security/privacy bot','accessibility/language bot','builder bot','sandbox QA bot','release reviewer']
    for case in cases:
        workers.append({'worker_id':f"global-gov-gap-{stable(case['case_id'])}",'case_id':case['case_id'],'parallel_roles':parallel,'status':'needs_runtime_baseline','required_outputs':['authoritative sources','baseline','workflow/department map','gap score','improvement proposal','sandbox fixtures','security/privacy review','before/after benchmark','runtime evidence'],'closure_rule':'close only with current jurisdiction evidence and passing affected tests/benchmarks'})
    payload={'schema':'dreamco.global_government_benchmarks.v1','case_count':len(cases),'functional_taxonomy':MODEL['reference_taxonomy'],'cases':cases,'truth_boundary':MODEL['truth_rule']}
    gaps={'schema':'dreamco.global_government_gap_workers.v1','worker_count':len(workers),'workers':workers,'truth_boundary':'Every global government benchmark case has a parallel closure team, but assignment is not proof of capability or improvement.'}
    OUT.parent.mkdir(parents=True,exist_ok=True); OUT.write_text(json.dumps(payload,indent=2)+'\n'); GAPS.write_text(json.dumps(gaps,indent=2)+'\n')
    print(json.dumps({'ok':True,'cases':len(cases),'workers':len(workers),'output':str(OUT.relative_to(ROOT))},indent=2)); return 0
if __name__=='__main__': raise SystemExit(main())
