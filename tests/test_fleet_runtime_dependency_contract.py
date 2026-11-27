from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]


def test_fleet_runtime_full_audit_installs_scipy_from_declared_learning_requirements():
    workflow = yaml.safe_load(
        (ROOT / ".github/workflows/fleet-runtime-truth.yml").read_text(encoding="utf-8")
    )
    steps = workflow["jobs"]["full-audit"]["steps"]
    install = next(
        str(step["run"])
        for step in steps
        if "pip install" in str(step.get("run", ""))
    )
    requirements = (ROOT / "requirements-buddy-learning.txt").read_text(encoding="utf-8")
    assert "-r requirements-buddy-learning.txt" in install
    assert "soundfile>=0.12,<1" in install
    assert "Pillow>=10,<12" in install
    assert "scipy>=1.11,<2" in requirements
    assert "cryptography>=42,<50" in requirements
