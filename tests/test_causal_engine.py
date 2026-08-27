from buddy_os.intelligence.causal_engine import CausalEngine, CausalHypothesis, Evidence


def test_causal_engine_keeps_weak_evidence_uncertain():
    engine = CausalEngine()
    engine.add("h1", CausalHypothesis("a", "b", evidence=[Evidence("source-a", True, .5), Evidence("source-b", False, .5)]))
    result = engine.assess("h1")
    assert result["status"] == "uncertain"
    assert result["support_score"] == .5
