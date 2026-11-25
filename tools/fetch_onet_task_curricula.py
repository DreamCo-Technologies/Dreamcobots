#!/usr/bin/env python3
"""Fetch the complete O*NET OnLine occupation/task inventory using an API key.

Set ONET_API_KEY from an O*NET Web Services developer account. API key is read
only from the environment and is never written to artifacts or logs.
"""
from __future__ import annotations
import argparse, json, os, time, urllib.error, urllib.parse, urllib.request
from pathlib import Path
from build_onet_task_curricula import build

BASE="https://api-v2.onetcenter.org"

def get_json(path:str,key:str)->dict:
    req=urllib.request.Request(BASE+path,headers={"X-API-Key":key,"Accept":"application/json","User-Agent":"DreamCo-Buddy-Bootcamp/1.0"})
    with urllib.request.urlopen(req,timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))

def fetch_all(key:str,delay:float)->tuple[list[dict],int]:
    occupations=[]; start=1; total=None
    while total is None or start<=total:
        data=get_json(f"/online/occupations/?start={start}&end={start+199}",key)
        batch=data.get("occupation",[])
        occupations.extend(batch); total=int(data.get("total",len(occupations)))
        if not batch: break
        start=int(data.get("end",start+len(batch)))+1
        time.sleep(delay)
    rows=[]
    for index,occupation in enumerate(occupations,1):
        if occupation.get("datalevel") is False: continue
        code=occupation.get("code")
        if not code: continue
        start=1
        while True:
            data=get_json(f"/online/occupations/{urllib.parse.quote(code,safe='')}/details/tasks?sort=category&start={start}&end={start+199}",key)
            tasks=data.get("task",[])
            for task in tasks:
                rows.append({"O*NET-SOC Code":code,"Occupation Title":occupation.get("title"),
                    "Task ID":task.get("id"),"Task":task.get("title"),
                    "Task Type":task.get("category","unspecified"),
                    "Importance":task.get("importance")})
            if not tasks or not data.get("next"): break
            start=int(data.get("end",start+len(tasks)))+1
        if index%25==0: print(f"Processed {index}/{len(occupations)} occupation records; tasks={len(rows)}")
        time.sleep(delay)
    return rows,len(occupations)

def main()->int:
    p=argparse.ArgumentParser()
    p.add_argument("--out-dir",required=True)
    p.add_argument("--version",default="O*NET Web Services 2.0 current")
    p.add_argument("--delay-seconds",type=float,default=0.25)
    a=p.parse_args()
    key=os.getenv("ONET_API_KEY")
    if not key: raise SystemExit("ONET_API_KEY is not set; request a free O*NET Web Services API key.")
    rows,occupation_records=fetch_all(key,a.delay_seconds)
    result=build(rows,a.version)
    result["source"]["official_api"]="https://services.onetcenter.org/reference/online"
    result["inventory"]["occupation_records_returned"]=occupation_records
    result["inventory"]["data_level_task_occupations"]=result["inventory"]["occupations"]
    out=Path(a.out_dir); out.mkdir(parents=True,exist_ok=True)
    (out/"onet-task-curricula.json").write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    (out/"onet-task-curricula.md").write_text(
      "# O*NET occupation and task curricula\n\n"+
      f"- Occupation records returned: {occupation_records}\n"+
      f"- Occupations with task records: {result['inventory']['occupations']}\n"+
      f"- Task statements: {result['inventory']['task_statements']}\n"+
      "- Source: O*NET Web Services 2.0; retain required attribution and version.\n",encoding="utf-8")
    print(json.dumps(result["inventory"],indent=2))
    return 0
if __name__=="__main__": raise SystemExit(main())
