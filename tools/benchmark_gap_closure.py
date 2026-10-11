#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,hashlib,math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def passing_evidence(record, root):
    """Require reviewed, hash-bound local results; declarations never prove closure."""
    evidence = record.get('evidence')
    if not isinstance(evidence, dict) or evidence.get('review_status') != 'reviewed' or not evidence.get('reviewer'):
        return False
    try:
        root = root.resolve()
        source = (root / evidence['source']).resolve()
        artifact = (root / evidence['artifact']).resolve()
        if not source.is_relative_to(root) or not artifact.is_relative_to(root):
            return False
        raw = artifact.read_bytes()
        if hashlib.sha256(raw).hexdigest() != evidence['artifact_sha256']:
            return False
        result = json.loads(raw)
        return (result.get('benchmark_id') == record['benchmark_id']
                and result.get('source_sha256') == hashlib.sha256(source.read_bytes()).hexdigest()
                and result.get('status') == 'passed' and result.get('regression_status') == 'passed'
                and type(result.get('tests_run')) is int and result['tests_run'] > 0
                and type(result.get('tests_failed')) is int and result['tests_failed'] == 0
                and type(result.get('score')) in (int, float) and math.isfinite(result['score'])
                and result['score'] == record['baseline'] and result.get('target') == record['target'])
    except (KeyError, TypeError, ValueError, OSError):
        return False

def plan(record, root=ROOT):
    required=['division_id','benchmark_id','baseline','target']
    missing=[k for k in required if k not in record]
    if missing:
        return {'status':'blocked','missing':missing}
    if any(type(record[k]) not in (int, float) or not math.isfinite(record[k]) for k in ('baseline', 'target')):
        return {'status': 'blocked', 'reason': 'finite numeric measurements required'}
    gap=record['target']-record['baseline']
    closed = gap <= 0 and passing_evidence(record, Path(root))
    return {'status':'closed' if closed else 'open','division_id':record['division_id'],'benchmark_id':record['benchmark_id'],'gap':gap,'next_action':'train_practice_sandbox_transfer' if gap>0 else 'regression_check', 'evidence_verified': closed}

def main():
    p=argparse.ArgumentParser(); p.add_argument('input'); p.add_argument('--output',default='benchmark-gap-plan.json'); a=p.parse_args()
    data=json.loads(Path(a.input).read_text())
    records=data if isinstance(data,list) else data.get('records',[])
    result=[plan(r) for r in records]
    Path(a.output).write_text(json.dumps({'schema':'dreamco.benchmark_gap_plan.v1','records':result},indent=2)+'\n')
    print(json.dumps({'records':len(result),'open':sum(x.get('status')=='open' for x in result),'blocked':sum(x.get('status')=='blocked' for x in result)},indent=2))
if __name__=='__main__': main()
