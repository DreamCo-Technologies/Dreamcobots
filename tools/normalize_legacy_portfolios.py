"""Adapt preserved historical bot sources to the existing portfolio shape.

This is discovery and categorization, not promotion to verified runtime instances.
"""
from __future__ import annotations
import hashlib
import re
from collections import Counter
from pathlib import Path
from tools.place_original_bots import parse_category, parse_system, infer_owner, slugify

DIVISION_ALIASES = {
    'DreamStreaming':'DreamContent', 'DreamLicensing':'DreamLegal',
    'DreamFoundry':'DreamAIInfra', 'DreamFranchise':'DreamBizLaunch',
    'DreamSaaS':'DreamAutomation', 'DreamTravel':'DreamTransport',
    'DreamAgency':'DreamProServices', 'DreamIntegrations':'DreamCodeLab',
    'DreamAffiliate':'DreamSalesPro', 'DreamRobotics':'DreamAIInfra',
}

def section(text, heading):
    found=re.search(r'^## '+re.escape(heading)+r'\s*\n(.*?)(?=^## |\Z)',text,re.M|re.S)
    return found[1].strip() if found else ''

def build_legacy_portfolios(root: Path, registry: dict) -> dict:
    canonical={b['identity']['slug']:b for b in registry['bots']}
    divisions={d['name'] for d in registry['divisions']}
    records=[]
    for path in sorted((root/'original-bots/autonomous-income-network').glob('category-*.md')):
        records.extend(parse_category(path))
    for path in sorted((root/'original-bots/systems').glob('*.md')):
        row=parse_system(path);text=path.read_text();mission=re.search(r'\*\*Mission:\*\*\s*(.+)',text)
        if mission:row['mission']=mission[1]
        row['specification']=text
        row['capabilities']=[x.strip() for x in re.findall(r'^###\s+(.+)',text,re.M)]
        records.append(row)
    markdown_linked=[]
    for path in sorted((root/'bots').rglob('*.md')):
        relative=path.relative_to(root).as_posix()
        if path.stem in canonical:
            markdown_linked.append({'path':relative,'canonical_id':path.stem})
            continue
        text=path.read_text();heading=re.search(r'^#\s+(.+)',text,re.M);division=re.search(r'\*\*Division:\*\*\s*([^|\n]+)',text)
        records.append({'kind':'historical_markdown_profile','source':relative,'slug':path.stem,
            'display_name':heading[1] if heading else path.stem,'mission':section(text,'Description'),
            'primary_division':division[1].strip() if division else 'DreamAgents',
            'capabilities':[line[2:].strip() for line in section(text,'Capabilities').splitlines() if line.startswith('- ')],
            'target_users':section(text,'Target Users'),'business_model':section(text,'Revenue Model'),
            'specification':text})
    items=[];bots=[]
    historical_groups={}
    for row in records:
        historical_groups.setdefault(row['slug'].removesuffix('-bot'),[]).append(row)
    for row in records:
        source=row['source'];raw_division=row['primary_division'];division=DIVISION_ALIASES.get(raw_division,raw_division)
        if division not in divisions:
            division=infer_owner(row['display_name']+' '+row['mission'],'DreamAgents')
            if division not in divisions:division='DreamAgents'
        identity_key=f"{source}:{row.get('index',0)}:{row['slug']}"
        identifier='legacy-'+hashlib.sha256(identity_key.encode()).hexdigest()[:16]
        exact=[slug for slug in canonical if slug==row['slug']]
        caps=row.get('capabilities') or [row['mission'] or 'Historical specification review']
        match_state='canonical_identity_reference' if exact else 'historical_profile_not_promoted'
        item={'id':identifier,'name':row['display_name'],'division_id':division.lower().replace(' ','-'),
              'category':row['kind'],'status':'catalogued','source_refs':[source],'evidence_refs':[source],
              'capability_ids':[],'legacy':True,'canonical_matches':exact,
              'source_division':raw_division,'classification':'source_declared' if division==raw_division else 'normalized_to_existing_division',
              'accounting_state':match_state,'same_name_source_records':len(historical_groups[row['slug'].removesuffix('-bot')])}
        bot={'identity':{'slug':identifier,'display_name':row['display_name'],'division':division,'category':row['kind'],'catalog_status':'catalogued'},
             'prospectus':{'mission':row['mission'],'target_users':row.get('target_users') or 'Not specified in this historical record',
                'catalog_business_model':row.get('business_model') or 'Historical concept; not commercially verified',
                'catalog_price_range':'Not verified','inputs':['Owner-defined brief and approved source material'],
                'outputs':['A reviewed plan; runtime outputs are not verified'],
                'limitations':['Historical source preserved. Not counted as an additional active runtime.',
                               'Division mapping is organizational; implementation and sandbox validation are still required.',
                               'Capability descriptions are historical claims, not completed actions.']},
             'capabilities':[{'name':c,'source':source,'evidence_level':'catalog_declared'} for c in caps],
             'readiness':{'production_verified':False,'runtime_promotion':'not_verified','accounting_state':match_state},
             'evidence':{'historical_source':source,'source_index':row.get('index'),'canonical_matches':exact},
             'historical_specification':row.get('specification',''),
             'logo':{'logo_id':'logo-'+identifier,'emoji':'📚','monogram':row['display_name'][:2].upper(),'shape':'tile','colors':{'primary':'#334155','accent':'#60a5fa','surface':'#111827'},'accessibility_label':row['display_name']+' historical profile'},
             'tools':[], 'api_candidates':[],
             'data_contract':{'inputs':['Owner brief'],'outputs':['Reviewable plan'],'status':'historical_contract_requires_validation'},
             'approvals':{'external_actions':'owner_approval_required','production_actions_enabled':False},
             'sandbox':{'status':'not_verified','fixture_policy':'synthetic_data_only'},
             'business_system':{'status':'historical_concept','revenue_verified':False},
             'sample_test_prompt':'Review the historical specification for '+row['display_name']+'. Identify one capability, its inputs, expected output, and a synthetic test. Do not claim execution.'}
        items.append(item);bots.append(bot)
    return {'schema':'dreamco.command_center.legacy_portfolios.v1',
            'summary':{'historical_source_records':len(items),'canonical_profiles':len(canonical),
                       'markdown_files_linked_to_canonical':len(markdown_linked),
                       'exact_canonical_reference_records':sum(bool(x['canonical_matches']) for x in items),
                       'historical_divisions':len({x['division_id'] for x in items})},
            'truth':'Historical source records are counted separately. Duplicate records do not increase the verified runtime count.',
            'items':items,'bots':bots,'canonical_markdown_links':markdown_linked,
            'by_division':dict(sorted(Counter(x['division_id'] for x in items).items()))}
