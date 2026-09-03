#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
CFG=json.loads((ROOT/'config/live-user-testing-readiness.json').read_text())
CERT=ROOT/'config/generated/full-system-operational-certification.json'
SANDBOX=ROOT/'config/generated/maximum-sandbox-matrix.json'
RUNALL=ROOT/'config/generated/run-everything-now-latest.json'
TRUST=ROOT/'config/generated/trusted-code-delivery-audit.json'
OUT=ROOT/'config/generated/live-user-testing-readiness.json'


def load(path): return json.loads(path.read_text()) if path.exists() else {}


def run_everything_clean(runall):
    results=runall.get('results')
    if isinstance(results, list):
        other_failures=[row for row in results if row.get('name')!='live_user_testing_readiness' and row.get('exit_code',0)!=0]
        return not other_failures
    return runall.get('failed')==0


def main()->int:
    cert=load(CERT); sandbox=load(SANDBOX); runall=load(RUNALL); trust=load(TRUST)
    checks={
      'core_certification':cert.get('core_operational_certified') is True,
      'code_trust':not trust.get('release_blockers',['missing']),
      'maximum_sandbox_generated':sandbox.get('worker_count',0)>0 and sandbox.get('minimum_test_dimensions_per_applicable_case',0)>=10,
      'run_everything_clean':run_everything_clean(runall),
      'production_runtime_smoke':cert.get('checks',{}).get('production_runtime_smoke') is True,
      'speed_accuracy':cert.get('checks',{}).get('speed_accuracy') is True,
      'bot_accounting':cert.get('checks',{}).get('bot_accounting') is True,
    }
    blockers=[name for name,passed in checks.items() if not passed]
    stage='owner_pilot' if not blockers else 'internal_only'
    payload={
      'schema':'dreamco.live_user_testing_readiness.generated.v1','ready':not blockers,'recommended_stage':stage,
      'checks':checks,'blockers':blockers,'rollout_stages':CFG['rollout_stages'],'success_metrics':CFG['success_metrics'],
      'automatic_pause_conditions':CFG['automatic_pause_conditions'],'truth_boundary':CFG['truth_rule']
    }
    OUT.parent.mkdir(parents=True,exist_ok=True); OUT.write_text(json.dumps(payload,indent=2)+'\n')
    print(json.dumps({'ok':not blockers,'stage':stage,'blockers':blockers,'output':str(OUT.relative_to(ROOT))},indent=2)); return 0 if not blockers else 1
if __name__=='__main__': raise SystemExit(main())
