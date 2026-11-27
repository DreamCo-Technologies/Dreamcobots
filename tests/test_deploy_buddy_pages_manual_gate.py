"""Ensure static-site publishing cannot happen on an ordinary main push."""
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[1]


def test_github_pages_deploy_requires_manual_dispatch_on_main():
    workflow = yaml.safe_load((ROOT / ".github/workflows/deploy-buddy-pages.yml").read_text(encoding="utf-8"))
    condition = workflow["jobs"]["deploy"]["if"]
    assert "github.event_name == 'workflow_dispatch'" in condition
    assert "github.ref == 'refs/heads/main'" in condition
    assert workflow["jobs"]["deploy"]["needs"] == "build"
    build_steps = workflow["jobs"]["build"]["steps"]
    assert any(
        "tools/check_frontier_claim_trust_gates.py" in str(step.get("run", ""))
        for step in build_steps
    )

def test_production_evidence_ledger_is_refreshed_after_validation_before_pages_checks():
    workflow = yaml.safe_load((ROOT / ".github/workflows/deploy-buddy-pages.yml").read_text(encoding="utf-8"))
    commands = [str(step.get("run", "")) for step in workflow["jobs"]["build"]["steps"]]
    check_index = next(i for i, command in enumerate(commands) if "generate_production_evidence_ledger.py --check" in command)
    refresh_index = next(i for i, command in enumerate(commands) if "generate_production_evidence_ledger.py" in command and "--check" not in command)
    downstream_index = next(i for i, command in enumerate(commands) if "build_manufacturer_marketplace_catalog.py" in command)
    assert check_index < refresh_index < downstream_index
