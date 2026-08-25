#!/usr/bin/env python3
from __future__ import annotations
import argparse,json
from pathlib import Path

def plan(record):
    required=['division_id','benchmark_id','baseline','target']
    missing=[k for k in required if k not in record]
    if missing:
        return {'status':'blocked','missing':missing}
    gap=record['target']-record['baseline']
    return {'status':'open' if gap>0 else 'closed','division_id':record['division_id'],'benchmark_id':record['benchmark_id'],'gap':gap,'next_action':'train_practice_sandbox_transfer' if gap>0 else 'regression_check'}

def main():
    p=argparse.ArgumentParser(); p.add_argument('input'); p.add_argument('--output',default='benchmark-gap-plan.json'); a=p.parse_args()
    data=json.loads(Path(a.input).read_text())
    records=data if isinstance(data,list) else data.get('records',[])
    result=[plan(r) for r in records]
    Path(a.output).write_text(json.dumps({'schema':'dreamco.benchmark_gap_plan.v1','records':result},indent=2)+'\n')
    print(json.dumps({'records':len(result),'open':sum(x.get('status')=='open' for x in result),'blocked':sum(x.get('status')=='blocked' for x in result)},indent=2))
if __name__=='__main__': main()
