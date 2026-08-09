#!/usr/bin/env python3
from __future__ import annotations

import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
CAT=json.loads((ROOT/'config/global-government-discovered-catalog.json').read_text())
CFG=json.loads((ROOT/'config/government-nonprofit-contract-readiness.json').read_text())
MODEL=json.loads((ROOT/'config/global-government-operating-model.json').read_text())
OUT=ROOT/'config/generated/government-department-improvement-benchmarks.json'

def stable(v): return hashlib.sha256(v.encode()).hexdigest()[:16]
def main()->int:
    cases=[]
    departments={d.get('department_id'):d for d in CAT.get('departments',[]) if d.get('department_id')}
    for dep_id,dep in departments.items():
        base={'department_id':dep_id,'jurisdiction_id':dep.get('jurisdiction_id'),'department_name':dep.get('official_name'),'functional_class':dep.get('functional_class'),'status':'needs_runtime_baseline'}
        for lane in MODEL['priority_improvement_lanes']:
            cases.append({'case_id':f"department:{stable(dep_id)}:{stable(lane)}",'domain':'department_improvement','intent':lane,**base,'benchmark_dimensions':MODEL['improvement_dimensions'],'required_outputs':['authoritative mandate/source','current workflow map','baseline cost/time/error/backlog','systems/vendors/APIs inventory','service/job/task impact','improvement proposal','sandbox evidence','before/after score']})
    for svc in CAT.get('services',[]):
        cases.append({'case_id':f"service:{stable(str(svc.get('service_id')))}",'domain':'government_service_simplification','department_id':svc.get('department_id'),'service_id':svc.get('service_id'),'intent':svc.get('purpose') or svc.get('official_name'),'status':'needs_runtime_baseline','benchmark_dimensions':CFG['service_simplification_metrics'],'required_outputs':['official source','eligibility source','forms/documents/fees','journey steps','friction baseline','simplification prototype','accessibility/language review','runtime evidence']})
    for job in CAT.get('jobs',[]):
        cases.append({'case_id':f"job:{stable(str(job.get('job_id')))}",'domain':'government_job_task_improvement','department_id':job.get('department_id'),'job_id':job.get('job_id'),'intent':job.get('title'),'status':'needs_runtime_baseline','required_outputs':['official job/task source','task inventory','tool/system map','AI assist candidates','AI automation candidates','human authority boundary','time/error baseline','sandbox tests','before/after evidence']})
    payload={'schema':'dreamco.government_department_improvement_benchmarks.v1','discovered_department_count':len(departments),'discovered_service_count':len(CAT.get('services',[])),'discovered_job_count':len(CAT.get('jobs',[])),'case_count':len(cases),'cases':cases,'discovery_status':'ready' if departments else 'awaiting_authoritative_jurisdiction_department_discovery','truth_boundary':CAT['truth_rule']}
    OUT.parent.mkdir(parents=True,exist_ok=True); OUT.write_text(json.dumps(payload,indent=2)+'\n')
    print(json.dumps({'ok':True,'departments':len(departments),'services':len(CAT.get('services',[])),'jobs':len(CAT.get('jobs',[])),'cases':len(cases),'status':payload['discovery_status'],'output':str(OUT.relative_to(ROOT))},indent=2)); return 0
if __name__=='__main__': raise SystemExit(main())
