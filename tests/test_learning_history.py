import json
from pathlib import Path

from buddy.learning.learning_history import append_event, capability_trend, summarize


def test_history_is_append_only_and_summarizable(tmp_path: Path):
    path = tmp_path / "learning.jsonl"
    append_event(path, {"capability_id": "coding", "verified": True, "native_success": True, "external_assistance": False, "promote": False})
    append_event(path, {"capability_id": "coding", "verified": True, "native_success": True, "external_assistance": False, "promote": True})
    append_event(path, {"capability_id": "research", "verified": True, "native_success": False, "external_assistance": True, "promote": False})

    lines = path.read_text().splitlines()
    assert len(lines) == 3
    assert summarize(path)["native_verified"] == 2
    assert summarize(path)["external_assisted"] == 1
    assert capability_trend(path, "coding")["promoted"] is True
    assert json.loads(lines[0])["capability_id"] == "coding"
