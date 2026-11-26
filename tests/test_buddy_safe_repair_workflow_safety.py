"""Safety tests for the main-only, branch-only generated-evidence repair workflow."""
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW_PATH = ROOT / ".github/workflows/buddy-ci-safe-repair.yml"


def test_safe_repair_can_be_dispatched_or_bootstrapped_only_on_main():
    workflow_text = WORKFLOW_PATH.read_text(encoding="utf-8")
    workflow = yaml.load(workflow_text, Loader=yaml.BaseLoader)
    triggers = workflow["on"]

    assert "workflow_dispatch" in triggers
    assert triggers["push"]["branches"] == ["main"]
    assert ".github/workflows/buddy-ci-safe-repair.yml" in triggers["push"]["paths"]
    assert "Buddy Bootcamp Curriculum" in triggers["workflow_run"]["workflows"]
    assert "Buddy Open-Source Weekly Bootcamp" in triggers["workflow_run"]["workflows"]
    assert "Buddy Bootcamp Curriculum" in triggers["workflow_run"]["workflows"]
    assert "Full System Certification" in triggers["workflow_run"]["workflows"]

    job = workflow["jobs"]["regenerate-and-verify"]
    checkout = next(step for step in job["steps"] if step.get("uses") == "actions/checkout@v4")
    assert "if" not in checkout
    assert "github.ref == 'refs/heads/main'" in job["if"]
    assert "github.event_name == 'workflow_dispatch'" in job["if"]
    assert "github.event_name == 'push'" in job["if"]
    assert "github.event.workflow_run.conclusion == 'failure'" in job["if"]


def test_safe_repair_uses_convergent_generators_and_only_pushes_a_repair_branch():
    workflow_text = WORKFLOW_PATH.read_text(encoding="utf-8")
    assert "python tools/refresh_repository_evidence.py" in workflow_text
    assert "python tools/generate_command_center_data.py" in workflow_text
    assert "python tools/generate_command_center_data.py --check" in workflow_text
    assert "node --import tsx tools/generate_bot_fleet_catalog.ts" in workflow_text
    assert "npm run buddy:fleet" in workflow_text
    assert "python tools/build_actions_prospectus.py --check --check-buttons" in workflow_text
    assert "python tools/build_file_prospectus.py --check" in workflow_text
    assert "python tools/sync_freecodecamp_learning_inventory.py" in workflow_text
    assert "python tools/sync_freecodecamp_learning_inventory.py --check" in workflow_text
    assert "tests.test_freecodecamp_learning_inventory" in workflow_text
    assert "tests.test_buddy_continuous_study_policy" in workflow_text
    assert "python tools/build_file_prospectus.py" in workflow_text
    assert "REPAIR_BRANCH:" in workflow_text
    assert "github.event.workflow_run.id || github.run_id" in workflow_text
    assert 'git switch -c "$REPAIR_BRANCH"' in workflow_text
    assert 'push "https://github.com/$GITHUB_REPOSITORY.git" "HEAD:refs/heads/$REPAIR_BRANCH"' in workflow_text
    assert "HEAD:refs/heads/main" not in workflow_text


def test_safe_repair_allowlist_includes_public_evidence_and_manifests():
    workflow_text = WORKFLOW_PATH.read_text(encoding="utf-8")
    for path in (
        "config/bots/bot-manifests.generated.json",
        "config/bots/division-manifests.generated.json",
        "config/generated/file-prospectus",
        "website/data/run-prospectus.json",
        "website/data/run-prospectus-bots.json",
        "website/data/pages-feature-audit.json",
        "command-center/data",
        "website/data/command-center",
        "config/master_bot_registry.json",
        "config/generated/bots.catalog.json",
        "website/data/bot-fleet-catalog.json",
        "website/data/buddy-routing-index.js",
        "website/data/bot-fleet",
        "reports/BOT_FLEET_PROSPECTUS.md",
        "config/freecodecamp-complete-learning-path.json",
        "config/buddy-continuous-study-policy.json",
        "website/data/fleet-runtime-status.json",
        "website/data/command-center",
    ):
        assert path in workflow_text
