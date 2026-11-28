import importlib.util
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parents[1] / "stages" / "06_repo_repair" / "__main__.py"
SPEC = importlib.util.spec_from_file_location("dreamco_stage06_repo_repair", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)


def test_dataset_route_failure_maps_only_to_static_dataset_builder():
    report = {
        "summary": {"failed": 1, "passed": 4},
        "tests": [{"nodeid": "tests/test_buddy_dataset_route_check.py::test_index", "outcome": "failed"}],
    }
    obs = MODULE.observation_from_report(report, "a" * 40)
    assert obs["failure_class"] == "generated-index"
    assert MODULE.repair_plan(obs) == [[MODULE.sys.executable, "tools/build_buddy_dataset_routes.py"]]


def test_unknown_failure_has_no_automatic_repair():
    report = {
        "summary": {"failed": 1},
        "tests": [{"nodeid": "tests/test_payment_security.py::test_auth", "outcome": "failed"}],
    }
    obs = MODULE.observation_from_report(report)
    assert obs["failure_class"] == "unknown"
    assert MODULE.repair_plan(obs) == []


def test_multiple_repair_families_require_human_triage():
    report = {
        "summary": {"failed": 2},
        "tests": [
            {"nodeid": "tests/test_buddy_dataset_route_check.py::test_index", "outcome": "failed"},
            {"nodeid": "tests/test_division_model_fleet.py::test_catalog", "outcome": "failed"},
        ],
    }
    obs = MODULE.observation_from_report(report)
    assert obs["failure_class"] == "unknown"
    assert MODULE.repair_plan(obs) == []


def test_passing_report_is_a_noop():
    report = {"summary": {"failed": 0, "passed": 2}, "tests": [
        {"nodeid": "tests/test_example.py::test_ok", "outcome": "passed"}
    ]}
    assert MODULE.observation_from_report(report)["failed_test_count"] == 0


def test_allowed_paths_cannot_expand_into_source_or_workflow_files():
    assert MODULE.allowed_prefixes("config/generated/,reports/") == ("config/generated/", "reports/")
    try:
        MODULE.allowed_prefixes("server/,.github/")
    except ValueError:
        pass
    else:
        raise AssertionError("protected source paths must remain excluded")


def test_path_guard_rejects_traversal_and_accepts_generated_artifacts():
    prefixes = MODULE.allowed_prefixes(None)
    assert not MODULE.path_is_allowed("../.github/workflows/ci.yml", prefixes)
    assert not MODULE.path_is_allowed("server/app.py", prefixes)
    assert MODULE.path_is_allowed("config/generated/index.json", prefixes)


def test_apply_guard_rejects_pull_request_context(monkeypatch, tmp_path):
    monkeypatch.setenv("GITHUB_EVENT_NAME", "pull_request")
    monkeypatch.setenv("GITHUB_REF", "refs/pull/1/merge")
    try:
        MODULE.assert_trusted_main(tmp_path, local_ok=True)
    except PermissionError:
        pass
    else:
        raise AssertionError("pull-request code must never execute a repair")


def test_failed_summary_without_node_ids_is_not_reported_as_pass():
    obs = MODULE.observation_from_report({"summary": {"failed": 1}, "tests": []})
    assert obs["failed_test_count"] == 1
    assert obs["failure_class"] == "unknown"


def _run_args(tmp_path, report_path, *, output="artifacts/repo-repair/result.json"):
    import argparse
    return argparse.Namespace(
        report=str(report_path), observation=None, max_attempts=3,
        allowed_paths=None, trajectory_dir="artifacts/repo-repair/trajectories",
        output=output, repo_root=str(tmp_path), apply=False, allow_local_apply=False,
    )


def test_output_path_traversal_is_rejected_before_report_read(tmp_path):
    args = _run_args(tmp_path, tmp_path / "missing.json", output="../outside.json")
    try:
        MODULE.run(args)
    except ValueError as exc:
        assert "Output path" in str(exc)
    else:
        raise AssertionError("output path must not escape repository root")


def test_input_report_must_remain_inside_repository(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    outside = tmp_path / "outside.json"
    outside.write_text('{"tests": [], "summary": {"failed": 0}}', encoding="utf-8")
    args = _run_args(repo, outside)
    try:
        MODULE.run(args)
    except ValueError as exc:
        assert "Input report" in str(exc)
    else:
        raise AssertionError("report path must not escape repository root")


def test_parameter_values_are_not_copied_into_failure_metadata():
    report = {
        "summary": {"failed": 1},
        "tests": [{"nodeid": "tests/test_example.py::test_user[person@example.test]", "outcome": "failed"}],
    }
    obs = MODULE.observation_from_report(report)
    assert "person@example.test" not in str(obs)
    assert "[parameterized]" in str(obs)


def test_repair_plan_cannot_inject_an_unregistered_script(monkeypatch, tmp_path):
    import sys
    report = {
        "summary": {"failed": 1},
        "tests": [{"nodeid": "tests/test_buddy_dataset_route_check.py::test_index", "outcome": "failed"}],
    }
    report_path = tmp_path / "report.json"
    import json
    report_path.write_text(json.dumps(report), encoding="utf-8")
    monkeypatch.setattr(MODULE, "repair_plan", lambda _obs: [[sys.executable, "tools/unregistered.py"]])
    args = _run_args(tmp_path, report_path)
    try:
        MODULE.run(args)
    except ValueError as exc:
        assert "fixed command allowlist" in str(exc)
    else:
        raise AssertionError("unregistered scripts must never execute")
