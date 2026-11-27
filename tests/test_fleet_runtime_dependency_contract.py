from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[1]


def test_fleet_runtime_full_audit_installs_scipy_for_media_imports():
    workflow = yaml.safe_load((ROOT / ".github/workflows/fleet-runtime-truth.yml").read_text(encoding="utf-8"))
    steps = workflow["jobs"]["full-audit"]["steps"]
    install = next(step["run"] for step in steps if "pip install" in str(step.get("run", "")))
    assert '"scipy>=1.11,<2"' in install
