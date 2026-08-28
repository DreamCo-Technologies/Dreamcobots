import pytest

from buddy_os.intelligence.hypothesis_engine import Hypothesis, HypothesisEngine


def test_hypothesis_engine_ranks_transparently_and_generates_tests():
    engine = HypothesisEngine()
    engine.add(Hypothesis("h1", "cause A", 0.6, ("predicts X",), ("not X",), ("e1",)))
    engine.add(Hypothesis("h2", "cause B", 0.7, ("predicts Y",), ("not Y",), ("e2", "e3")))
    assert engine.rank()[0].hypothesis_id == "h2"
    questions = engine.discriminating_questions()
    assert any("h1" in q for q in questions)
    assert any("h2" in q for q in questions)


def test_hypothesis_confidence_is_bounded():
    with pytest.raises(ValueError):
        Hypothesis("bad", "bad", -0.1)
