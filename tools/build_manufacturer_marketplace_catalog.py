#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SCOUT=ROOT/'config'/'china-us-tech-manufacturing-scout-program.json'
MARKET=ROOT/'config'/'us-manufacturer-rfq-marketplace-program.json'
OUT=ROOT/'website'/'data'/'manufacturer-marketplace.json'


def main()->int:
    scout=json.loads(SCOUT.read_text(encoding='utf-8'))
    market=json.loads(MARKET.read_text(encoding='utf-8'))
    payload={
      'schema':'dreamco.manufacturer_marketplace_catalog.v1',
      'status':'prototype_ready_for_verified_data',
      'manufacturer_count':0,
      'rfq_count':0,
      'quote_count':0,
      'opportunity_count':0,
      'manufacturer_profile_fields':market['manufacturer_profile'],
      'rfq_fields':market['rfq_fields'],
      'quote_fields':market['quote_fields'],
      'matching_score':market['matching_score'],
      'marketplace_features':market['marketplace_features'],
      'scout_sources':scout['source_classes'],
      'scout_comparison_dimensions':scout['comparison_dimensions'],
      'opportunity_types':scout['opportunity_types'],
      'manufacturers':[],
      'rfqs':[],
      'quotes':[],
      'opportunities':[],
      'truth_boundary':'No supplier, RFQ, quote or opportunity is invented for the demo. Counts grow only from verified/user-provided/authorized data.'
    }
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(payload,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'ok':True,'output':str(OUT.relative_to(ROOT)),'status':payload['status']},indent=2))
    return 0

if __name__=='__main__':
    raise SystemExit(main())
