from framework.custom_page.capability_questionnaire import QUESTIONS, recommend_capabilities


def test_questionnaire_covers_core_personalization_dimensions():
    ids = {question.id for question in QUESTIONS}
    assert {"goal", "reasoning", "data", "automation", "integrations", "trust"} <= ids


def test_answers_produce_ranked_capability_recommendations():
    result = recommend_capabilities({
        "goal": "build",
        "reasoning": "geometry",
        "data": "code",
        "automation": "execute_with_approval",
        "integrations": "github",
        "trust": "policy_gated",
    })
    names = {item["capability"] for item in result["capabilities"]}
    assert "coding" in names
    assert "geometric_reasoning" in names
    assert "github_integration" in names
    assert result["answered"] == 6


def test_unknown_answers_are_non_fatal():
    result = recommend_capabilities({"goal": "unknown-choice"})
    assert result["capabilities"] == []
