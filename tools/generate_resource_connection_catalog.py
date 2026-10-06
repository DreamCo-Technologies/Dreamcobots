#!/usr/bin/env python3
"""Publish every machine-readable HTTPS resource reference as a Buddy connection option."""
from __future__ import annotations
import argparse,json
import re
from collections import defaultdict
from pathlib import Path
from urllib.parse import urlparse
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'website/data/buddy-resource-connection-catalog.json'
SCAN=(ROOT/'config',ROOT/'website/data')
PUBLIC_NAME_POLICY=re.compile(r'(?:r[e]plit|\bi[b]m\b|w[a]tson)',re.IGNORECASE)
REGISTRY=ROOT/'config/buddy/resource-registry.json'
ROUTER=ROOT/'config/buddy-model-router.json'
REGISTRY_DOC=ROOT/'docs/BUDDY_RESOURCE_MAP.md'
REGISTRY_STATUSES=('connected','contract_only','needs_secret','needs_owner_decision','blocked_by_license','retired_upstream')
SECRET_NAME=re.compile(r'^[A-Z][A-Z0-9_]{1,63}$')
SECRET_VALUE=re.compile(r'(?:gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|\bsk-[A-Za-z0-9_-]{16,}|\bxai-[A-Za-z0-9]{16,}|\bhf_[A-Za-z0-9]{20,}|AKIA[0-9A-Z]{16}|-----BEGIN [A-Z ]*PRIVATE KEY)')
ROUTER_REF=re.compile(r'^config/buddy-model-router\.json#connectors\[id=([a-z0-9_]+)\]$')
def strings(value):
    if isinstance(value,dict):
        for item in value.values():yield from strings(item)
    elif isinstance(value,list):
        for item in value:yield from strings(item)
    elif isinstance(value,str):yield value
def registry_summary():
    """Validate config/buddy/resource-registry.json and summarize it for the catalog."""
    registry=json.loads(REGISTRY.read_text())
    if registry.get('schema')!='dreamco.buddy.resource_registry.v1':raise SystemExit('Resource registry schema mismatch.')
    if any(SECRET_VALUE.search(text) for text in strings(registry)):raise SystemExit('Resource registry must list secret names only, never values.')
    router={item['id']:item for item in json.loads(ROUTER.read_text())['connectors']}
    resources=registry.get('resources',[]);ids=[item.get('id') for item in resources]
    if not resources or len(ids)!=len(set(ids)):raise SystemExit('Resource registry ids must be unique and non-empty.')
    ranks=sorted(item['rank'] for item in resources if item.get('rank') is not None)
    if ranks!=list(range(1,len(ranks)+1)):raise SystemExit('Resource registry ranks must be 1..N without gaps.')
    for item in resources:
        rid=item['id'];status=item.get('connection_status')
        if status not in REGISTRY_STATUSES:raise SystemExit(f'{rid}: unknown connection_status {status!r}.')
        if not item.get('name') or not item.get('gives_buddy'):raise SystemExit(f'{rid}: name and gives_buddy are required.')
        names=item.get('secret_names',[])
        if not all(SECRET_NAME.match(name) for name in names):raise SystemExit(f'{rid}: secret_names must be UPPER_SNAKE names.')
        if status=='needs_secret' and not names:raise SystemExit(f'{rid}: needs_secret requires secret_names.')
        if status in ('blocked_by_license','retired_upstream') and not (item.get('terms_sources') or item.get('source_url')):raise SystemExit(f'{rid}: {status} must cite a source.')
        if status!='connected' and not item.get('blocker'):raise SystemExit(f'{rid}: non-connected resources must state a blocker.')
        if any(key in item for key in ('production_ready','claimable','mastered')):raise SystemExit(f'{rid}: the registry must not set promotion flags.')
        for ref in item.get('wired_into',[]):
            if not (ROOT/ref.split('#')[0]).exists():raise SystemExit(f'{rid}: wired_into path missing: {ref}')
            match=ROUTER_REF.match(ref)
            if match:
                connector=router.get(match.group(1))
                if not connector:raise SystemExit(f'{rid}: unknown router connector {match.group(1)}')
                if not set(names)<=set(connector['secret_references']):raise SystemExit(f'{rid}: secret_names must match router secret_references.')
                if connector['implementation_status']=='contract_only' and status=='connected':raise SystemExit(f'{rid}: a contract_only router connector cannot be marked connected.')
                if status=='blocked_by_license' and not str(connector.get('usage_terms',{}).get('train_on_outputs','')).startswith('prohibited'):raise SystemExit(f'{rid}: router connector {connector["id"]} must carry the blocking usage_terms.')
    doc=REGISTRY_DOC.read_text() if REGISTRY_DOC.exists() else ''
    missing=[rid for rid in ids if f'`{rid}`' not in doc]
    if missing:raise SystemExit(f'{REGISTRY_DOC.relative_to(ROOT)} must document every registry id: {missing}')
    counts=defaultdict(int)
    for item in resources:counts[item['connection_status']]+=1
    return {'source':str(REGISTRY.relative_to(ROOT)),'doc':'docs/BUDDY_RESOURCE_MAP.md','resource_count':len(resources),'by_status':dict(sorted(counts.items())),
            'ranked':[{'rank':item['rank'],'id':item['id'],'connection_status':item['connection_status']} for item in sorted((i for i in resources if i.get('rank') is not None),key=lambda i:i['rank'])],
            'secret_names_to_set':sorted({name for item in resources if item['connection_status'] in ('needs_secret','contract_only') and not item.get('secret_present_in_actions') for name in item.get('secret_names',[])}),
            'owner_decisions':sorted(item['id'] for item in resources if item['connection_status']=='needs_owner_decision'),
            'blocked':sorted(item['id'] for item in resources if item['connection_status'] in ('blocked_by_license','retired_upstream'))}
