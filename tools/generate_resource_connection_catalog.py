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
    return {'schema':'dreamco.buddy.resource_connection_catalog.v1','truth':'A discovered link is a resource reference, not a live integration or a statement of provider permission. Public-site policy exclusions are omitted.','scan_roots':['config','website/data'],'scanned_json_lists':scanned,'resource_count':len(resources),'excluded_by_public_site_policy':len(excluded),'resources':resources,'connection_methods':['oauth_pkce','oauth_device','api_key','webhook_hmac','passkey_webauthn','browser_session_handoff','oidc_saml','custom_rest','mcp_transport'],'secret_rule':'Public Pages stores only the chosen method and scope; a backend, keychain, or approved MCP server handles credentials.'}
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--check',action='store_true');args=parser.parse_args();payload=json.dumps(build(),indent=2)+'\n'
    if args.check:
        if not OUT.exists() or OUT.read_text()!=payload:raise SystemExit('Resource connection catalog is stale; regenerate it.')
        print(json.dumps({'ok':True,'output':str(OUT.relative_to(ROOT))}));return
    OUT.write_text(payload);print(json.dumps({'generated':str(OUT.relative_to(ROOT)),'resources':build()['resource_count']}))
if __name__=='__main__':main()
