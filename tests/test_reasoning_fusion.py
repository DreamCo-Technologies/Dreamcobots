import pytest

from buddy_os.intelligence.reasoning_fusion import ReasoningFusion, ReasoningSignal


def test_fusion_preserves_sources_evidence_and_conflict():
    signals = [
        ReasoningSignal("causal", "plan_a", .9, ("e1",)),
        ReasoningSignal("tree", "plan_a", .8, ("e2",)),
        ReasoningSignal("monte_carlo", "plan_b", .7, ("e3",)),
    ]
    fused = ReasoningFusion().fuse(signals)
    assert fused[0].claim == "plan_a"
    assert fused[0].supporting_sources == ("causal", "tree")
    assert fused[0].evidence_ids == ("e1", "e2")
    assert fused[0].contradicting_claims == ("plan_b",)
    assert fused[0].confidence == pytest.approx(.72)


def test_signal_validation():
    with pytest.raises(ValueError):
        ReasoningSignal("", "x", .5)
    with pytest.raises(ValueError):
        ReasoningSignal("x", "y", 1.1)
