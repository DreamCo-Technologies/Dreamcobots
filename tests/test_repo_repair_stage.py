import importlib.util
import json
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parents[1] / "stages" / "06_repo_repair" / "__main__.py"
SPEC = importlib.util.spec_from_file_location("dreamco_stage06_repo_repair", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)


def test_report_maps_known_dataset_route_failure_to_static_repair():
    report = {
        "summary": {"failed": 1, "passed": 4},
        "tests": [{"nodeid": "tests/test_buddy_dataset_route_check.py::test_index", "outcome": "failed"}],
    }
    observation = MODULE.observation_from_report(report, "a" * 40)
    assert observation["failure_class"] == "generated-index"
    assert observation["repair_family"] == "dataset-route"
    assert MODULE.repair_plan(observation) == [[MODULE.sys.executable, "tools/build_buddy_dataset_routes.py"]]


def test_unknown_failure_never_gets_an_automatic_command():
    report = {
        "summary": {"failed": 1},
        "tests": [{"nodeid": "tests/test_payment_security.py::test_auth", "outcome": "failed"}],
    }
    observation = MODULE.observation_from_report(report)
    assert observation["failure_class"] == "unknown"
    assert MODULE.repair_plan(observation) == []


def test_multiple_repair_families_are_not_auto_routed():
    report = {
        "summary": {"failed": 2},
        "tests": [
            {"nodeid": "tests/test_buddy_dataset_route_check.py::test_index", "outcome": "failed"},
            {"nodeid": "tests/test_division_model_fleet.py::test_catalog", "outcome": "failed"},
        ],
    }
    observation = MODULE.observation_from_report(report)
    assert observation["failure_class"] == "unknown"
    assert MODULE.repair_plan(observation) == []


def test_report_with_no_failures_is_a_noop():
    report = {"summary": {"failed": 0, "passed": 3}, "tests": [
        {"nodeid": "tests/test_example.py::test_ok", "outcome": "passed"}
    ]}
    observation = MODULE.observation_from_report(report)
    assert observation["failed_test_count"] == 0


def test_allowed_paths_cannot_expand_beyond_generated_artifact_allowlist():
    assert MODULE.validate_allowed_paths("config/generated/,reports/") == (
        "config/generated/", "reports/"
    )
    try:
        MODULE.validate_allowed_paths("server/,tools/")
    except ValueError:
        pass
    else:
        raise AssertionError("source-code paths must not be admitted")


def test_path_guard_rejects_traversal_and_protected_paths():
    prefixes = MODULE.validate_allowed_paths(None)
    assert not MODULE._is_allowed_path("../.github/workflows/ci.yml", prefixes)
    assert not MODULE._is_allowed_path("server/app.py", prefixes)
    assert MODULE._is_allowed_path("config/generated/index.json", prefixes)


def test_attempt_limit_is_capped_at_three():
    import argparse
    args = argparse.Namespace(
        report=None, observation=None, max_attempts=4, allowed_paths=None,
        trajectory_dir="artifacts/repo-repair/trajectories", output="artifacts/repo-repair/result.json",
        repo_root=str(MODULE.ROOT), apply=False, allow_local_apply=False,
    )
    try:
        MODULE.run(args)
    except ValueError:
        pass
    else:
        raise AssertionError("invalid attempt limit should be rejected")
