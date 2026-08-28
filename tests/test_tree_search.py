import pytest

from buddy_os.intelligence.tree_search import BoundedTreeSearch, SearchNode


def test_bounded_tree_search_respects_depth_and_beam_width():
    root = SearchNode("root", (("s", "0"),), 0)
    children = {
        "root": [
            SearchNode("a", (("s", "a"),), 1, 5, .8, "root", "A"),
            SearchNode("b", (("s", "b"),), 1, 2, .9, "root", "B"),
        ],
        "a": [SearchNode("aa", (("s", "aa"),), 2, 10, .7, "a", "AA")],
        "b": [],
    }
    search = BoundedTreeSearch(max_depth=2, beam_width=1)
    leaves = search.search(root, lambda n: children.get(n.node_id, []))
    assert leaves[-1].node_id == "aa"


def test_search_configuration_is_validated():
    with pytest.raises(ValueError):
        BoundedTreeSearch(max_depth=-1)
    with pytest.raises(ValueError):
        BoundedTreeSearch(beam_width=0)
