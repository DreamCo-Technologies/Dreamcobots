"""Actions Failure Watch captures bounded evidence without creating issue cascades."""
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "actions-failure-watch.yml"


def test_failure_watch_observes_configured_main_workflow_completions():
    workflow = yaml.load(WORKFLOW.read_text(encoding="utf-8"), Loader=yaml.BaseLoader)
    trigger = workflow["on"]["workflow_run"]
    assert trigger["types"] == ["completed"]
    assert trigger["branches"] == ["main"]
    assert trigger["workflows"]
    assert "Actions Failure Watch" not in trigger["workflows"]


def test_failure_watch_excludes_itself_and_only_captures_real_failures():
    workflow = WORKFLOW.read_text(encoding="utf-8")
    capture = workflow.split("  capture:", 1)[1]
    assert "github.event.workflow_run.name != 'Actions Failure Watch'" in capture
    for conclusion in ("failure", "timed_out", "action_required", "stale"):
        assert f"conclusion == '{conclusion}'" in capture


def test_failure_watch_is_artifact_only_and_does_not_open_issues():
    workflow = WORKFLOW.read_text(encoding="utf-8")
    assert "repos/$GITHUB_REPOSITORY/actions/runs/$RUN_ID/jobs?per_page=100" in workflow
    assert "actions/upload-artifact@v7" in workflow
    assert "Issue filing is disabled" in workflow
    assert "Do not open GitHub issues" in workflow
    assert "actions/jobs/$job_id/logs" not in workflow
    assert "pull-requests: write" not in workflow


def test_safe_repair_reconciles_dashboard_and_pages_deployment_failures():
    repair = (ROOT / ".github" / "workflows" / "buddy-ci-safe-repair.yml").read_text(encoding="utf-8")
    assert "DreamCo Live Dashboard" in repair
    assert "Deploy Buddy Website" in repair


def test_all_modified_action_workflows_parse_as_yaml():
    paths = [
        ".github/workflows/actions-failure-watch.yml",
        ".github/workflows/buddy-ci-safe-repair.yml",
        ".github/workflows/fleet-runtime-truth.yml",
        ".github/workflows/dreamco-live-dashboard.yml",
        ".github/workflows/deploy-buddy-pages.yml",
    ]
    for relative in paths:
        yaml.load((ROOT / relative).read_text(encoding="utf-8"), Loader=yaml.BaseLoader)
