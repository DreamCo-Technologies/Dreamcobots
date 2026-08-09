#!/usr/bin/env python3
from __future__ import annotations

import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
CFG=json.loads((ROOT/'config/continuous-human-value-discovery.json').read_text())
CAP=ROOT/'config/generated/universal-capability-benchmark.json'
GAPS=ROOT/'config/generated/engineering-gap-closure-plan.json'
OUT=ROOT/'config/generated/continuous-value-discovery-backlog.json'
def load(path,default): return json.loads(path.read_text()) if path.exists() else default
def sid(v): return hashlib.sha256(v.encode()).hexdigest()[:16]
def main()->int:
    cap=load(CAP,{'cases':[]}); gaps=load(GAPS,{'gaps':[]}); candidates=[]
    for loop in CFG['loops']:
        questions=loop.get('questions') or [loop.get('question','')]
        for question in questions:
            if not question: continue
            iid=f"discovery-{sid(loop['id']+'|'+question)}"
            candidates.append({'idea_id':iid,'loop':loop['id'],'problem_prompt':question,'source':'continuous-human-value-discovery','status':'benchmark_needed','owner':'CommandCore','required_evidence':['problem evidence','user/buyer','baseline time/cost/risk','solution hypothesis','sandbox plan','before/after benchmark']})
    for case in cap.get('cases',[]):
        candidates.append({'idea_id':f"benchmark-{sid(case['case_id'])}",'loop':'benchmark_gap_value','problem_prompt':f"Improve or productize benchmark: {case['case_id']}",'source':case['case_id'],'status':'benchmark_needed','owner':'benchmark gap worker','required_evidence':['baseline score','gap','reusable improvement','user/business value','retest']})
    for gap in gaps.get('gaps',[]):
        gid=str(gap.get('gap_id','gap')); candidates.append({'idea_id':f"gap-{sid(gid)}",'loop':'intelligence','problem_prompt':f"Close engineering gap {gid}",'source':gid,'status':'sandbox_building','owner':gap.get('primary_owner'),'required_evidence':['acceptance tests','implementation','security review','runtime evidence']})
    payload={'schema':'dreamco.continuous_value_discovery_backlog.v2','candidate_count':len(candidates),'loop_count':len(CFG['loops']),'candidates':candidates,'required_product_evidence':CFG['required_product_evidence'],'truth_boundary':CFG['truth_rule']}
    OUT.parent.mkdir(parents=True,exist_ok=True); OUT.write_text(json.dumps(payload,indent=2)+'\n'); print(json.dumps({'ok':True,'candidates':len(candidates),'output':str(OUT.relative_to(ROOT))},indent=2)); return 0
if __name__=='__main__': raise SystemExit(main())
