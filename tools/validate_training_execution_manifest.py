#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,sys
from pathlib import Path

def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--manifest',required=True); a=ap.parse_args()
 d=json.loads(Path(a.manifest).read_text()); items=d.get('items',[]); errors=[]
 for i,x in enumerate(items):
  if x.get('execution_status') not in {'ready','blocked'}: errors.append(f'item {i}: invalid execution status')
  if x.get('execution_status')=='ready' and not x.get('mode'): errors.append(f'item {i}: missing mode')
  if x.get('curriculum_contract',{}).get('requires_runtime_evidence') is not True: errors.append(f'item {i}: runtime evidence contract missing')
 if d.get('no_auto_mastery') is not True: errors.append('manifest must forbid automatic mastery')
 result={'schema':'dreamco.training_execution_manifest_validation.v1','items':len(items),'valid':not errors,'errors':errors}
 print(json.dumps(result,indent=2)); sys.exit(1 if errors else 0)
if __name__=='__main__': main()
