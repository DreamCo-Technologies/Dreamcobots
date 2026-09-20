#!/usr/bin/env python3
"""Generate lightweight invention-hub catalogs; preserve every existing page."""
import argparse, hashlib, html, json, re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
WEB=ROOT/'website'
OWNER={'actions','master-build','buddy-operating-system','autonomy','orchestration','connections','data-control','costs','revenue','settings','debug','timecapsule','system-map','test-center','benchmark-tracker','open-model-lab','security','dashboard','models','platform','ecosystem','leaders','branch-health','ops','command','wiring','connect-desk','resource-connection-center','system-progress','buddy-command-center'}
def payloads():
 source=WEB/'data/bot-fleet-catalog.json'; raw=source.read_bytes(); catalog=json.loads(raw)
 bots=[{'slug':b['identity']['slug'],'name':b['identity']['display_name'],'division':b['identity']['division'],'category':b['identity']['category'],'tier':b['identity']['tier'],'mission':b['mission'],'capabilities':b['capability_search'].split(' | '),'source':b['evidence']['catalog_source'],'productionReady':b['readiness']['production_ready']} for b in catalog['bots']]
 bots.sort(key=lambda b:(0 if b['slug']=='buddy-bot' else 1,b['name'].lower()))
 compact={'summary':catalog['summary'],'divisions':catalog['divisions'],'bots':bots,'source':{'repository':'DreamCo-Technologies/Dreamcobots','path':'website/data/bot-fleet-catalog.json','catalogSha256':hashlib.sha256(raw).hexdigest()}}
 features=[]
 for p in sorted(WEB.glob('*.html')):
  if p.stem in {'index','404','command-center'}:continue
  s=p.read_text();m=re.search(r'<title>(.*?)</title>',s,re.S|re.I);title=html.unescape(m[1]) if m else p.stem.replace('-',' ').title();title=re.split(r'\s+[—–|]\s+',title)[0].replace('DreamCo Empire OS - ','');d=re.search(r'<meta\s+name=["\']description["\']\s+content=["\'](.*?)["\']',s,re.I)
  features.append({'href':p.name,'name':title,'area':'owner' if p.stem in OWNER else 'user','description':html.unescape(d[1])[:190] if d else 'Open the existing '+title+' workspace and its tools.'})
 return {'command-center-catalog.json':compact,'command-center-features.json':{'schema':'dreamco.command_center_features.v1','features':features}}
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--check',action='store_true');args=ap.parse_args();errors=[]
 for name,data in payloads().items():
  p=WEB/'data'/name;text=json.dumps(data,ensure_ascii=False,separators=(',',':'))+'\n'
  if args.check:
   if not p.exists() or p.read_text()!=text:errors.append(name+' is stale')
  else:p.write_text(text)
 if errors:raise SystemExit('\n'.join(errors))
 print('Inventions hub: canonical catalog and all feature pages accounted for.')
if __name__=='__main__':main()
