#!/usr/bin/env python3
"""Generate practice-only teaching records from executable regression tests."""
import ast,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
FILES=['tests/test_cycle_evidence_integrity.py','tests/test_strategy_policy.py','tests/test_source_division_catalog.py','tests/test_verify_frontier_evidence.py','tests/test_general_intelligence.py']

def build():
    records=[]
    for name in FILES:
        raw=(ROOT/name).read_text();tree=ast.parse(raw)
        for node in ast.walk(tree):
            if not isinstance(node,(ast.FunctionDef,ast.AsyncFunctionDef)) or not node.name.startswith('test_'):continue
            code=ast.get_source_segment(raw,node)
            records.append({'id':hashlib.sha256((name+node.name).encode()).hexdigest(),'topic':node.name.removeprefix('test_').replace('_',' '),'mode':'practice_only','training_allowed':False,'rights_verified':False,'license':'pending_review','provenance':{'file':name,'line':node.lineno,'source_sha256':hashlib.sha256(raw.encode()).hexdigest()},'exercise':code,'levels':{'beginner':'Identify the invalid input and explain why accepting it would produce a false claim.','intermediate':'Run the regression, inspect the canonical implementation, and explain the failure boundary.','expert':'Add a new adversarial case and verify that valid evidence remains accepted without weakening any gate.'},'quiz':'Which assertion proves this software behavior, and what real-world capability does it not prove?','production_ready':False})
    return records
if __name__=='__main__':
    rows=build();(ROOT/'data/buddy-bootcamp/regression-candidates.jsonl').write_text(''.join(json.dumps(r,sort_keys=True)+'\n' for r in rows));print(len(rows))
