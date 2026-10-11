#!/usr/bin/env python3
"""Read-only repository inventory and division-sized implementation handoff."""
import argparse
import ast
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import re
import subprocess

ROOT=Path(__file__).resolve().parents[1]

def build(out, evidence=None):
    out=Path(out).resolve();out.mkdir(parents=True,exist_ok=True)
    cross=json.loads((ROOT/'config/generated/superbot-crosswalk.json').read_text())
    before=set(subprocess.check_output(['git','ls-tree','-r','--name-only','HEAD'],cwd=ROOT,text=True).splitlines())
    paths=sorted(set(subprocess.check_output(['git','ls-files','--cached','--others','--exclude-standard'],cwd=ROOT,text=True).splitlines()))
    changed=set(subprocess.check_output(['git','diff','HEAD','--name-only'],cwd=ROOT,text=True).splitlines())
    results={r['bot']:r for r in (json.loads(Path(evidence).read_text())['results'] if evidence else [])}
    owners=defaultdict(set)
    for category in ['proposals','bots','legacy']:
        for row in cross[category]:
            for ref in row['source_refs']:owners[ref.split('#')[0]].add(row['primary_owner'])
    inventory=[]
    for name in paths:
        p=ROOT/name
        if not p.is_file():continue
        raw=p.read_bytes();suffix=p.suffix.lower();text=raw.decode('utf-8',errors='replace')
        syntax='not_checked';findings=[]
        if suffix=='.py':
            try:
                tree=ast.parse(text);syntax='pass'
                for n in ast.walk(tree):
                    if isinstance(n,ast.Raise) and 'NotImplementedError' in ast.dump(n):findings.append({'line':n.lineno,'kind':'explicit_unimplemented_path'})
            except SyntaxError as e:syntax='error';findings.append({'line':e.lineno,'kind':'syntax_error','detail':str(e)})
        if suffix=='.json':
            try:json.loads(text);syntax='pass'
            except ValueError as e:syntax='error';findings.append({'kind':'json_error','detail':str(e)})
        for line,body in enumerate(text.splitlines(),1):
            if re.search(r'\b(?:TODO|FIXME)\b',body):findings.append({'line':line,'kind':'review_marker','detail':body.strip()[:200]})
        code=suffix in {'.py','.js','.mjs','.cjs','.ts','.tsx','.jsx','.sh','.html'}
        inventory.append({'path':name,'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw),
            'comparison':'added' if name not in before else 'modified' if name in changed else 'pre_existing',
            'kind':'code_or_page' if code else 'data_documentation_or_asset','syntax':syntax,
            'owners':sorted(owners[name]),'findings':findings,
            'verification':'Static inventory only; markers are review leads, not proof of defects. Documents and data do not require executable code.'})
    packets=defaultdict(list)
    for category in ['proposals','bots','legacy']:
        for row in cross[category]:
            record={'catalog':category,**row,'local_shared_engine_evidence':results.get(row['id']),
                'inspect_files':list(dict.fromkeys([r.split('#')[0] for r in row['source_refs']]+['buddy/fleet_runtime/executor.py','buddy/fleet_runtime/engines.py','server/superbot-systems.ts'])),
                'next_steps':(['Recover original name and full capability description with provenance; do not invent it.'] if row['source_status']!='recovered' else [
                    'Read the preserved source and every listed capability; select one capability for this change.',
                    'Inspect candidate bots and existing shared engines for reusable code; preserve stable IDs.',
                    'Define inputs, outputs, failure cases and an independent acceptance fixture for the selected capability.',
                    'Implement missing specialist behavior behind the existing permission and run-policy gates.',
                    'Add meaningful success, invalid-input and denied-action tests; record exact commands and results.',
                    'Connect the implemented capability to its primary owner and Pages control only after tests pass.']),
                'acceptance':['No unsupported operational or domain-accuracy claim.','No secret embedded in browser code.','Blocked money/destructive policies remain enforced.','External integrations require configured credentials and separately verified behavior.']}
            packets[row['primary_owner']].append(record)
    for owner,records in packets.items():(out/(owner+'.json')).write_text(json.dumps(records,indent=2)+'\n')
    (out/'FILE_INVENTORY.json').write_text(json.dumps(inventory,indent=2)+'\n')
    summary={'base_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'files':len(inventory),'comparison':dict(Counter(r['comparison'] for r in inventory)), 'syntax_errors':[r['path'] for r in inventory if r['syntax']=='error'],'files_with_review_findings':sum(bool(r['findings']) for r in inventory),'catalog':cross['summary'],'division_packets':{k:len(v) for k,v in sorted(packets.items())}}
    (out/'INDEX.json').write_text(json.dumps(summary,indent=2)+'\n')
    (out/'START_HERE.md').write_text('''# DreamCo implementation handoff

Read INDEX.json first, then only the relevant division packet. Every packet preserves the source, capability list, existing candidates, ownership, local shared-engine evidence, file paths, next steps and acceptance criteria. FILE_INVENTORY.json compares all files to the inspected base commit; documents and configurations are not missing code merely because they are not executable.

Priority order:
1. Recover the 166 missing and 8 partial original proposal descriptions; never fill gaps with fabricated historical proposals.
2. Review the 90 blocked fleet results. Implement missing engines/fixtures where appropriate; do not remove money/destructive restrictions to improve counts.
3. Implement one independently testable specialist capability at a time using the division packets. Shared-engine checks are not specialist benchmarks.
4. Review SCAN_REPORT.json dependency review items and FILE_INVENTORY.json explicit unimplemented paths/markers; distinguish intentional abstract methods and examples from defects.
5. Validate providers using configured test accounts, required hardware and independent domain data. Medical/scientific claims need qualified validation beyond generic bot fixtures.
6. Run the committed tests, publish the reviewed branch, and verify the new Actions jobs and Pages buttons on GitHub. Local results do not prove hosted capacity or deployment.

Do not repeat the whole repository scan for every bot. Work in a small division batch and update evidence only for changed capabilities. Preserve existing readiness states until the corresponding evidence gates pass.
''')
    return summary

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--out',required=True);p.add_argument('--evidence');a=p.parse_args();print(json.dumps(build(a.out,a.evidence),indent=2))
