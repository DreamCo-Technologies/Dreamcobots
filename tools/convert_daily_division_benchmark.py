#!/usr/bin/env python3
from __future__ import annotations
import argparse,json
from pathlib import Path

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--input',required=True); ap.add_argument('--output',required=True); args=ap.parse_args()
    source=json.loads(Path(args.input).read_text())
    rows=[]
    for item in source.get('divisionResults',[]):
        rows.append({
            'division': item['division'],
            'benchmark': 'buddy-division-contract',
            'score': item['score'],
            'target': 100,
            'status': 'pass' if item['status']=='pass' else 'failed',
            'evidence_count': item['passed'],
            'source': 'run_daily_division_benchmarks',
        })
    Path(args.output).write_text(json.dumps({'schema':'dreamco.benchmark_scores.v1','results':rows},indent=2)+'\n')
    print(json.dumps({'divisions':len(rows),'measured':sum(r['score'] is not None for r in rows)},indent=2))
if __name__=='__main__': main()
