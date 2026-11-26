"""Actions Failure Watch must observe all main-branch workflows without recursion."""
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "actions-failure-watch.yml"


def test_failure_watch_observes_every_main_workflow_completion():
    workflow = yaml.load(WORKFLOW.read_text(encoding="utf-8"), Loader=yaml.BaseLoader)
    trigger = workflow["on"]["workflow_run"]
    assert trigger["types"] == ["completed"]
    assert trigger["branches"] == ["main"]
    assert "workflows" not in trigger


def test_failure_watch_excludes_itself_and_only_captures_real_failures():
    workflow = WORKFLOW.read_text(encoding="utf-8")
    capture = workflow.split("  capture:", 1)[1]
    assert "github.event.workflow_run.name != 'Actions Failure Watch'" in capture
    for conclusion in ("failure", "timed_out", "action_required", "stale"):
        assert f"conclusion == '{conclusion}'" in capture


def test_failure_watch_downloads_failed_job_logs_and_does_not_file_issues():
    workflow = WORKFLOW.read_text(encoding="utf-8")
    assert "actions/jobs/$job_id/logs" in workflow
    assert "failure-evidence/job-logs/$job_id.zip" in workflow
    assert "Issue filing is disabled" in workflow
