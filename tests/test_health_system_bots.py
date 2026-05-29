import importlib
import os
import sys

import pytest

REPO_ROOT = os.path.join(os.path.dirname(__file__), '..')
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

HEALTH_BOTS = [
    ('nervous_system_bot', 'NervousSystemBot', 'brain health'),
    ('cardiovascular_bot', 'CardiovascularBot', 'heart health'),
    ('immune_system_bot', 'ImmuneSystemBot', 'immunology'),
    ('endocrine_bot', 'EndocrineBot', 'hormones'),
    ('musculoskeletal_bot', 'MusculoskeletalBot', 'muscle recovery'),
    ('digestive_bot', 'DigestiveBot', 'gut health'),
    ('respiratory_bot', 'RespiratoryBot', 'lung health'),
    ('skin_regeneration_bot', 'SkinRegenerationBot', 'anti-aging'),
    ('genetics_longevity_bot', 'GeneticsLongevityBot', 'CRISPR'),
]


@pytest.mark.parametrize(('slug', 'class_name', 'valid_domain'), HEALTH_BOTS)
def test_health_system_bot_core_flow(slug, class_name, valid_domain):
    module = importlib.import_module(f'bots.{slug}.{slug}')
    bot_cls = getattr(module, class_name)
    error_cls = getattr(module, f'{class_name}Error')

    bot = bot_cls(tier='pro')
    finding = bot.record_finding(valid_domain, 'Research signal', 'Promising early data.', 'strong_evidence', source='study')
    bot.record_finding(valid_domain, 'Safety note', 'Needs more evidence.', 'experimental')
    findings = bot.get_findings(valid_domain)
    filtered = bot.get_findings(valid_domain, 'strong_evidence')
    update = bot.post_discovery_update('New system update', 'Important finding added.')
    feed = bot.get_discovery_feed()
    summary = bot.research_summary()
    tier_info = bot.describe_tier()

    assert finding['domain'] == valid_domain
    assert 'DISCLAIMER:' in finding['disclaimer']
    assert len(findings) == 2
    assert len(filtered) == 1
    assert update['headline'] == 'New system update'
    assert feed[0]['headline'] == 'New system update'
    assert summary['total_findings'] == 2
    assert summary['tier'] == 'pro'
    assert tier_info['tier'] == 'pro'
    assert 'features' in tier_info

    with pytest.raises(error_cls):
        bot.record_finding('not-a-valid-domain', 'Oops', 'Out of scope')


def test_supplement_discovery_bot_flow():
    from bots.supplement_discovery_bot.supplement_discovery_bot import SupplementDiscoveryBot

    bot = SupplementDiscoveryBot()
    compound = bot.add_compound('Magnesium Glycinate', 'supplement', 'Supports sleep quality and relaxation.', 'strong_evidence', sources=['trial-1'])
    reclassified = bot.classify_compound(compound['id'], 'proven')
    matches = bot.search_compounds('magnesium', evidence_level='proven')
    category_items = bot.get_compounds_by_category('supplement')
    safety = bot.safety_check('Magnesium Glycinate')

    assert compound['name'] == 'Magnesium Glycinate'
    assert 'DISCLAIMER:' in compound['disclaimer']
    assert reclassified['evidence_level'] == 'proven'
    assert len(matches) == 1
    assert category_items[0]['type'] == 'supplement'
    assert safety['safety_status'] == 'research_supported'
    assert 'DISCLAIMER:' in safety['disclaimer']
