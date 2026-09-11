#!/usr/bin/env python3
import argparse,json,sys
from pathlib import Path
R=Path(__file__).resolve().parents[1]; S=R/'config'/'buddy-universal-connection-catalog.json'; O=R/'website'/'data'/'buddy-universal-connections.json'
def build():
 d=json.loads(S.read_text()); ids=[]
 for x in d['connections']:
  if not x['setup_url'].startswith('https://'): raise ValueError(f"HTTPS required: {x['id']}")
  ids.append(x['id'])
 if len(ids)!=len(set(ids)): raise ValueError('duplicate connection ids')
 return d
def main():
 p=argparse.ArgumentParser();p.add_argument('--check',action='store_true');a=p.parse_args();e=json.dumps(build(),indent=2,sort_keys=True)+'\n'
 if a.check and (not O.exists() or O.read_text()!=e): print('Setup Center data stale',file=sys.stderr);return 1
 if not a.check: O.parent.mkdir(parents=True,exist_ok=True);O.write_text(e)
 print('Setup Center data validated' if a.check else 'Setup Center data generated');return 0
if __name__=='__main__':raise SystemExit(main())
