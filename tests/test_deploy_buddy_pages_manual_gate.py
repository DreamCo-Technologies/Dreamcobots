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

def test_production_evidence_ledger_is_regenerated_before_consistency_check():
    workflow = yaml.safe_load((ROOT / ".github/workflows/deploy-buddy-pages.yml").read_text(encoding="utf-8"))
    commands = "\n".join(str(step.get("run", "")) for step in workflow["jobs"]["build"]["steps"])
    refresh_position = commands.index("python3 tools/generate_production_evidence_ledger.py\n")
    check_position = commands.index("python3 tools/generate_production_evidence_ledger.py --check")
    downstream_position = commands.index("build_manufacturer_marketplace_catalog.py")
    assert refresh_position < check_position < downstream_position
