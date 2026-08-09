#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
GEN=ROOT/'config/generated'
TEAM=json.loads((ROOT/'config/engineering-gap-closure-team.json').read_text())
OUT=GEN/'parallel-benchmark-gap-registry.json'
REPORT=ROOT/'reports/PARALLEL_BENCHMARK_GAP_REGISTRY.md'

def stable(v:str)->str: return hashlib.sha256(v.encode()).hexdigest()[:16]

def case_id(row:dict,index:int,source:str)->str:
    for key in ('case_id','gap_id','task_id','benchmark_id','id','slug'):
        if row.get(key): return str(row[key])
    label=row.get('intent') or row.get('step') or row.get('metric') or row.get('scenario') or row.get('task') or str(index)
    return f'{Path(source).stem}:{stable(str(label))}'

def main()->int:
    entries=[]; seen=set(); sources=[]
    for path in sorted(GEN.glob('*.json')):
        if 'benchmark' not in path.name.lower(): continue
        if path.name=='parallel-benchmark-gap-registry.json': continue
        try: doc=json.loads(path.read_text())
        except Exception: continue
        source=str(path.relative_to(ROOT)); sources.append(source)
        arrays=[]
        for key in ('cases','gaps','benchmarks','tasks','workers'):
            value=doc.get(key)
            if isinstance(value,list): arrays.append((key,value))
        if not arrays:
            synthetic={'case_id':f'artifact:{path.stem}','intent':f'Validate benchmark artifact {path.stem}'}; arrays=[('artifact',[synthetic])]
        for key,rows in arrays:
            for index,row in enumerate(rows):
                if not isinstance(row,dict): continue
                cid=case_id(row,index,source); unique=f'{source}|{cid}'
                if unique in seen: continue
                seen.add(unique)
                risk='high' if any(word in json.dumps(row).lower() for word in ('security','payment','auth','government','regulated','privacy','medical','legal')) else 'normal'
                entries.append({
                  'gap_worker_id':f'benchmark-gap-{stable(unique)}','source_artifact':source,'source_array':key,'case_id':cid,
                  'domain':row.get('domain') or row.get('medium') or row.get('phase') or row.get('scenario') or 'general',
                  'risk':risk,'status':'needs_runtime_baseline',
                  'parallel_team':['domain benchmark bot','gap analyst bot','builder bot','integration bot','sandbox QA bot','security/compliance bot','performance bot','business-value bot','release reviewer'],
                  'engineering_specialists':[member['id'] for member in TEAM['team']],
                  'required_outputs':['baseline evidence','capability/quality gap','canonical owner','acceptance criteria','parallel build proposals','sandbox/regression tests','security review when applicable','before/after score','runtime evidence','release recommendation'],
                  'closure_rule':'close only when required benchmark threshold and affected regression evidence pass'
                })
    payload={'schema':'dreamco.parallel_benchmark_gap_registry.v1','benchmark_source_count':len(set(sources)),'benchmark_case_count':len(entries),'parallel_lane_limit':TEAM['parallel_policy']['maximum_parallel_lanes'],'entries':entries,'truth_boundary':'Every discovered benchmark case gets an accountable closure path. A worker assignment is not evidence that the gap is closed.'}
    OUT.parent.mkdir(parents=True,exist_ok=True); REPORT.parent.mkdir(parents=True,exist_ok=True); OUT.write_text(json.dumps(payload,indent=2)+'\n')
    lines=['# Parallel Benchmark Gap Registry','',f"- Benchmark sources: **{payload['benchmark_source_count']}**",f"- Benchmark cases with workers: **{len(entries)}**",f"- Parallel lane limit: **{payload['parallel_lane_limit']}**",'']
    for row in entries[:1000]: lines.append(f"- `{row['case_id']}` → `{row['gap_worker_id']}` ({row['domain']}, {row['risk']})")
    REPORT.write_text('\n'.join(lines)+'\n')
    print(json.dumps({'ok':True,'sources':payload['benchmark_source_count'],'cases':len(entries),'output':str(OUT.relative_to(ROOT))},indent=2)); return 0
if __name__=='__main__': raise SystemExit(main())
