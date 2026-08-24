#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,fnmatch
from pathlib import Path

PATTERNS={
 'capabilities':['capabilities/**','bots/**','framework/**'],
 'vrs':['**/*VR*','**/*vr*','goals/**','plans/**'],
 'benchmarks':['benchmarks/**','**/*benchmark*'],
 'study_plans':['plans/**','training/**','bootcamp/**'],
 'strategies':['strategies/**','learning/**','global_learning_system/**'],
 'divisions':['divisions/**','masterbots/**'],
 'evidence':['evidence/**','artifacts/**','reports/**','actions/**']}

def classify(path):
 return [k for k,patterns in PATTERNS.items() if any(fnmatch.fnmatch(path,p) for p in patterns)]

def main():
 p=argparse.ArgumentParser(); p.add_argument('root',nargs='?',default='.'); p.add_argument('--output',default='buddy-system-inventory.json'); a=p.parse_args(); root=Path(a.root)
 inventory={k:[] for k in PATTERNS}
 for f in root.rglob('*'):
  if f.is_file() and '.git' not in f.parts:
   rel=f.relative_to(root).as_posix()
   for k in classify(rel): inventory[k].append(rel)
 out={'schema':'dreamco.buddy_system_inventory.v1','inventory':inventory,'counts':{k:len(v) for k,v in inventory.items()}}
 Path(a.output).write_text(json.dumps(out,indent=2)+'\n'); print(json.dumps(out['counts'],indent=2))
if __name__=='__main__': main()
