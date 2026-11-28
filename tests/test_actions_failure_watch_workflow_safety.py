"""Safety checks for the main-branch Actions failure evidence watcher."""
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "actions-failure-watch.yml"


def test_failure_watch_covers_critical_dreamco_workflows():
    workflow = yaml.load(WORKFLOW.read_text(encoding="utf-8"), Loader=yaml.BaseLoader)
    trigger = workflow["on"]["workflow_run"]
    assert trigger["types"] == ["completed"]
    assert trigger["branches"] == ["main"]
    names = set(trigger["workflows"])
    assert {
        "Full System Certification",
        "Fleet runtime truth",
        "Buddy Bootcamp Curriculum",
        "DreamCo 55-Division Curriculum",
        "Buddy In-House Capability Certification",
        "DreamCo Live Dashboard",
        "Deploy Buddy Website",
    }.issubset(names)
    assert "Actions Failure Watch" not in names


def test_failure_watch_keeps_issue_creation_disabled_and_evidence_read_only():
    workflow = WORKFLOW.read_text(encoding="utf-8")
    assert "Issue filing disabled" in workflow
    assert "issues: write" not in workflow
    assert "actions: read" in workflow
    assert "contents: read" in workflow
