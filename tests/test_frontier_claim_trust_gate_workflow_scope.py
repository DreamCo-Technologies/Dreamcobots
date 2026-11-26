"""Ensure strict frontier certification is limited to actual public claim surfaces."""
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github/workflows/frontier-claim-trust-gate.yml"


def test_strict_claim_gate_is_scoped_to_public_claim_surfaces():
    data = yaml.load(WORKFLOW.read_text(encoding="utf-8"), Loader=yaml.BaseLoader)
    pull_paths = data["on"]["pull_request"]["paths"]
    push_paths = data["on"]["push"]["paths"]
    assert ".github/workflows/frontier-claim-trust-gate.yml" not in push_paths

    for paths in (pull_paths, push_paths):
        assert "website/**" not in paths
        assert "website/*benchmark*.html" in paths
        assert "website/*model*.html" in paths
        assert "website/*production*.html" in paths
        assert "website/data/*frontier*" in paths
        assert "website/data/*claim*" in paths

    assert "website/buddy-bootcamp.html" not in pull_paths
    assert "website/dataset-profile-builder.html" not in pull_paths


def test_deploy_mode_checks_every_triggered_claim_change_without_soak_artifact():
    data = yaml.load(WORKFLOW.read_text(encoding="utf-8"), Loader=yaml.BaseLoader)
    steps = data["jobs"]["vanity-and-unit"]["steps"]
    names = [step.get("name", "") for step in steps]
    assert "Deploy-mode trust check (fail on vanity while gates red)" in names
    assert "Restore latest successful 24-hour sandbox evidence" not in names

    strict_steps = data["jobs"]["claim-surfaces-all-gates"]["steps"]
    strict_names = [step.get("name", "") for step in strict_steps]
    assert "Restore latest successful 24-hour sandbox evidence" in strict_names
    assert "Strict require-all-gates (hard-fail until claimable)" in strict_names
