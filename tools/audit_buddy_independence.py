#!/usr/bin/env python3
"""Generate an honest local-first dependency audit for Buddy."""
from __future__ import annotations
import argparse,json
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
REGISTRY=ROOT/'config/buddy-local-first-replacement-registry.json'
CAPABILITIES=ROOT/'website/data/command-center/capabilities.json'
MODELS=ROOT/'config/buddy-model-router.json'
OUT=ROOT/'website/data/buddy-independence-audit.json'
def build():
    registry=json.loads(REGISTRY.read_text()); capabilities=json.loads(CAPABILITIES.read_text()).get('items',[]); models=json.loads(MODELS.read_text()).get('connectors',[])
    return {'schema':'dreamco.buddy.independence_audit.v1','truth':'Cataloged capability records are not proof that each capability is executable or independent.','capabilities':{'total':len(capabilities),'by_status':dict(sorted(Counter(item.get('status','unknown') for item in capabilities).items()))},'model_connectors':{'total':len(models),'by_implementation_status':dict(sorted(Counter(item.get('implementation_status','unknown') for item in models).items()))},'local_replacements':registry['components'],'summary':{'implemented_local_components':sum(item['status']=='implemented' for item in registry['components']),'setup_required_components':sum(item['status']=='setup_required' for item in registry['components']),'external_authority_or_license_required':sum(item['external_required'] for item in registry['components'])},'next_rule':'Do not call the repository fully independent until executable tests and deployment evidence exist for each claimed capability.'}
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--check',action='store_true');args=parser.parse_args();payload=json.dumps(build(),indent=2)+'\n'
    if args.check:
        if not OUT.exists() or OUT.read_text()!=payload:raise SystemExit('Independence audit is stale; regenerate it.')
        print(json.dumps({'ok':True,'output':str(OUT.relative_to(ROOT))}));return
    OUT.write_text(payload);print(json.dumps({'generated':str(OUT.relative_to(ROOT))}))
if __name__=='__main__':main()
