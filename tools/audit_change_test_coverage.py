#!/usr/bin/env python3
from __future__ import annotations

import argparse, json, subprocess
from datetime import date
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
POLICY=json.loads((ROOT/'config/change-impact-test-policy.json').read_text())
EXEMPT=json.loads((ROOT/'config/change-impact-test-exemptions.json').read_text()).get('exemptions',[])
OUT=ROOT/'config/generated/change-impact-test-coverage.json'

def git_diff(base,head):
    p=subprocess.run(['git','diff','--name-only',base,head],cwd=ROOT,capture_output=True,text=True)
    if p.returncode: raise SystemExit(p.stderr)
    return [x.strip() for x in p.stdout.splitlines() if x.strip()]

def valid_exemption(path):
    for row in EXEMPT:
        if row.get('path')==path and row.get('reason') and row.get('owner') and row.get('expires','')>=date.today().isoformat(): return row
    return None

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--base',required=True); ap.add_argument('--head',required=True); args=ap.parse_args()
    changed=git_diff(args.base,args.head)
    exts=set(POLICY['executable_extensions']); tests=[p for p in changed if any(p.startswith(x) for x in POLICY['test_paths'])]
    executable=[p for p in changed if Path(p).suffix in exts and not any(p.startswith(x) for x in POLICY['test_paths'])]
    high_words=[x.lower() for x in POLICY['high_risk_path_keywords']]
    rows=[]; blockers=[]
    for path in executable:
        lower=path.lower(); high=any(k in lower for k in high_words); shared=any(path.startswith(x) for x in POLICY['shared_core_prefixes'])
        exemption=valid_exemption(path)
        evidence=[]
        if tests: evidence.append('changed_test_file')
        if shared: evidence.append('broad_repository_verification_required')
        if high: evidence += ['negative_security_integration_evidence_required','rollback_review_when_applicable']
        ok=bool(tests or exemption)
        if not ok: blockers.append(f'{path}: no changed test evidence or valid exemption')
        rows.append({'path':path,'risk':'high' if high else 'normal','shared_core':shared,'evidence':evidence,'exemption':exemption,'covered':ok})
    payload={'schema':'dreamco.change_impact_test_coverage.v1','base':args.base,'head':args.head,'changed_file_count':len(changed),'changed_test_file_count':len(tests),'changed_executable_file_count':len(executable),'files':rows,'release_blockers':blockers,'ok':not blockers,'truth_boundary':POLICY['truth_rule']}
    OUT.parent.mkdir(parents=True,exist_ok=True); OUT.write_text(json.dumps(payload,indent=2)+'\n')
    print(json.dumps({'ok':not blockers,'changed':len(changed),'executable':len(executable),'tests':len(tests),'blockers':blockers},indent=2))
    return 0 if not blockers else 1

if __name__=='__main__': raise SystemExit(main())
