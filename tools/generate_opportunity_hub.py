#!/usr/bin/env python3
import argparse, json, sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'config'/'buddy-opportunity-resource-registry.json'
OUTPUT=ROOT/'website'/'data'/'buddy-opportunity-resources.json'

def build():
    data=json.loads(SOURCE.read_text(encoding='utf-8'))
    required={'id','name','category','url','authority','services','action','approval'}
    ids=[]
    for row in data['resources']:
        missing=required-set(row)
        if missing: raise ValueError(f"{row.get('id','resource')} missing {sorted(missing)}")
        if not row['url'].startswith('https://'): raise ValueError(f"HTTPS required: {row['id']}")
        ids.append(row['id'])
    if len(ids)!=len(set(ids)): raise ValueError('Duplicate resource IDs')
    return data

def main():
    parser=argparse.ArgumentParser(); parser.add_argument('--check',action='store_true'); args=parser.parse_args()
    expected=json.dumps(build(),indent=2,sort_keys=True)+'\n'
    if args.check:
        if not OUTPUT.exists() or OUTPUT.read_text(encoding='utf-8')!=expected:
            print('Opportunity Hub data is stale; run tools/generate_opportunity_hub.py',file=sys.stderr); return 1
    else:
        OUTPUT.parent.mkdir(parents=True,exist_ok=True); OUTPUT.write_text(expected,encoding='utf-8')
    print('Opportunity Hub data validated' if args.check else 'Opportunity Hub data generated'); return 0
if __name__=='__main__': raise SystemExit(main())
