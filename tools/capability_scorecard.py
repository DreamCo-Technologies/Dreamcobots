#!/usr/bin/env python3
from __future__ import annotations
import argparse,json
from pathlib import Path
WEIGHTS={'capability_coverage':20,'benchmark_mastery':25,'study_plan_completion':15,'training_execution':15,'reliability':10,'regression_control':10,'evidence_quality':5}

def clamp(x): return max(0.0,min(100.0,float(x)))
def score(d):
    dims={k:clamp(d.get(k,0)) for k in WEIGHTS}
    overall=sum(dims[k]*w/100 for k,w in WEIGHTS.items())
    return {'overall_score':round(overall,2),'dimension_scores':dims,'top_gaps':sorted(((k,round(100-v,2)) for k,v in dims.items()),key=lambda x:x[1],reverse=True)}
def main():
    p=argparse.ArgumentParser(); p.add_argument('input'); p.add_argument('--output',default='capability-score.json'); a=p.parse_args()
    d=json.loads(Path(a.input).read_text()); result=score(d); Path(a.output).write_text(json.dumps(result,indent=2)+'\n'); print(json.dumps(result,indent=2))
if __name__=='__main__': main()
