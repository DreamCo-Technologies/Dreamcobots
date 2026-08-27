from buddy_os.learning.decision_engine import BuddyDecisionEngine, CandidateEvidence


def test_decision_engine_selects_best_authorized_candidate():
    engine = BuddyDecisionEngine()
    result = engine.decide([
        CandidateEvidence("strong", capability=1, reliability=1, evidence_quality=1, historical_success=1),
        CandidateEvidence("weak", capability=.3, reliability=.2),
    ])
    assert result.selected == "strong"
    assert result.confidence >= .55


def test_decision_engine_never_ranks_unauthorized_candidate():
    engine = BuddyDecisionEngine()
    result = engine.decide([
        CandidateEvidence("unauthorized", capability=1, authorized=False),
        CandidateEvidence("approved", capability=.2, evidence_quality=.8),
    ])
    assert all(item["name"] != "unauthorized" for item in result.ranked)
