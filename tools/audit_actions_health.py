#!/usr/bin/env python3
from __future__ import annotations
import json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
WORKFLOWS=ROOT/'.github'/'workflows'
OUT_JSON=ROOT/'config'/'generated'/'actions-health-report.json'
OUT_MD=ROOT/'reports'/'ACTIONS_HEALTH_REPORT.md'
PUBLIC_JSON=ROOT/'website'/'data'/'actions-health-report.json'
PACKAGE=json.loads((ROOT/'package.json').read_text())
SCRIPTS=set(PACKAGE.get('scripts',{}))
# MAX_MAJOR is the preferred/recommended baseline.  MIN_MAJOR prevents genuinely
# obsolete action releases from passing.  A workflow being one major behind the
# recommendation is maintenance debt, not a broken workflow, so it must not turn
# the entire Actions page red when the action is still supported and executes.
MAX_MAJOR={'actions/checkout':7,'actions/setup-node':7,'actions/setup-python':7,'actions/upload-artifact':6,'actions/configure-pages':6,'actions/upload-pages-artifact':5,'actions/deploy-pages':5}
MIN_MAJOR={'actions/checkout':4,'actions/setup-node':4,'actions/setup-python':5,'actions/upload-artifact':4,'actions/configure-pages':5,'actions/upload-pages-artifact':4,'actions/deploy-pages':4}
USES_RE=re.compile(r'uses:\s*([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)@v(\d+)')
NPM_RE=re.compile(r'npm\s+run\s+([A-Za-z0-9:_-]+)')
PATH_CMD_RE=re.compile(r'(?:python3|python|node|tsx|npx\s+tsx)\s+((?:tools|script|scripts|tests)/[^\s\'\"|&;]+)')
TRIGGERS=[('manual',r'^\s+workflow_dispatch\s*:'),('push',r'^\s+push\s*:'),('pull request',r'^\s+pull_request(?:_target)?\s*:'),('schedule',r'^\s+schedule\s*:'),('issues',r'^\s+issues\s*:'),('workflow completion',r'^\s+workflow_run\s*:')]

def main()->int:
    workflows=sorted(WORKFLOWS.glob('*.yml'))+sorted(WORKFLOWS.glob('*.yaml'))
    findings=[]; critical=0
    for path in workflows:
        text=path.read_text(encoding='utf-8'); filename=path.name
        triggers=[name for name,pat in TRIGGERS if re.search(pat,text,re.M)]
        if not triggers and re.search(r'^on\s*:\s*$', text, re.M): triggers=['declared']
        errors=[]; warnings=[]; actions=[]; upgrades=[]
        if 'jobs:' not in text: errors.append('missing jobs section')
        if not triggers: errors.append('no recognizable trigger')
        for action,major_s in USES_RE.findall(text):
            major=int(major_s); actions.append(f'{action}@v{major}')
            allowed=MAX_MAJOR.get(action); minimum=MIN_MAJOR.get(action)
            if minimum is not None and major < minimum:
                errors.append(f'obsolete action major: {action}@v{major}; minimum supported major is v{minimum}')
            elif allowed is not None and major < allowed:
                upgrades.append(f'upgrade recommendation: {action}@v{major} -> v{allowed}')
        npm=sorted(set(NPM_RE.findall(text)))
        for script in npm:
            if script not in SCRIPTS: errors.append(f'missing npm script: {script}')
        refs=sorted({v.rstrip('),]') for v in PATH_CMD_RE.findall(text)})
        for ref in refs:
            if not (ROOT/ref).exists(): errors.append(f'missing referenced file: {ref}')
        critical += len(errors)
        findings.append({'workflow':str(path.relative_to(ROOT)),'filename':filename,'display_name':filename.removesuffix('.yml').removesuffix('.yaml').replace('-',' ').title(),'purpose':'Governed DreamCo workflow with evidence-backed execution.','triggers':triggers,'errors':errors,'warnings':warnings,'actions':actions,'npm_scripts':npm,'referenced_files':refs,'controls':{'permissions_declared':bool(re.search(r'^permissions\s*:',text,re.M)),'concurrency_declared':bool(re.search(r'^concurrency\s*:',text,re.M)),'job_timeouts_declared':len(re.findall(r'^\s+timeout-minutes\s*:',text,re.M)),'runner_jobs':len(re.findall(r'^\s+runs-on\s*:',text,re.M)),'artifacts_declared':'actions/upload-artifact@' in text or 'actions/upload-pages-artifact@' in text},'upgrades':['Publish machine-readable evidence for every run.','Keep external writes behind explicit authorization and bounded policy.','Preserve failures and regressions instead of converting unknown states into passes.'] + upgrades,'github_url':f'https://github.com/DreamCo-Technologies/Dreamcobots/actions/workflows/{filename}','static_status':'blocked' if errors else 'static_checks_passed','maintenance_status':'recommended_upgrade' if upgrades else 'current_baseline'})
    payload={'schema':'dreamco.actions_health.v1','workflow_count':len(workflows),'critical_error_count':critical,'warning_count':0,'operational_workflow_count':0,'live_evidence_note':'Static checks do not prove runtime operation; successful GitHub Actions runs provide operational evidence.','baseline':{'checkout':'actions/checkout@v7','setup_node':'actions/setup-node@v7','setup_python':'actions/setup-python@v7','upload_artifact':'actions/upload-artifact@v6','configure_pages':'actions/configure-pages@v6','upload_pages_artifact':'actions/upload-pages-artifact@v5','deploy_pages':'actions/deploy-pages@v5'},'supported_minimums':{k:f'{k}@v{v}' for k,v in MIN_MAJOR.items()},'findings':findings,'truth_boundary':'Static workflow health distinguishes supported action versions from upgrade recommendations. Runtime success must be established by GitHub Actions execution evidence.'}
    for p in (OUT_JSON,PUBLIC_JSON): p.parent.mkdir(parents=True,exist_ok=True); p.write_text(json.dumps(payload,indent=2)+'\n')
    OUT_MD.parent.mkdir(parents=True,exist_ok=True)
    lines=['# GitHub Actions Health Report','',f'Workflows scanned: **{len(workflows)}**',f'Critical errors: **{critical}**','Warnings: **0**','']
    for item in findings:
        lines.append(f"## {item['workflow']}")
        lines.append('- ✅ No static problems found.' if not item['errors'] else '\n'.join(f'- ❌ {e}' for e in item['errors']))
        if item['maintenance_status']=='recommended_upgrade': lines.append('- ℹ️ Supported version; upgrade recommended when convenient.')
        lines.append('')
    OUT_MD.write_text('\n'.join(lines))
    print(json.dumps({'ok':critical==0,'workflows':len(workflows),'critical_errors':critical,'warnings':0,'report':str(OUT_MD.relative_to(ROOT))},indent=2))
    return 0 if critical==0 else 1
if __name__=='__main__': raise SystemExit(main())