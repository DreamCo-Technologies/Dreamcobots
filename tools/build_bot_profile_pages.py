#!/usr/bin/env python3
"""Build dedicated intake pages from current bot sources, preserving provenance."""
import argparse, hashlib, html, json, re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
WEB=ROOT/'website'
def profiles():
 catalog=json.loads((WEB/'data/bot-fleet-catalog.json').read_text());verified={b['identity']['slug']:b for b in catalog['bots']};rows={}
 def add(slug,name,division,mission,caps,source,kind):
  slug=re.sub(r'[^a-z0-9-]+','-',slug.lower()).strip('-')
  if not slug:return
  if slug in rows:
   if source not in rows[slug]['sources']:rows[slug]['sources'].append(source)
   return
  rows[slug]={'slug':slug,'name':name,'division':division,'mission':mission,'capabilities':caps or ['Scope clarification'],'sources':[source],'kind':kind,'routeRegistered':slug in verified,'productionReady':False,'accent':'#'+hashlib.sha256(slug.encode()).hexdigest()[:6]}
 for path in sorted((ROOT/'App_bots').glob('*.json')):
  data=json.loads(path.read_text())
  for b in data.get('bots',[]):add(b['slug'],b.get('displayName',b['slug']),data.get('division','Unassigned'),b.get('description','Purpose needs clarification from the source owner.'),b.get('capabilities',[]),path.relative_to(ROOT).as_posix(),'division_profile')
 # The master registry explicitly owns 65 coordinating roles outside the fleet.
 data=json.loads((ROOT/'config/masterbot-65-registry.json').read_text())
 for b in data['divisions']:
  division=b['name'];caps=sorted({c for p in rows.values() if p['division']==division for c in p['capabilities']})[:8]
  add('master-'+division,division+' MasterBot',division,'Coordinate the '+division+' domain under the repository masterbot ownership policy.',caps or ['Define domain scope','Coordinate specialist handoffs','Review capability evidence'],'config/masterbot-65-registry.json','master_role')
 # Markdown catalogs are additional specifications, not automatically live services.
 from tools.compile_md_bots import parse_md
 for path in sorted((ROOT/'bots').glob('*.md')):
  spec=parse_md(path)
  if spec:add(spec['slug'],spec['display_name'],spec['division'],spec['mission'],spec['capabilities'],path.relative_to(ROOT).as_posix(),'markdown_spec')
 data=json.loads((ROOT/'money_os/config/bot_registry.json').read_text())
 for b in data.get('bots',[]):
  name=Path(b['path']).name;add(name,name.replace('_',' ').replace('-',' ').title(),'Money OS', 'Registered '+b['lane'].replace('_',' ')+' role; referenced implementation must be verified.',[b['lane'].replace('_',' ')], 'money_os/config/bot_registry.json','legacy_reference')
 for b in data.get('new_money_os_bots',[]):
  add(b['name'],b['name'].replace('_',' ').title(),'Money OS','Proposed '+b['lane'].replace('_',' ')+' role in the Money OS registry.',[b['lane'].replace('_',' ')],'money_os/config/bot_registry.json','proposed_role')
 return sorted(rows.values(),key=lambda p:(p['name'].lower(),p['slug']))
def build(check=False):
 rows=profiles();target=WEB/'bot-pages';target.mkdir(exist_ok=True);errors=[];expected=set()
 for b in rows:
  name=html.escape(b['name']);mission=html.escape(b['mission']);slug=b['slug'];expected.add(slug+'.html')
  text=f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{name} — DreamCo AI Specialist</title><meta name="description" content="Explore {name}, its source-backed scope, and 30 tailored intake questions."><link rel="icon" href="../assets/images/command-center.svg"><link rel="stylesheet" href="../command-center.css"><link rel="stylesheet" href="../bot-profile.css"><script type="module" src="../bot-profile.js"></script></head><body data-bot="{slug}"><main class="bot-profile-shell"><nav class="profile-nav"><a href="../command-center.html">DreamCo / Inventions Hub</a><a href="../bot-directory.html">All AI specialists</a><a href="../grok-buddy-playbook.html">Grok + Buddy</a></nav><header class="profile-hero"><p class="eyebrow">{html.escape(b['division'])} / AI SPECIALIST INTAKE</p><h1>{name}</h1><p>{mission}</p></header><div id="profile-app"><p role="status">Loading this specialist's 30-question intake…</p><noscript>JavaScript is required for interactive intake. The source description above remains available.</noscript></div></main></body></html>\n'''
  path=target/(slug+'.html')
  if check:
   if not path.exists() or path.read_text()!=text:errors.append(str(path.relative_to(ROOT)))
  else:path.write_text(text)
 payload={'schema':'dreamco.bot_intake_profiles.v1','profiles':rows,'coverage':{'profileCount':len(rows),'registeredFleetRoutes':sum(p['routeRegistered'] for p in rows),'questionsPerProfile':30,'sourceFamilies':['App_bots/*.json','config/masterbot-65-registry.json','bots/*.md','money_os/config/bot_registry.json']},'truth':'Intake pages and declared roles are not proof of live AI execution. Unknown implementations remain unverified.'}
 path=WEB/'data/bot-intake-profiles.json';text=json.dumps(payload,ensure_ascii=False,separators=(',',':'))+'\n'
 if check:
  if not path.exists() or path.read_text()!=text:errors.append(str(path.relative_to(ROOT)))
  extras={p.name for p in target.glob('*.html')}-expected
  if extras:errors.append('Unexpected generated profile pages: '+', '.join(sorted(extras)))
 else:path.write_text(text)
 if errors:raise SystemExit('\n'.join(errors[:20]))
 print(json.dumps(payload['coverage']))
if __name__=='__main__':
 import sys
 sys.path.insert(0,str(ROOT))
 parser=argparse.ArgumentParser();parser.add_argument('--check',action='store_true');build(parser.parse_args().check)
