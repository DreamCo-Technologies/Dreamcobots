"""Regression tests for bounded, non-recursive Actions failure issue filing."""
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]


def test_failure_sweep_is_main_only_and_serialized():
    workflow_text = (ROOT / ".github/workflows/actions-failure-sweep.yml").read_text(encoding="utf-8")
    workflow = yaml.load(workflow_text, Loader=yaml.BaseLoader)
    assert workflow["on"]["push"]["branches"] == ["main"]
    assert "github.ref == 'refs/heads/main'" in workflow["jobs"]["sweep"]["if"]
    assert workflow["concurrency"]["cancel-in-progress"] == "false"


def test_failure_sweep_deduplicates_all_issue_states_and_excludes_itself():
    workflow_text = (ROOT / ".github/workflows/actions-failure-sweep.yml").read_text(encoding="utf-8")
    assert "--state all --search" in workflow_text
    assert "row.get('head_branch') != 'main'" in workflow_text
    assert "row.get('name') == 'Actions Failure Sweep'" in workflow_text
