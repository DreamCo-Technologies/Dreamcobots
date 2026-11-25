import json
from pathlib import Path

import pytest

from tools.build_buddy_revenue_playbook_queue import build_queue

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "config/buddy-workforce-entrepreneurship-bootcamp.json"


def test_queue_preserves_every_subject_across_all_canonical_paths():
    config = json.loads(SOURCE.read_text(encoding="utf-8"))
    result = build_queue(config)
    expected = sum(len(path["subjects"]) for path in config["training_paths"])
    assert result["track_count"] == len(config["training_paths"]) == 12
    assert result["playbook_work_item_count"] == expected
    assert len(result["playbooks"]) == expected
    assert result["authored_count"] == result["reviewed_count"] == 0
    assert all(row["status"] == "not_authored" for row in result["playbooks"])
    assert all(row["capstone_status"] == "needs_definition" for row in result["playbooks"])
    assert len({row["playbook_id"] for row in result["playbooks"]}) == expected


def test_every_item_carries_the_full_task_playbook_contract():
    config = json.loads(SOURCE.read_text(encoding="utf-8"))
    result = build_queue(config)
    required = config["task_capability_catalog"]["task_playbook_requirements"]
    for row in result["playbooks"]:
        assert row["required_sections"] == required
        assert row["authoring_brief"]["objective"]
        assert "guaranteed employment, income, funding or business success" in row["authoring_brief"]["must_not_assume"]


def test_duplicate_track_or_subject_is_rejected():
    config = {
        "schema": "dreamco.buddy_workforce_entrepreneurship_bootcamp.v1",
        "task_capability_catalog": {"task_playbook_requirements": ["task_definition"]},
        "training_paths": [
            {"id": "one", "title": "One", "subjects": ["sales", "sales"], "capstone": "Build a pipeline"}
        ],
    }
    with pytest.raises(ValueError, match="duplicate subject"):
        build_queue(config)


def test_missing_capstone_is_explicitly_queued_for_definition():
    config = {
        "schema": "dreamco.buddy_workforce_entrepreneurship_bootcamp.v1",
        "task_capability_catalog": {"task_playbook_requirements": ["task_definition"]},
        "training_paths": [{"id": "one", "title": "One", "subjects": ["sales"]}],
    }
    result = build_queue(config)
    assert result["playbooks"][0]["capstone_status"] == "needs_definition"
    assert result["playbooks"][0]["capstone_outcome"] is None
