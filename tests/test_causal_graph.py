import pytest

from buddy_os.intelligence.causal_graph import CausalEdge, CausalGraph


def test_causal_graph_distinguishes_upstream_candidates():
    graph = CausalGraph()
    graph.add_edge(CausalEdge("engine", "temperature", 0.8, ("e1",)))
    graph.add_edge(CausalEdge("coolant", "temperature", 0.7, ("e2",)))
    graph.add_edge(CausalEdge("temperature", "shutdown", 0.9, ("e3",)))
    assert set(graph.parents("temperature")) == {"engine", "coolant"}
    assert graph.children("temperature") == ("shutdown",)
    assert set(graph.intervention_candidates("temperature")) == {"engine", "coolant"}


def test_causal_edge_rejects_self_edges_and_bad_confidence():
    with pytest.raises(ValueError):
        CausalEdge("x", "x")
    with pytest.raises(ValueError):
        CausalEdge("x", "y", 1.2)
