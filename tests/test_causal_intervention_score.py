import pytest

from buddy_os.intelligence.causal_intervention_score import InterventionCandidate, InterventionScorer


def test_intervention_scorer_prefers_high_value_low_risk_candidate():
    scorer = InterventionScorer()
    candidates = [
        InterventionCandidate("a", "cooling", .9, .9, cost=1, risk=.1),
        InterventionCandidate("b", "replacement", .95, .8, cost=4, risk=.2),
    ]
    ranked = scorer.rank(candidates)
    assert ranked[0].candidate_id == "a"
    assert scorer.score(ranked[0]) > scorer.score(ranked[1])


def test_intervention_candidate_validates_inputs():
    with pytest.raises(ValueError):
        InterventionCandidate("x", "v", 1.2, .5)
    with pytest.raises(ValueError):
        InterventionCandidate("x", "v", .5, .5, cost=0)
