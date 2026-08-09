#!/usr/bin/env python3
from __future__ import annotations

import argparse,json,urllib.request
from datetime import datetime,timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'config/generated/public-fiscal-latest.json'
US_DEBT_URL='https://api.fiscaldata.treasury.gov/services/api/fiscal_service/v2/accounting/od/debt_to_penny?sort=-record_date&page[size]=1'
US_AGENCIES_URL='https://api.usaspending.gov/api/v2/references/toptier_agencies/'

def fetch_json(url:str)->dict:
    req=urllib.request.Request(url,headers={'User-Agent':'DreamCo-Buddy-Public-Fiscal-Transparency/1.0'})
    with urllib.request.urlopen(req,timeout=30) as response:
        return json.loads(response.read().decode('utf-8'))

def main()->int:
    ap=argparse.ArgumentParser(); ap.add_argument('--allow-offline',action='store_true'); args=ap.parse_args()
    records=[]; agency_spending=[]; failures=[]; fetched_at=datetime.now(timezone.utc).isoformat()
    try:
        doc=fetch_json(US_DEBT_URL); row=(doc.get('data') or [])[0]
        records.append({
          'jurisdiction':'US','source_id':'us_treasury_debt_to_penny','authority':'U.S. Department of the Treasury Fiscal Data','source_endpoint':US_DEBT_URL,
          'source_record_date':row.get('record_date'),'currency':'USD','debt_measure':'total_public_debt_outstanding','debt_value':row.get('tot_pub_debt_out_amt'),
          'debt_held_public':row.get('debt_held_public_amt'),'intragovernmental_holdings':row.get('intragov_hold_amt'),'runtime_status':'verified','fetched_at':fetched_at
        })
    except Exception as exc:
        failures.append({'source_id':'us_treasury_debt_to_penny','error':str(exc),'runtime_status':'blocked'})
    try:
        doc=fetch_json(US_AGENCIES_URL)
        for row in doc.get('results',[]):
            agency_spending.append({
              'jurisdiction':'US','source_id':'us_usaspending','authority':'USAspending.gov / U.S. Treasury','source_endpoint':US_AGENCIES_URL,
              'agency_id':row.get('agency_id'),'toptier_code':row.get('toptier_code'),'agency_name':row.get('agency_name'),'abbreviation':row.get('abbreviation'),
              'active_fiscal_year':row.get('active_fy'),'active_fiscal_quarter':row.get('active_fq'),'outlay_amount':row.get('outlay_amount'),'obligated_amount':row.get('obligated_amount'),'budget_authority_amount':row.get('budget_authority_amount'),
              'percentage_of_total_budget_authority':row.get('percentage_of_total_budget_authority'),'runtime_status':'verified','fetched_at':fetched_at
            })
    except Exception as exc:
        failures.append({'source_id':'us_usaspending','error':str(exc),'runtime_status':'blocked'})
    payload={
      'schema':'dreamco.public_fiscal_latest.v2','generated_at':fetched_at,'debt_records':records,'agency_spending_records':agency_spending,'failures':failures,
      'runtime_verified_source_count':len({r['source_id'] for r in records}|({x['source_id'] for x in agency_spending} if agency_spending else set())),
      'failed_source_count':len(failures),
      'truth_boundary':'Values are copied from authoritative source records with their fiscal/source context. The generated-at timestamp is not the fiscal record date; debt and spending use different accounting periods and definitions and must not be mixed without explicit normalization.'
    }
    OUT.parent.mkdir(parents=True,exist_ok=True); OUT.write_text(json.dumps(payload,indent=2)+'\n')
    print(json.dumps({'ok':not failures,'debt_records':len(records),'agency_spending_records':len(agency_spending),'failures':len(failures),'output':str(OUT.relative_to(ROOT))},indent=2))
    if failures and not args.allow_offline: return 1
    return 0
if __name__=='__main__': raise SystemExit(main())
