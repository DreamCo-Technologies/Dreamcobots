from buddy_os.intelligence.causal_engine import CausalEngine, CausalHypothesis
from buddy_os.intelligence.causal_temporal_bridge import CausalTemporalBridge
from buddy_os.intelligence.state_engine import StateEngine


def test_temporal_observation_is_explicitly_non_causal_proof():
    causal = CausalEngine()
    causal.add("h1", CausalHypothesis("a", "b"))
    bridge = CausalTemporalBridge(causal, StateEngine())
    bridge.observe("x", "planned", "simulated", "preflight", "2026-08-27T00:00:00+00:00")
    result = bridge.add_temporal_evidence("h1", "state-transition")
    assert result["evidence_count"] == 1
    assert result["support_score"] == 1.0
    assert bridge.timeline("x")[0]["current"] == "simulated"
    assert "not causal proof" in causal.get("h1").evidence[0].note
