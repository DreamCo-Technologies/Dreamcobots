#!/usr/bin/env python3
from __future__ import annotations
import argparse,json
from pathlib import Path

def pct(x): return round(x,2) if isinstance(x,(int,float)) else None

def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--baseline',required=True); ap.add_argument('--final',required=True); ap.add_argument('--out',required=True); a=ap.parse_args()
 b=json.loads(Path(a.baseline).read_text()).get('results',[]); f=json.loads(Path(a.final).read_text()).get('results',[])
 bm={str(x.get('benchmark')):x for x in b}; fm={str(x.get('benchmark')):x for x in f}; rows=[]
 for k in sorted(set(bm)|set(fm)):
  bs=bm.get(k,{}).get('score'); fs=fm.get(k,{}).get('score'); rows.append({'benchmark':k,'baseline':bs,'final':fs,'delta':pct(fs-bs) if isinstance(bs,(int,float)) and isinstance(fs,(int,float)) else None})
 report={'schema':'dreamco.dacl_customer_report.v1','results':rows,'claims_policy':'report measured deltas only; do not infer AGI/frontier status from training activity'}
 Path(a.out).write_text(json.dumps(report,indent=2)+'\n'); print(json.dumps({'benchmarks':len(rows),'measured_deltas':sum(r['delta'] is not None for r in rows)},indent=2))
if __name__=='__main__': main()
