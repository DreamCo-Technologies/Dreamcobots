#!/usr/bin/env python3
"""Execute only declared, local training actions and emit auditable evidence.
External model training or service calls are intentionally not invented here.
"""
from __future__ import annotations
import argparse,json,time
from pathlib import Path

ALLOWED={"MEASURE_BASELINE","TRAIN_TARGETED","REGRESSION_RETEST","SANDBOX_VALIDATE"}

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--queue',required=True); ap.add_argument('--out',required=True); ap.add_argument('--limit',type=int,default=20); a=ap.parse_args()
    q=json.loads(Path(a.queue).read_text()).get('queue',[])
    selected=q[:max(0,a.limit)]; runs=[]
    for item in selected:
        action=item.get('action')
        if action not in ALLOWED: status='rejected'; reason='unsupported action'
        elif not item.get('requires_evidence',True): status='rejected'; reason='evidence contract missing'
        else: status='planned'; reason='awaiting concrete registered runner'
        runs.append({'rank':item.get('rank'),'division':item.get('division'),'benchmark':item.get('benchmark'),'action':action,'status':status,'reason':reason,'started_at':time.time()})
    out={'schema':'dreamco.benchmark_training_execution.v1','runs':runs,'executed':0,'planned':sum(r['status']=='planned' for r in runs),'rejected':sum(r['status']=='rejected' for r in runs),'policy':'never claim training or mastery until a registered runner returns reproducible evidence'}
    Path(a.out).write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({'selected':len(runs),'planned':out['planned'],'executed':0},indent=2))
if __name__=='__main__': main()
