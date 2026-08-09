#!/usr/bin/env python3
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
MATRIX=ROOT/'config/generated/maximum-sandbox-matrix.json'
EVIDENCE=ROOT/'config/sandbox-runtime-evidence.json'
FLEET_E2E=ROOT/'website/data/bot-fleet-e2e.json'
OUT=ROOT/'config/generated/maximum-sandbox-runtime-audit.json'


def load(path:Path,default): return json.loads(path.read_text()) if path.exists() else default

def main()->int:
    if not MATRIX.exists(): raise SystemExit('Run tools/build_maximum_sandbox_matrix.py first')
    matrix=load(MATRIX,{})
    evidence_doc=load(EVIDENCE,{'evidence':[],'truth_rule':'No evidence registry found.'})
    fleet=load(FLEET_E2E,{'summary':{},'profiles':[]})
    workers={w['worker_id']:w for w in matrix.get('workers',[])}
    evidence=evidence_doc.get('evidence',[])
    counts=Counter(row.get('status') for row in evidence)
    explicit_pass={row.get('worker_id') for row in evidence if row.get('status')=='passed' and row.get('worker_id') in workers}
    canonical={w['worker_id'] for w in workers.values() if w.get('worker_type')=='canonical_bot'}
    fleet_pass={p.get('slug') for p in fleet.get('profiles',[]) if p.get('status')=='sandbox_certified' and p.get('capabilityTestsFailed',0)==0}
    canonical_with_pass=canonical & (explicit_pass | fleet_pass)
    summary=fleet.get('summary',{})
    fleet_contract_ok=bool(
        summary.get('repositoryControlledFlowComplete') is True
        and summary.get('allDeclaredCapabilitiesTested') is True
        and summary.get('failed',0)==0
        and summary.get('sandboxCapabilityTestsFailed',0)==0
    )
    payload={
      'schema':'dreamco.maximum_sandbox_runtime_audit.v2',
      'planned_worker_count':len(workers),
      'explicit_evidence_record_count':len(evidence),
      'explicit_status_counts':dict(counts),
      'fleet_e2e_profile_count':len(fleet.get('profiles',[])),
      'fleet_e2e_contract_ok':fleet_contract_ok,
      'canonical_worker_count':len(canonical),
      'canonical_workers_with_pass_evidence':len(canonical_with_pass),
      'canonical_worker_runtime_coverage_percent':round((len(canonical_with_pass)/len(canonical))*100,2) if canonical else 0,
      'all_canonical_workers_have_runtime_evidence':bool(canonical) and canonical==canonical_with_pass and fleet_contract_ok,
      'noncanonical_workers_requiring_explicit_evidence':sum(1 for w in workers.values() if w.get('worker_type')!='canonical_bot'),
      'failed_evidence_count':counts.get('failed',0),
      'blocked_evidence_count':counts.get('blocked',0),
      'evidence_sources':['website/data/bot-fleet-e2e.json','config/sandbox-runtime-evidence.json'],
      'truth_boundary':'Canonical fleet E2E evidence may be inherited because it executes repository-controlled bot/capability sandbox contracts. Legacy/job/task workers still need explicit runtime evidence; planned coverage is not a pass.'
    }
    OUT.parent.mkdir(parents=True,exist_ok=True); OUT.write_text(json.dumps(payload,indent=2)+'\n')
    print(json.dumps(payload,indent=2)); return 0

if __name__=='__main__': raise SystemExit(main())
