#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
WORK=ROOT/'config/generated/universal-work-ai-catalog.json'
REG=ROOT/'config/work-platform-benchmark-registry.json'
OUT=ROOT/'config/generated/work-platform-benchmark-backlog.json'

KEYWORDS={
 'freelance_marketplaces':['write','design','develop','research','analy','translate','edit','program','document','market','advertis','consult','account','bookkeep'],
 'creator_platforms':['create','write','record','video','audio','music','teach','train','present','publish'],
 'ecommerce_marketplaces':['product','sell','market','inventory','merchandise','retail','package'],
 'developer_marketplaces':['software','program','code','database','api','web','application','automate','debug','test'],
 'app_marketplaces':['software','application','mobile','web','tool','automation'],
 'procurement_rfq':['manufactur','supplier','procure','contract','construction','design','engineering','service','maintenance'],
 'direct_business_sales':['business','customer','sales','market','service','support','consult','manage','analy','automate'],
 'employer_job_boards':['manage','operate','prepare','maintain','coordinate','perform','develop','analy','assist','supervise'],
 'gig_service_marketplaces':['service','clean','repair','install','deliver','assist','photograph','design','write','tutor'],
 'dreamco_marketplace':['write','design','develop','research','analy','translate','edit','program','document','market','sales','support','service','automate','plan','create','teach','train','manufactur','procure']
}

def main()->int:
    reg=json.loads(REG.read_text())
    if not WORK.exists():
        payload={'schema':'dreamco.work_platform_benchmark_backlog.v1','status':'work_catalog_missing','task_count':0,'benchmark_case_count':0,'cases':[],'truth_boundary':reg['truth_rule']}
        OUT.parent.mkdir(parents=True,exist_ok=True); OUT.write_text(json.dumps(payload,indent=2)+'\n'); print(json.dumps(payload,indent=2)); return 0
    work=json.loads(WORK.read_text()); cases=[]
    platforms={p['id']:p for p in reg['platforms']}
    for task in work.get('tasks',[]):
        lower=task['task'].lower()
        for pid,platform in platforms.items():
            hits=[k for k in KEYWORDS.get(pid,[]) if k in lower]
            if task.get('licensed_or_high_risk_hint'):
                applicability='regulated_or_restricted'
            elif task.get('physical_world_requirement') and pid in {'freelance_marketplaces','developer_marketplaces','app_marketplaces','creator_platforms'}:
                applicability='requires_physical_presence'
            elif len(hits)>=2:
                applicability='strong_fit'
            elif hits:
                applicability='possible'
            else:
                applicability='not_applicable'
            if applicability!='not_applicable':
                cases.append({
                    'task_id':task['task_id'],'occupation':task.get('occupation_title'),'task':task['task'],'platform_id':pid,
                    'applicability':applicability,'matching_signals':hits,'automation_level':task['automation_level'],
                    'policy_fit':'requires_current_platform_verification','price_evidence':None,'fees':None,'demand_evidence':None,
                    'runtime_connection_state':platform['access_state'],'benchmark_status':'planned_not_run',
                    'required_metrics':['correctness','speed','cost','human_review_time','platform_fit','profitability_simulation','risk']
                })
    payload={'schema':'dreamco.work_platform_benchmark_backlog.v1','status':'generated','task_count':work.get('task_count',0),'platform_count':len(platforms),'benchmark_case_count':len(cases),'cases':cases,'truth_boundary':reg['truth_rule']}
    OUT.parent.mkdir(parents=True,exist_ok=True); OUT.write_text(json.dumps(payload,indent=2)+'\n')
    print(json.dumps({'ok':True,'tasks':payload['task_count'],'platforms':len(platforms),'cases':len(cases),'output':str(OUT.relative_to(ROOT))},indent=2)); return 0
if __name__=='__main__': raise SystemExit(main())
