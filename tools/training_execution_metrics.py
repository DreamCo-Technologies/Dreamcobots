#!/usr/bin/env python3
from __future__ import annotations
import argparse,json
from pathlib import Path

def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--runs',required=True); ap.add_argument('--out',required=True); a=ap.parse_args()
 d=json.loads(Path(a.runs).read_text()); runs=d.get('runs',[])
 completed=[r for r in runs if r.get('status')=='completed']; failed=[r for r in runs if r.get('status')=='failed']; planned=[r for r in runs if r.get('status')=='planned']
 report={'schema':'dreamco.training_execution_metrics.v1','selected':len(runs),'completed':len(completed),'failed':len(failed),'planned':len(planned),'execution_rate':(len(completed)/len(runs) if runs else 0),'evidence_rate':sum(bool(r.get('evidence')) for r in completed)/len(completed) if completed else 0,'policy':'training activity is not mastery; only reproducible benchmark evidence can change mastery state'}
 Path(a.out).write_text(json.dumps(report,indent=2)+'\n'); print(json.dumps(report,indent=2))
if __name__=='__main__': main()
