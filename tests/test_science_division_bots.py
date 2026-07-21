import importlib
import os
import sys

import pytest

REPO_ROOT = os.path.join(os.path.dirname(__file__), '..')
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

SCIENCE_BOTS = [
    ('plant_science_bot', 'PlantScienceBot', 'agriculture'),
    ('animal_science_bot', 'AnimalScienceBot', 'veterinary science'),
    ('ocean_science_bot', 'OceanScienceBot', 'marine biology'),
    ('earth_systems_bot', 'EarthSystemsBot', 'climate science'),
    ('space_science_bot', 'SpaceScienceBot', 'astronomy'),
]


@pytest.mark.parametrize(('slug', 'class_name', 'valid_domain'), SCIENCE_BOTS)
def test_science_division_bot_core_flow(slug, class_name, valid_domain):
    module = importlib.import_module(f'bots.{slug}.{slug}')
    bot_cls = getattr(module, class_name)
    error_cls = getattr(module, f'{class_name}Error')

    bot = bot_cls(tier='enterprise')
    finding = bot.record_finding(valid_domain, 'Cross-domain discovery', 'A meaningful systems discovery.', 'proven', source='lab')
    bot.record_finding(valid_domain, 'Exploratory signal', 'Still under investigation.', 'experimental')
    findings = bot.get_findings(valid_domain)
    filtered = bot.get_findings(valid_domain, 'proven')
    update = bot.post_discovery_update('Research pulse', 'Fresh discovery feed item.')
    feed = bot.get_discovery_feed(limit=5)
    summary = bot.research_summary()
    tier_info = bot.describe_tier()

    assert finding['evidence_level'] == 'proven'
    assert len(findings) == 2
    assert len(filtered) == 1
    assert update['headline'] == 'Research pulse'
    assert feed[0]['headline'] == 'Research pulse'
    assert summary['proven_findings'] == 1
    assert summary['tier'] == 'enterprise'
    assert tier_info['tier'] == 'enterprise'

    with pytest.raises(error_cls):
        bot.record_finding('invalid domain', 'Nope', 'Should fail')
