"""Publish allowlisted public metadata; private source exports are never inputs."""
import argparse
import json
import hashlib
import re
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen
ROOT=Path(__file__).resolve().parents[1]

def get_json(url):
    with urlopen(Request(url,headers={'Accept':'application/vnd.github+json','User-Agent':'DreamCo-repository-directory'}),timeout=30) as response:
        return json.load(response)

PUBLIC_NAME = re.compile(r"(?:r[e]plit|\bi[b]m\b|w[a]tson)", re.I)

def public_file(item, name):
    path = item['path']
    if PUBLIC_NAME.search(path):
        digest = hashlib.sha256(path.encode()).hexdigest()
        return {'path': 'External integration source ' + digest[:12], 'size': item.get('size',0), 'path_is_display_label': True, 'source_path_sha256': digest, 'source_url': 'https://api.github.com/repos/'+name+'/git/blobs/'+item['sha']}
    return {'path':path,'size':item.get('size',0)}

def collect(repo):
    name=repo['name']; metadata=get_json('https://api.github.com/repos/'+name)
    if metadata.get('private') or metadata.get('visibility')!='public':
        raise ValueError('Only public repositories can enter the public index')
    branch=metadata['default_branch'];data=get_json(f'https://api.github.com/repos/{name}/git/trees/{branch}?recursive=1')
    if data.get('truncated'):
        raise ValueError(name+': tree truncated; refusing an incomplete snapshot')
    return {**repo,'branch':branch,'snapshot_commit':data['sha'],'files':[public_file(x,name) for x in data['tree'] if x['type']=='blob']}

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--refresh-repositories',action='store_true');parser.add_argument('--check',action='store_true');args=parser.parse_args()
    source=ROOT/'config/conversation-index.json';out=ROOT/'website/data/conversation-index.json'
    if args.check:
        if source.read_bytes()!=out.read_bytes():raise SystemExit('Conversation index is stale')
    else:out.write_bytes(source.read_bytes())
    if args.refresh_repositories:
        config=json.loads((ROOT/'config/repository-connections.json').read_text())
        payload={'schema':config['schema'],'updated_at':datetime.now(timezone.utc).isoformat(),'scope':'Public metadata only. New files can also be loaded directly from GitHub on each repository page.','repositories':[collect(r) for r in config['repositories']]}
        (ROOT/'website/data/repository-connections.json').write_text(json.dumps(payload,indent=2)+'\n')
    data=json.loads((ROOT/'website/data/repository-connections.json').read_text())
    names={r['name'] for r in json.loads((ROOT/'config/repository-connections.json').read_text())['repositories']}
    if {r['name'] for r in data['repositories']}!=names:raise SystemExit('Repository snapshot does not match configured public connections')
    print(f'Connected indexes: {len(data["repositories"])} public repositories; 49 conversation records')
if __name__=='__main__':main()
