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
