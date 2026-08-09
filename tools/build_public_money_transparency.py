#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
CFG=json.loads((ROOT/'config/government-nonprofit-contract-readiness.json').read_text())
SOURCES=json.loads((ROOT/'config/global-government-source-adapters.json').read_text())
OUT=ROOT/'config/generated/public-money-transparency-backlog.json'

def main()->int:
    cases=[]
    for source in SOURCES['sources']:
        fiscal_types=[x for x in source['data_types'] if any(k in x.lower() for k in ['debt','spending','expenditure','obligation','budget','award','contract','grant','revenue','interest','account','recipient','vendor'])]
        if not fiscal_types: continue
        cases.append({
          'source_id':source['id'],'jurisdiction':source['jurisdiction'],'authority':source['authority'],'purpose':source['purpose'],'runtime_state':source['runtime_state'],
          'data_types':fiscal_types,'required_outputs':CFG['fiscal_transparency']['citizen_outputs'],'dimensions':CFG['fiscal_transparency']['dimensions'],
          'status':'adapter_or_runtime_evidence_required','freshness_expectation':source['freshness_expectation'],'live_claim_rule':source['live_claim_rule']
        })
    trackers=[
      {'id':'debt_tracker','measures':['official debt measure','change from prior official record','debt service/interest where available'],'freshness':'source dependent'},
      {'id':'spending_tracker','measures':['spending/obligation/expenditure','agency/department','program/function','recipient/vendor','geography'],'freshness':'source dependent'},
      {'id':'budget_vs_actual','measures':['budget/appropriation','actual spending','variance'],'freshness':'source dependent'},
      {'id':'contract_grant_tracker','measures':['award amount','recipient/vendor','agency/program','location','date'],'freshness':'source dependent'},
      {'id':'citizen_money_map','measures':['where money came from','where money went','per-capita where population source exists','largest changes','source freshness'],'freshness':'source dependent'}]
    payload={'schema':'dreamco.public_money_transparency_backlog.v1','adapter_case_count':len(cases),'tracker_count':len(trackers),'adapter_cases':cases,'trackers':trackers,'daily_refresh_rule':'Refresh only as often as each authoritative source supports. Daily scheduler may check for updates, but must preserve the official source date and must not manufacture new daily figures.','truth_boundary':CFG['fiscal_transparency']['rule']}
    OUT.parent.mkdir(parents=True,exist_ok=True); OUT.write_text(json.dumps(payload,indent=2)+'\n')
    print(json.dumps({'ok':True,'adapter_cases':len(cases),'trackers':len(trackers),'output':str(OUT.relative_to(ROOT))},indent=2)); return 0
if __name__=='__main__': raise SystemExit(main())
