#!/usr/bin/env python3
from __future__ import annotations
import argparse,json
from pathlib import Path

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--gaps',required=True); ap.add_argument('--out',required=True); a=ap.parse_args()
    gaps=json.loads(Path(a.gaps).read_text()).get('queue',[])
    actions={"CLOSE_GAPS":"TRAIN_TARGETED","RUN_BENCHMARKS":"MEASURE_BASELINE","RETEST_FAILURES":"REGRESSION_RETEST","RUN_SANDBOX":"SANDBOX_VALIDATE"}
    queue=[]
    for i,g in enumerate(gaps):
        action=g.get('action','RUN_BENCHMARKS')
        queue.append({'rank':i+1,'division':g.get('division'),'benchmark':g.get('benchmark'),'priority':g.get('priority',99),'action':actions.get(action,'MEASURE_BASELINE'),'source_action':action,'reason':g.get('reason',''),'requires_evidence':True})
    Path(a.out).write_text(json.dumps({'schema':'dreamco.benchmark_training_queue.v1','queue':queue,'policy':'finish each eligible job by recording evidence and immediately claim the next highest-value item'},indent=2)+'\n')
    print(json.dumps({'training_items':len(queue)},indent=2))
if __name__=='__main__': main()
