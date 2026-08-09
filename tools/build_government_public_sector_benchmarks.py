#!/usr/bin/env python3
from __future__ import annotations

import json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
CFG=json.loads((ROOT/'config/government-nonprofit-contract-readiness.json').read_text())
SOURCES=json.loads((ROOT/'config/government-source-adapters.json').read_text())
OUT=ROOT/'config/generated/government-public-sector-benchmarks.json'
GAPS=ROOT/'config/generated/government-public-sector-gap-workers.json'
def slug(v): return re.sub(r'[^a-z0-9]+','-',v.lower()).strip('-')
def main()->int:
    cases=[]
    groups=[('government_job',CFG['government_job_families']),('citizen_service',CFG['citizen_service_journeys']),('government_contracting',CFG['contracting_lifecycle']),('nonprofit',CFG['nonprofit_lifecycle'])]
    for domain,items in groups:
        for item in items:
            cases.append({'case_id':f'{domain}:{slug(item)}','domain':domain,'intent':item,'government_levels':CFG['government_levels'],'dimensions':CFG['benchmark_dimensions'],'status':'planned_not_run','human_authority_boundaries':CFG['high_risk_human_authority']})
    source_cases=[]
    for source in SOURCES['sources']:
        source_cases.append({'case_id':f"source:{source['id']}",'domain':'government_source_adapter','intent':source['purpose'],'source_id':source['id'],'access_modes':source['access_modes'],'runtime_state':source['runtime_state'],'status':'planned_not_run'})
    workers=[]
    for case in cases+source_cases:
        workers.append({'worker_id':f"public-gap-{slug(case['case_id'])}",'case_id':case['case_id'],'parallel_roles':['government workflow analyst','public-service UX bot','contract/grant researcher','requirements/compliance bot','data/provenance bot','sandbox QA bot','security/privacy bot','accessibility bot','builder bot'],'required_outputs':['current authoritative source where applicable','baseline','workflow map','human-authority boundary','sandbox fixtures','accuracy/time-saved benchmark','gap/fix plan','runtime evidence'],'live_allowed':False})
    payload={'schema':'dreamco.government_public_sector_benchmarks.v1','case_count':len(cases)+len(source_cases),'government_workflow_cases':len(cases),'source_adapter_cases':len(source_cases),'cases':cases+source_cases,'contract_readiness_evidence':CFG['contract_readiness_evidence'],'truth_boundary':CFG['truth_rule']}
    gap={'schema':'dreamco.government_public_sector_gap_workers.v1','worker_count':len(workers),'workers':workers,'truth_boundary':'Government and nonprofit benchmark gaps require current authority/provenance and preserve authorized-human decision boundaries.'}
    OUT.parent.mkdir(parents=True,exist_ok=True); OUT.write_text(json.dumps(payload,indent=2)+'\n'); GAPS.write_text(json.dumps(gap,indent=2)+'\n')
    print(json.dumps({'ok':True,'cases':payload['case_count'],'gap_workers':len(workers),'output':str(OUT.relative_to(ROOT))},indent=2)); return 0
if __name__=='__main__': raise SystemExit(main())