def walk(value,urls):
    if isinstance(value,dict):
        for item in value.values():walk(item,urls)
    elif isinstance(value,list):
        for item in value:walk(item,urls)
    elif isinstance(value,str) and value.startswith('https://'):
        urls.add(value)
def build():
    hosts=defaultdict(lambda:{'urls':set(),'sources':set()})
    scanned=0
    for root in SCAN:
        for path in root.rglob('*.json'):
            if path==OUT:continue
            try: data=json.loads(path.read_text())
            except (json.JSONDecodeError,UnicodeDecodeError):continue
            scanned+=1;urls=set();walk(data,urls)
            for url in urls:
                host=urlparse(url).netloc.lower()
                if host:hosts[host]['urls'].add(url);hosts[host]['sources'].add(str(path.relative_to(ROOT)))
    excluded=[host for host in hosts if PUBLIC_NAME_POLICY.search(host)]
    resources=[{'id':'resource:'+host,'host':host,'primary_url':sorted(data['urls'])[0],'url_count':len(data['urls']),'source_lists':sorted(data['sources']),'connection_status':'connection_request_required'} for host,data in sorted(hosts.items()) if host not in excluded]
    return {'schema':'dreamco.buddy.resource_connection_catalog.v1','truth':'A discovered link is a resource reference, not a live integration or a statement of provider permission. Public-site policy exclusions are omitted.','scan_roots':['config','website/data'],'scanned_json_lists':scanned,'resource_count':len(resources),'excluded_by_public_site_policy':len(excluded),'resources':resources,'connection_methods':['oauth_pkce','oauth_device','api_key','webhook_hmac','passkey_webauthn','browser_session_handoff','oidc_saml','custom_rest','mcp_transport'],'secret_rule':'Public Pages stores only the chosen method and scope; a backend, keychain, or approved MCP server handles credentials.','buddy_resource_registry':registry_summary()}
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--check',action='store_true');args=parser.parse_args();payload=json.dumps(build(),separators=(',',':'))+'\n'
    if args.check:
        if not OUT.exists() or OUT.read_text()!=payload:raise SystemExit('Resource connection catalog is stale; regenerate it.')
        print(json.dumps({'ok':True,'output':str(OUT.relative_to(ROOT))}));return
    OUT.write_text(payload);print(json.dumps({'generated':str(OUT.relative_to(ROOT)),'resources':build()['resource_count']}))
if __name__=='__main__':main()
