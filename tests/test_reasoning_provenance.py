import pytest

from buddy_os.intelligence.reasoning_provenance import ProvenanceNode, ReasoningProvenanceGraph


def test_provenance_graph_traces_conclusion_to_evidence():
    graph = ReasoningProvenanceGraph()
    graph.add_node(ProvenanceNode("e", "evidence", "sensor observation"))
    graph.add_node(ProvenanceNode("m", "method", "causal analysis"))
    graph.add_node(ProvenanceNode("c", "conclusion", "candidate cause"))
    graph.connect("e", "supports", "m")
    graph.connect("m", "produces", "c")
    assert graph.trace("c") == ("c", "e", "m")
    assert graph.predecessors("c")[0].relation == "produces"


def test_provenance_rejects_unknown_nodes_and_duplicates():
    graph = ReasoningProvenanceGraph()
    graph.add_node(ProvenanceNode("x", "evidence", "x"))
    with pytest.raises(KeyError):
        graph.connect("x", "supports", "missing")
    with pytest.raises(ValueError):
        graph.add_node(ProvenanceNode("x", "evidence", "duplicate"))
