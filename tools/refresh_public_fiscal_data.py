#!/usr/bin/env python3
from __future__ import annotations

import argparse,json,urllib.error,urllib.request
from datetime import datetime,timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'config/generated/public-fiscal-latest.json'
US_DEBT_URL='https://api.fiscaldata.treasury.gov/services/api/fiscal_service/v2/accounting/od/debt_to_penny?sort=-record_date&page[size]=1'

def fetch_json(url:str)->dict:
    req=urllib.request.Request(url,headers={'User-Agent':'DreamCo-Buddy-Public-Fiscal-Transparency/1.0'})
    with urllib.request.urlopen(req,timeout=30) as response:
        return json.loads(response.read().decode('utf-8'))

def main()->int:
    ap=argparse.ArgumentParser(); ap.add_argument('--allow-offline',action='store_true'); args=ap.parse_args()
    records=[]; failures=[]
    try:
        doc=fetch_json(US_DEBT_URL); row=(doc.get('data') or [])[0]
        records.append({
          'jurisdiction':'US','source_id':'us_treasury_debt_to_penny','authority':'U.S. Department of the Treasury Fiscal Data','source_endpoint':US_DEBT_URL,
          'source_record_date':row.get('record_date'),'currency':'USD','debt_measure':'total_public_debt_outstanding','debt_value':row.get('tot_pub_debt_out_amt'),
          'debt_held_public':row.get('debt_held_public_amt'),'intragovernmental_holdings':row.get('intragov_hold_amt'),'runtime_status':'verified','fetched_at':datetime.now(timezone.utc).isoformat()
        })
    except Exception as exc:
        failures.append({'source_id':'us_treasury_debt_to_penny','error':str(exc),'runtime_status':'blocked'})
    payload={'schema':'dreamco.public_fiscal_latest.v1','generated_at':datetime.now(timezone.utc).isoformat(),'records':records,'failures':failures,'runtime_verified_count':len(records),'failed_source_count':len(failures),'truth_boundary':'Values are copied from authoritative source records with their source dates. The generated-at timestamp is not the fiscal record date, and missing sources are never estimated.'}
    OUT.parent.mkdir(parents=True,exist_ok=True); OUT.write_text(json.dumps(payload,indent=2)+'\n')
    print(json.dumps({'ok':not failures,'records':len(records),'failures':len(failures),'output':str(OUT.relative_to(ROOT))},indent=2))
    if failures and not args.allow_offline: return 1
    return 0
if __name__=='__main__': raise SystemExit(main())
