from learning_history import append_event, summarize


def test_learning_history_is_append_only_and_measurable(tmp_path):
    path = tmp_path / "history.jsonl"
    append_event(path, {"verified": True, "promote": True, "native_success": True, "external_assistance": False})
    append_event(path, {"verified": True, "promote": False, "native_success": False, "external_assistance": True})
    result = summarize(path)
    assert result["events"] == 2
    assert result["verified"] == 2
    assert result["promoted"] == 1
    assert result["native_solve_rate"] == 0.5
