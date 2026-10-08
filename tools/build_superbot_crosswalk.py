#!/usr/bin/env python3
"""Connect proposals and preserved legacy sources to existing owners and planners.

This organizational crosswalk never promotes a claimed capability to implemented.
"""
from __future__ import annotations
import argparse
from collections import Counter
import hashlib
import json
import math
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools.normalize_legacy_portfolios import build_legacy_portfolios, DIVISION_ALIASES
from tools.proposal_registry import validate
from tools.place_original_bots import SYSTEM_DEFAULT

OUTPUT = ROOT / 'config/generated/superbot-crosswalk.json'
PUBLIC = ROOT / 'website/data/superbot-crosswalk.json'
STOP = set('ai bot bots assistant engine intelligence intelligent universal system systems dreamco the and for with from into of a an to research coordinate manage generate'.split())


def tokens(text):
    return set(re.findall(r'[a-z0-9]{3,}', text.casefold())) - STOP


def build(root=ROOT):
    def read(name):
        return json.loads((root/name).read_text())
    registry = validate(read('config/proposals/master-registry.json'))
    routing = read('config/proposals/division-routing.json')
    owners = {d['name'] for d in read('config/masterbot-65-registry.json')['divisions']}
    routes = {d['proposal_division_id']: d for d in routing['divisions']}
    if len(routes) != len(routing['divisions']):
        raise ValueError('Duplicate proposal division ownership')
    if set(routes) - {d['id'] for d in registry['divisions']}:
        raise ValueError('Routing references a nonexistent division')
    for division in registry['divisions']:
        if division['id'] not in routes:
            routes[division['id']] = {'proposal_division_id':division['id'],'source_division_name':division['name'],
                'primary_owner':'DreamDiscovery','collaborators':[], 'status':'classification_required',
                'reason':'New division awaits a domain-owner mapping; do not infer implementation.'}
    for d in routing['divisions']:
        if d['primary_owner'] not in owners or not set(d['collaborators']) <= owners:
            raise ValueError('Unknown canonical owner')
    fleet = read('config/master_bot_registry.json')
    profiles = fleet['bots'] + fleet.get('supplemental_bots', [])
    slugs = {p['identity']['slug'] for p in profiles}
    profile_by_slug = {p['identity']['slug']: p for p in profiles}
    manifests = read('config/bots/bot-manifests.generated.json')['bots']
    legacy = build_legacy_portfolios(root, fleet)
    corpus = [tokens(p['identity']['display_name']+' '+p['prospectus']['mission']+' '+' '.join(c['name'] for c in p['capabilities'])) for p in profiles]
    frequencies = Counter(word for bag in corpus for word in bag)
    aliases = {**DIVISION_ALIASES, 'GrokTeammates': 'DreamAgents', 'UNASSIGNED': 'DreamDiscovery'}

    def normalize(division):
        owner = aliases.get(division, division)
        return owner if owner in owners else 'DreamDiscovery'

    def candidates(name, mission, owner, collaborators):
        wanted = tokens(name+' '+mission)
        ranked = []
        for profile, bag in zip(profiles, corpus):
            division = normalize(profile['identity']['division'])
            # Keep a specialist in the owning domain or an explicitly named collaborator.
            if division not in {owner, *collaborators}:
                continue
            matched = sorted(wanted & bag)
            score = sum(math.log(1+len(profiles)/(1+frequencies[word])) for word in matched)
            if not matched:
                continue
            ranked.append({'slug': profile['identity']['slug'], 'name': profile['identity']['display_name'],
                           'declared_division': profile['identity']['division'], 'score': round(score, 3),
                           'matched_terms': matched, 'reason': 'lexical_reuse_candidate_not_capability_verification'})
        return sorted(ranked, key=lambda item: (-item['score'], item['slug']))[:3]

    proposal_rows = []
    for s in registry['systems']:
        route = routes[s['division_id']]
        candidate = candidates(s['name'] or '', s['purpose'] or '', route['primary_owner'], route['collaborators']) if s['name'] and route['status']!='classification_required' else []
        proposal_rows.append({'id': str(s['id']), 'key': s['key'], 'name': s['name'], 'purpose': s['purpose'],
                             'division_id': s['division_id'], 'primary_owner': route['primary_owner'],
                             'collaborators': route['collaborators'], 'source_status': s['source_status'],
                             'source_refs': ['config/proposals/master-registry.json#'+s['key']],
                             'capabilities': s['capabilities'], 'candidate_bots': candidate,
                             'state': 'source_needed' if s['source_status'] in {'missing','partial'} else 'proposal_only',
                             'capability_verified': False})
    legacy_rows = []
    for bot in legacy['bots']:
        source = bot['evidence']['historical_source']
        division = bot['identity']['division']
        # The curated system-domain map is stronger evidence than incidental words
        # such as "license" buried in a 200-feature historical note.
        if source.startswith('original-bots/systems/'):
            division = SYSTEM_DEFAULT[Path(source).name]
        owner = normalize(division)
        collaborators = [d for d in ('DreamCodeLab','DreamIntegration','DreamQuality') if d != owner]
        caps = [c['name'] for c in bot['capabilities']]
        legacy_rows.append({'id': bot['identity']['slug'], 'name': bot['identity']['display_name'],
                            'purpose': bot['prospectus']['mission'], 'source_refs': [source],
                            'source_status': 'recovered', 'source_index': bot['evidence'].get('source_index'),
                            'declared_division': bot['identity']['division'], 'primary_owner': owner,
                            'collaborators': collaborators, 'capabilities': caps,
                            'exact_catalog_matches': bot['evidence']['canonical_matches'],
                            'candidate_bots': candidates(bot['identity']['display_name'],bot['prospectus']['mission'],owner,collaborators),
                            'state': 'historical_specification', 'capability_verified': False})
    bot_rows = []
    for m in manifests:
        slug = m['slug']; profile = profile_by_slug.get(slug); owner = normalize(m['division'])
        sources = m['sources']
        bot_rows.append({'id': slug, 'name': m['name'], 'primary_owner': owner,
                         'declared_division': m['division'], 'collaborators': [],
                         'source_refs': sources, 'missing_source_paths': [s for s in sources if not (root/s).is_file()],
                         'source_status': 'recovered', 'manifest_flags': m['flags'],
                         'capabilities': [c['name'] for c in profile['capabilities']] if profile else [],
                         'purpose': profile['prospectus']['mission'] if profile else 'Manifest-only profile; inspect the cited source.',
                         'candidate_bots': [{'slug': slug,'name':m['name'],'declared_division':m['division'],
                                             'score':None,'matched_terms':[],'reason':'existing_shared_planner_identity'}] if slug in slugs else [],
                         'state': 'shared_planner_available' if slug in slugs else 'manifest_only',
                         'capability_verified': False})
    sources = ['config/proposals/master-registry.json','config/proposals/division-routing.json',
               'config/masterbot-65-registry.json','config/master_bot_registry.json',
               'config/bots/bot-manifests.generated.json','config/generated/bots.catalog.json',
               'tools/build_superbot_crosswalk.py','tools/proposal_registry.py','tools/normalize_legacy_portfolios.py','tools/place_original_bots.py']
    sources += sorted({ref for row in legacy_rows+bot_rows for ref in row['source_refs'] if (root/ref).is_file()})
    source_hashes = {name: hashlib.sha256((root/name).read_bytes()).hexdigest() for name in sorted(set(sources))}
    return {'schema_version':1,'schema':'dreamco.superbot_crosswalk.v1','truth_boundary':'Organizational connections and shared planning only; no scientific, commercial, or live capability is proven.',
            'source_hashes':source_hashes,'divisions':[routes[key] for key in sorted(routes)],
            'summary':{'proposal_slots':len(proposal_rows),'complete_source_proposals':sum(s['source_status'] in {'recovered','generated'} for s in proposal_rows),
                       'missing_source_proposals':sum(s['source_status']=='missing' for s in proposal_rows),
                       'partial_source_proposals':sum(s['source_status']=='partial' for s in proposal_rows),
                       'manifest_bots':len(bot_rows),'shared_planner_profiles':len(slugs),
                       'manifest_only_bots':sum(s['state']=='manifest_only' for s in bot_rows),
                       'historical_records':len(legacy_rows),'original_bot_records':sum(s['source_refs'][0].startswith('original-bots/') for s in legacy_rows),
                       'verified_specialist_capabilities':0},
            'proposals':proposal_rows,'bots':bot_rows,'legacy':legacy_rows}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check',action='store_true')
    args=parser.parse_args()
    data=build();encoded=json.dumps(data,ensure_ascii=False,separators=(',',':'))+'\n'
    drift=[]
    for path in (OUTPUT,PUBLIC):
        if args.check:
            if not path.exists() or path.read_text()!=encoded:drift.append(str(path.relative_to(ROOT)))
        else:
            path.parent.mkdir(parents=True,exist_ok=True);path.write_text(encoded)
    print(json.dumps({'ok':not drift,'drift':drift,'summary':data['summary']}))
    return 1 if drift else 0


if __name__=='__main__':
    raise SystemExit(main())
