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
# Derived review/measurement artifacts are not executable benchmark sources.
DERIVED_METADATA_ARTIFACTS=frozenset({'benchmark-suite-gap-contracts.json','buddy_benchmark_index.json','buddy_model_benchmarks.json','system-speed-accuracy-benchmarks.json'})

def stable(v:str)->str: return hashlib.sha256(v.encode()).hexdigest()[:16]

def case_id(row:dict,index:int,source:str)->str:
    for key in ('case_id','gap_id','task_id','benchmark_id','id','slug'):
        if row.get(key): return str(row[key])
    label=row.get('intent') or row.get('step') or row.get('metric') or row.get('scenario') or row.get('task') or str(index)
    return f'{Path(source).stem}:{stable(str(label))}'

def main()->int:
    entries=[]; seen=set(); sources=[]; errors=[]; placeholders=0
    for path in sorted(GEN.glob('*.json')):
        if 'benchmark' not in path.name.lower(): continue
        if path.name=='parallel-benchmark-gap-registry.json' or path.name in DERIVED_METADATA_ARTIFACTS: continue
        source=str(path.relative_to(ROOT)); sources.append(source)
        try:
            doc=json.loads(path.read_text())
        except (OSError, ValueError) as exc:
            errors.append(f'{source}: invalid JSON or unreadable artifact ({type(exc).__name__})')
            continue
        if not isinstance(doc, dict):
            errors.append(f'{source}: benchmark artifact must be an object')
            continue
        arrays=[]
        for key in ('cases','gaps','benchmarks','tasks','workers'):
            value=doc.get(key)
            if isinstance(value,list): arrays.append((key,value))
            elif key in doc: errors.append(f'{source}:{key}: benchmark case collection must be an array')
        if arrays and not any(rows for _,rows in arrays):
            errors.append(f'{source}: no executable benchmark cases; preserve as a blocked source')
        if not arrays:
            synthetic={'case_id':f'artifact:{path.stem}','intent':f'Define benchmark cases for {path.stem}'}
            arrays=[('artifact',[synthetic])]
            placeholders += 1
        for key,rows in arrays:
            for index,row in enumerate(rows):
                if not isinstance(row,dict):
                    errors.append(f'{source}:{key}[{index}]: benchmark case must be an object')
                    continue
                cid=case_id(row,index,source); unique=f'{source}|{cid}'
                if unique in seen:
                    errors.append(f'{source}:{key}[{index}]: duplicate case identity {cid!r}')
                    continue
                seen.add(unique)
                risk='high' if any(word in json.dumps(row).lower() for word in ('security','payment','auth','government','regulated','privacy','medical','legal')) else 'normal'
                entries.append({
                  'gap_worker_id':f'benchmark-gap-{stable(unique)}','source_artifact':source,'source_array':key,'case_id':cid,
                  'domain':row.get('domain') or row.get('medium') or row.get('phase') or row.get('scenario') or 'general',
                  'risk':risk,'status':'needs_benchmark_definition' if key=='artifact' else 'needs_runtime_baseline',
                  'parallel_team':['domain benchmark bot','gap analyst bot','builder bot','integration bot','sandbox QA bot','security/compliance bot','performance bot','business-value bot','release reviewer'],
                  'engineering_specialists':[member['id'] for member in TEAM['team']],
                  'required_outputs':['baseline evidence','capability/quality gap','canonical owner','acceptance criteria','parallel build proposals','sandbox/regression tests','security review when applicable','before/after score','runtime evidence','release recommendation'],
                  'closure_rule':'close only when required benchmark threshold and affected regression evidence pass'
                })
    if not sources: errors.append('no benchmark source artifacts discovered')
    payload={'schema':'dreamco.parallel_benchmark_gap_registry.v1','benchmark_source_count':len(set(sources)),'benchmark_case_count':len(entries),'defined_case_count':len(entries)-placeholders,'artifact_placeholder_count':placeholders,'registry_complete':not errors,'source_errors':errors,'parallel_lane_limit':TEAM['parallel_policy']['maximum_parallel_lanes'],'entries':entries,'truth_boundary':'Every discovered benchmark case gets an accountable closure path. A worker assignment is not evidence that the gap is closed.'}
    OUT.parent.mkdir(parents=True,exist_ok=True); REPORT.parent.mkdir(parents=True,exist_ok=True); OUT.write_text(json.dumps(payload,indent=2)+'\n')
    lines=['# Parallel Benchmark Gap Registry','',f"- Benchmark sources: **{payload['benchmark_source_count']}**",f"- Benchmark cases with workers: **{len(entries)}**",f"- Parallel lane limit: **{payload['parallel_lane_limit']}**",'']
    for row in entries[:1000]: lines.append(f"- `{row['case_id']}` → `{row['gap_worker_id']}` ({row['domain']}, {row['risk']})")
    if errors: lines += ['', '## Registry integrity blockers', ''] + [f'- {error}' for error in errors]
    REPORT.write_text('\n'.join(lines)+'\n')
    print(json.dumps({'ok':not errors,'sources':payload['benchmark_source_count'],'cases':len(entries),'placeholders':placeholders,'errors':len(errors),'output':str(OUT.relative_to(ROOT))},indent=2)); return 2 if errors else 0
if __name__=='__main__': raise SystemExit(main())
