import pytest

from buddy_os.intelligence.reasoning_ensemble import ReasoningEnsemble, ReasoningOpinion


def test_ensemble_requires_verification_when_methods_disagree():
    result = ReasoningEnsemble().combine([
        ReasoningOpinion("causal", "A", 0.9, ("e1",)),
        ReasoningOpinion("bayesian", "B", 0.8, ("e2",)),
    ])
    assert result.disputed
    assert result.requires_verification
    assert result.confidence <= 0.9


def test_ensemble_can_reach_high_agreement_without_claiming_ground_truth():
    result = ReasoningEnsemble().combine([
        ReasoningOpinion("deductive", "A", 0.95),
        ReasoningOpinion("constraint", "A", 0.9),
        ReasoningOpinion("symbolic", "A", 0.9),
    ])
    assert result.answer == "A"
    assert result.agreement == pytest.approx(1.0)
    assert not result.requires_verification
