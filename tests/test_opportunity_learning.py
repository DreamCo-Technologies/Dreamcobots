import json

import pytest

from core.opportunity_learning import Opportunity, build_report
from global_learning_system.learning_loop import BotDecision, GlobalLearningLoop


def test_opportunity_score_and_approval_gate():
    item = Opportunity.from_dict(
        {
            "id": "one",
            "title": "One",
            "evidence_strength": 0.8,
            "expected_value": 0.7,
            "effort": 0.2,
            "risk": 0.1,
            "next_experiment": "Draft",
            "required_actions": ["money_movement"],
        }
    )

    assert item.score == 0.575
    assert item.requires_owner_approval is True


def test_build_report_ranks_without_external_actions(tmp_path):
    config = tmp_path / "opportunities.json"
    config.write_text(
        json.dumps(
            {
                "opportunities": [
                    {
                        "id": "low",
                        "title": "Low",
                        "evidence_strength": 0.2,
                        "expected_value": 0.2,
                        "effort": 0.8,
                        "risk": 0.8,
                        "next_experiment": "Research",
                        "required_actions": [],
                    },
                    {
                        "id": "high",
                        "title": "High",
                        "evidence_strength": 0.9,
                        "expected_value": 0.8,
                        "effort": 0.2,
                        "risk": 0.1,
                        "next_experiment": "Draft",
                        "required_actions": ["purchase"],
                    },
                ]
            }
        )
    )

    report = build_report(config)

    assert report["external_actions_executed"] is False
    assert [item["opportunity_id"] for item in report["opportunities"]] == ["high", "low"]
    assert report["opportunities"][0]["status"] == "awaiting_owner_approval"


def test_scores_must_be_bounded():
    with pytest.raises(ValueError):
        Opportunity.from_dict(
            {
                "id": "bad",
                "title": "Bad",
                "evidence_strength": 2,
                "expected_value": 0.5,
                "effort": 0.5,
                "risk": 0.5,
                "next_experiment": "None",
            }
        )


def test_recent_outcomes_are_ordered_and_classified(tmp_path):
    loop = GlobalLearningLoop(db_path=tmp_path / "learning.db")
    loop.record_decision(
        BotDecision(
            decision_id="success",
            bot_name="test",
            action_type="experiment",
            action_params={},
            context={},
            prediction=0.8,
            timestamp="2026-01-01T00:00:00+00:00",
        )
    )
    loop.record_outcome("success", actual_outcome=1.0, reward=2.0)
    loop.record_decision(
        BotDecision(
            decision_id="failure",
            bot_name="test",
            action_type="experiment",
            action_params={},
            context={},
            prediction=0.4,
            timestamp="2026-01-02T00:00:00+00:00",
        )
    )
    loop.record_outcome("failure", actual_outcome=0.0, reward=0.0)

    outcomes = loop.get_recent_outcomes(n=2)

    assert [item["decision_id"] for item in outcomes] == ["failure", "success"]
    assert [item["outcome"] for item in outcomes] == ["failure", "success"]
