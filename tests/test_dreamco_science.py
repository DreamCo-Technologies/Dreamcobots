import os
import sys

REPO_ROOT = os.path.join(os.path.dirname(__file__), '..')
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from bots.dreamco_science import (
    DiscoveryCorrelationEngine,
    DreamCredits,
    DreamScienceBrain,
    EvidenceLevel,
    InventionVoting,
    grade_evidence,
)


def test_dream_science_brain_core_flow():
    brain = DreamScienceBrain()
    left_id = brain.record_discovery('neuroscience', 'Sleep-guided memory replay', 'Sleep improves memory replay signals.', 'strong_evidence', source='paper-a')
    right_id = brain.record_discovery('cardiology', 'Heart-rate variability recovery', 'Sleep quality improves variability recovery.', 'proven', source='paper-b')

    discoveries = brain.get_discoveries(domain='neuroscience')
    assert discoveries[0]['id'] == left_id
    assert discoveries[0]['evidence_level'] == 'strong_evidence'
    assert len(brain.get_discoveries(min_evidence_level='strong_evidence')) == 2

    link_id = brain.link_discoveries(left_id, right_id, 'sleep-recovery-axis')
    related = brain.get_related_discoveries(left_id)
    assert link_id > 0
    assert related[0]['id'] == right_id
    assert related[0]['relationship_type'] == 'sleep-recovery-axis'

    update_id = brain.post_update('neuroscience', 'New sleep study', 'A recovery-focused sleep study was added.')
    updates = brain.get_updates(domain='neuroscience')
    assert update_id > 0
    assert updates[0]['headline'] == 'New sleep study'


def test_grade_evidence_parses_levels():
    assert grade_evidence('proven') is EvidenceLevel.PROVEN
    assert grade_evidence('strong') is EvidenceLevel.STRONG


def test_discovery_correlation_engine_hypothesis_and_breakthroughs():
    brain = DreamScienceBrain()
    brain.record_discovery('genetics', 'Epigenetic clock reset', 'Reset signals improved biological age markers.', 'proven')
    brain.record_discovery('genetics', 'Telomere stability pathway', 'Telomere maintenance improved repair.', 'strong_evidence')
    brain.record_discovery('metabolism', 'NAD recovery signal', 'Energy recovery improved in early work.', 'early_evidence')

    engine = DiscoveryCorrelationEngine(brain)
    hypothesis = engine.generate_hypothesis('genetics', 'healthy aging programs')
    breakthroughs = engine.scan_for_breakthroughs(['genetics'])

    assert hypothesis['domain'] == 'genetics'
    assert 'healthy aging programs' in hypothesis['hypothesis']
    assert 0 < hypothesis['confidence'] <= 0.95
    assert len(breakthroughs) == 2


def test_invention_voting_and_dream_credits():
    voting = InventionVoting()
    invention_id = voting.submit_idea('ada', 'Adaptive hydrogel patch', 'A regenerative wound-healing patch.', 'regenerative medicine')
    vote_count = voting.vote('grace', invention_id, 1)
    top = voting.get_top_inventions()

    assert invention_id > 0
    assert vote_count == 1
    assert top[0]['id'] == invention_id
    assert voting.get_invention(invention_id)['title'] == 'Adaptive hydrogel patch'
    assert voting.mark_for_simulation(invention_id) is True
    assert voting.credits.get_balance('ada') >= 2.0

    credits = DreamCredits()
    balance = credits.award('linus', 5, 'Research milestone')
    leaderboard = credits.get_leaderboard()
    assert balance == 5.0
    assert credits.get_balance('linus') == 5.0
    assert leaderboard[0]['user_id'] == 'linus'
