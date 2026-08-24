#!/usr/bin/env python3
"""Generate auditable contracts for every canonical 65-MasterBot division.
This creates executable contract metadata, not fake implementations."""
from __future__ import annotations
import argparse,json
from pathlib import Path

def main():
 p=argparse.ArgumentParser(); p.add_argument('--registry',required=True); p.add_argument('--out',required=True); a=p.parse_args()
 registry=json.loads(Path(a.registry).read_text())
 divisions=registry.get('divisions') or registry.get('masterbots') or []
 out=[]
 for d in divisions:
  did=str(d.get('id') or d.get('division_id') or d.get('name'))
  name=d.get('name',did)
  out.append({'division_id':did,'name':name,'entrypoint':f'divisions/{did}/main.py','cli':f'python -m divisions.{did}.main','tests':f'tests/divisions/{did}','benchmark_suite':f'benchmark/divisions/{did}','training_plan':f'training/divisions/{did}','dashboard_route':f'/actions/divisions/{did}','command_center_route':f'/actions/divisions/{did}/command-center','evidence_path':f'benchmark-evidence/divisions/{did}','runnable_contract':True,'implementation_status':'contract-generated','note':'must be backed by real source code and tests before claiming runnable'})
 payload={'schema':'dreamco.division_runtime_contracts.v1','count':len(out),'divisions':out,'claim_policy':'contract metadata does not equal implementation or benchmark mastery'}
 Path(a.out).write_text(json.dumps(payload,indent=2)+'\n'); print(json.dumps({'count':len(out)},indent=2))
if __name__=='__main__': main()
