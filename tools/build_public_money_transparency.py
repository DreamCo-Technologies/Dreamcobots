#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
CFG=json.loads((ROOT/'config/government-nonprofit-contract-readiness.json').read_text())
SOURCES=json.loads((ROOT/'config/global-government-source-adapters.json').read_text())
OUT=ROOT/'config/generated/public-money-transparency-benchmarks.json'

def main()->int:
    cases=[]
    for source in SOURCES['sources']:
        fiscal_types=[x for x in source['data_types'] if any(k in x.lower() for k in ['debt','spending','expenditure','obligation','budget','award','contract','grant','revenue','interest','account','recipient','vendor'])]
        if not fiscal_types: continue
        cases.append({
          'case_id':f"public-money:{source['id']}",'domain':'public_money_transparency','source_id':source['id'],'jurisdiction':source['jurisdiction'],'authority':source['authority'],'purpose':source['purpose'],'runtime_state':source['runtime_state'],
          'data_types':fiscal_types,'required_outputs':CFG['fiscal_transparency']['citizen_outputs'],'dimensions':CFG['fiscal_transparency']['dimensions'],
          'benchmark_dimensions':['source authority','freshness','definition fidelity','reconciliation','coverage','traceability','citizen readability','drilldown quality','update reliability','error detection'],
          'status':'needs_runtime_baseline','freshness_expectation':source['freshness_expectation'],'live_claim_rule':source['live_claim_rule']
        })
    trackers=[
      {'case_id':'tracker:debt','domain':'public_money_tracker','intent':'debt tracker','measures':['official debt measure','change from prior official record','debt service/interest where available'],'freshness':'source dependent','status':'needs_runtime_baseline'},
      {'case_id':'tracker:spending','domain':'public_money_tracker','intent':'spending tracker','measures':['spending/obligation/expenditure','agency/department','program/function','recipient/vendor','geography'],'freshness':'source dependent','status':'needs_runtime_baseline'},
      {'case_id':'tracker:budget-vs-actual','domain':'public_money_tracker','intent':'budget versus actual','measures':['budget/appropriation','actual spending','variance'],'freshness':'source dependent','status':'needs_runtime_baseline'},
      {'case_id':'tracker:contracts-grants','domain':'public_money_tracker','intent':'contract and grant tracker','measures':['award amount','recipient/vendor','agency/program','location','date'],'freshness':'source dependent','status':'needs_runtime_baseline'},
      {'case_id':'tracker:citizen-money-map','domain':'public_money_tracker','intent':'citizen money map','measures':['where money came from','where money went','per-capita where population source exists','largest changes','source freshness'],'freshness':'source dependent','status':'needs_runtime_baseline'}]
    payload={'schema':'dreamco.public_money_transparency_benchmarks.v2','case_count':len(cases)+len(trackers),'adapter_case_count':len(cases),'tracker_count':len(trackers),'cases':cases+trackers,'daily_refresh_rule':'Refresh only as often as each authoritative source supports. A daily scheduler may check for updates, but must preserve the official source date and must not manufacture new daily figures.','truth_boundary':CFG['fiscal_transparency']['rule']}
    OUT.parent.mkdir(parents=True,exist_ok=True); OUT.write_text(json.dumps(payload,indent=2)+'\n')
    print(json.dumps({'ok':True,'cases':payload['case_count'],'adapter_cases':len(cases),'trackers':len(trackers),'output':str(OUT.relative_to(ROOT))},indent=2)); return 0
if __name__=='__main__': raise SystemExit(main())
