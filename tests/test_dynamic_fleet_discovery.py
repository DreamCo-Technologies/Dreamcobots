import json

from framework.dynamic_fleet.discovery import discover_json_modules


def test_discovery_finds_modules_and_reports_bad_assets(tmp_path):
    good = tmp_path / "good.json"
    good.write_text(json.dumps({"bot_id": "alpha", "capabilities": ["geometry", "planning"]}), encoding="utf-8")
    bad = tmp_path / "bad.json"
    bad.write_text("{broken", encoding="utf-8")

    modules, errors = discover_json_modules(tmp_path)

    assert [m.module_id for m in modules] == ["alpha"]
    assert modules[0].capabilities == {"geometry", "planning"}
    assert len(errors) == 1
    assert errors[0]["path"].endswith("bad.json")


def test_discovery_does_not_impose_a_count_limit(tmp_path):
    for i in range(120):
        (tmp_path / f"module-{i}.json").write_text(
            json.dumps({"id": f"m-{i}", "skills": [f"cap-{i}"]}), encoding="utf-8"
        )

    modules, errors = discover_json_modules(tmp_path)
    assert len(modules) == 120
    assert errors == []
