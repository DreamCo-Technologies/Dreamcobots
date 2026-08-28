from buddy_os.intelligence.reasoning_conflict import ReasoningConflictResolver
from buddy_os.intelligence.reasoning_ensemble import ReasoningOpinion


def test_conflict_resolver_generates_verification_agenda():
    conflict = ReasoningConflictResolver().analyze([
        ReasoningOpinion("causal", "A", 0.8, ("e1",)),
        ReasoningOpinion("probabilistic", "B", 0.7, ("e2",)),
    ])
    assert conflict is not None
    assert set(conflict.answers) == {"A", "B"}
    assert "e1" in conflict.evidence and "e2" in conflict.evidence
    assert len(conflict.verification_questions) >= 3


def test_no_conflict_for_unanimous_answer():
    assert ReasoningConflictResolver().analyze([
        ReasoningOpinion("a", "same", 0.9),
        ReasoningOpinion("b", "same", 0.8),
    ]) is None
