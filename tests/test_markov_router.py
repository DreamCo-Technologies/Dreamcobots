from buddy_os.learning.markov_router import MarkovRouteAdvisor


def test_markov_route_advisor_ranks_learned_routes():
    advisor = MarkovRouteAdvisor().learn(
        [
            ["intake", "code_review", "test"],
            ["intake", "code_review", "deploy"],
            ["intake", "research", "review"],
        ]
    )
    ranked = advisor.rank("intake", ["code_review", "research"])
    assert ranked[0].route == "code_review"


def test_markov_route_advisor_is_advisory_only():
    advisor = MarkovRouteAdvisor().learn([["a", "b"]])
    evidence = advisor.evidence("a", ["b"])
    assert evidence["authority"] == "advisory"
    assert evidence["execution"] == "none"
