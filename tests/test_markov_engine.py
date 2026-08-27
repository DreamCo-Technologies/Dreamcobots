from buddy_os.learning.markov_engine import MarkovChain


def test_markov_chain_predicts_observed_next_state():
    model = MarkovChain(smoothing=0.1).fit(
        [
            ["intake", "classify", "plan", "execute"],
            ["intake", "classify", "plan", "review"],
            ["intake", "classify", "plan", "execute"],
        ]
    )

    predictions = model.predict_next("plan", top_k=2)
    assert predictions[0].state == "execute"
    assert predictions[0].probability > predictions[1].probability


def test_transition_probabilities_are_normalized():
    model = MarkovChain(smoothing=0.1).fit([["a", "b", "a"], ["a", "b", "c"]])
    row = model.transition_matrix()["a"]
    assert abs(sum(row.values()) - 1.0) < 1e-9


def test_anomaly_score_prefers_unseen_or_rare_transition():
    model = MarkovChain(smoothing=0.1).fit([["a", "b"], ["a", "b"], ["a", "c"]])
    assert model.anomaly_score("a", "c") > model.anomaly_score("a", "b")
