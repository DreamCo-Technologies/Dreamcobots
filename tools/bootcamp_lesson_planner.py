#!/usr/bin/env python3
from __future__ import annotations
import argparse,json
from pathlib import Path

def main():
 p=argparse.ArgumentParser(); p.add_argument('input'); p.add_argument('--output',default='bootcamp-plan.json'); a=p.parse_args()
 data=json.loads(Path(a.input).read_text()); units=data if isinstance(data,list) else data.get('units',[])
 plan=[]
 for u in units:
  missing=[k for k in ('capability_id','objective','benchmark','provenance') if not u.get(k)]
  plan.append({'capability_id':u.get('capability_id'),'status':'blocked' if missing else 'ready','missing':missing,'stages':['lesson','practice','sandbox','transfer','score','remediate','regression','evidence']})
 Path(a.output).write_text(json.dumps({'schema':'dreamco.bootcamp_plan.v1','units':plan},indent=2)+'\n')
 print(json.dumps({'units':len(plan),'ready':sum(x['status']=='ready' for x in plan),'blocked':sum(x['status']=='blocked' for x in plan)},indent=2))
if __name__=='__main__': main()
