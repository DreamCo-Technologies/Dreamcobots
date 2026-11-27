import json
from pathlib import Path

import pytest

from tools.build_buddy_benchmark_guide_queue import build_queue

ROOT = Path(__file__).resolve().parents[1]


def _sources():
    index = json.loads((ROOT / "config/buddy-benchmark-index.json").read_text(encoding="utf-8"))
    tasks = json.loads((ROOT / "config/buddy-benchmark-task-registry.json").read_text(encoding="utf-8"))
    return index, tasks


def test_every_program_and_task_gets_a_guide_work_item():
    index, tasks = _sources()
    result = build_queue(index, tasks)
    assert result["program_count"] == len(index["programs"])
    assert result["task_count"] == len(tasks["tasks"])
    assert result["work_item_count"] == len(index["programs"]) + len(tasks["tasks"])
    assert result["measured_count"] == 0
    assert all(row["measured"] is False for row in result["work_items"])
    assert len({row["work_item_id"] for row in result["work_items"]}) == result["work_item_count"]


def test_program_guides_preserve_canonical_commands_and_scope():
    index, tasks = _sources()
    result = build_queue(index, tasks)
    programs = {row["benchmark_id"]: row for row in result["work_items"] if row["work_item_type"] == "program_guide"}
    for program in index["programs"]:
        row = programs[program["id"]]
        assert row["scope"] == program["scope"]
        assert row["check_command"] == program.get("check_command")
        assert "holdout and contamination controls are documented" in row["acceptance"]


def test_duplicate_benchmark_tasks_are_rejected():
    index, _ = _sources()
    tasks = {"schema": "dreamco.buddy_benchmark_registry.v1", "tasks": ["coding", "Coding"]}
    with pytest.raises(ValueError, match="duplicate benchmark task"):
        build_queue(index, tasks)
