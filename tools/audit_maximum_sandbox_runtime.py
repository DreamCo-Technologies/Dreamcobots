#!/usr/bin/env python3
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
MATRIX=ROOT/'config/generated/maximum-sandbox-matrix.json'
EVIDENCE=ROOT/'config/sandbox-runtime-evidence.json'
OUT=ROOT/'config/generated/maximum-sandbox-runtime-audit.json'


def main()->int:
    if not MATRIX.exists(): raise SystemExit('Run tools/build_maximum_sandbox_matrix.py first')
    matrix=json.loads(MATRIX.read_text()); evidence_doc=json.loads(EVIDENCE.read_text())
    workers={w['worker_id']:w for w in matrix.get('workers',[])}
    evidence=evidence_doc.get('evidence',[])
    counts=Counter(row.get('status') for row in evidence)
    workers_with_pass={row.get('worker_id') for row in evidence if row.get('status')=='passed' and row.get('worker_id') in workers}
    canonical={w['worker_id'] for w in workers.values() if w.get('worker_type')=='canonical_bot'}
    canonical_with_pass=canonical & workers_with_pass
    payload={
      'schema':'dreamco.maximum_sandbox_runtime_audit.v1',
      'planned_worker_count':len(workers),
      'evidence_record_count':len(evidence),
      'status_counts':dict(counts),
      'workers_with_any_pass_evidence':len(workers_with_pass),
      'canonical_worker_count':len(canonical),
      'canonical_workers_with_pass_evidence':len(canonical_with_pass),
      'canonical_worker_runtime_coverage_percent':round((len(canonical_with_pass)/len(canonical))*100,2) if canonical else 0,
      'all_canonical_workers_have_runtime_evidence':bool(canonical) and canonical==canonical_with_pass,
      'failed_evidence_count':counts.get('failed',0),
      'blocked_evidence_count':counts.get('blocked',0),
      'truth_boundary':evidence_doc['truth_rule']
    }
    OUT.parent.mkdir(parents=True,exist_ok=True); OUT.write_text(json.dumps(payload,indent=2)+'\n')
    print(json.dumps(payload,indent=2)); return 0

if __name__=='__main__': raise SystemExit(main())
