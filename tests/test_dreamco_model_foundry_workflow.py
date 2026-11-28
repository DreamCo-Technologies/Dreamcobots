"""Validate the DreamCo model-foundry workflow is parseable and runnable."""
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github/workflows/dreamco-model-foundry-kits.yml"


def test_model_foundry_workflow_has_valid_yaml_and_buyer_kit_job():
    workflow = yaml.safe_load(WORKFLOW.read_text(encoding="utf-8"))
    assert "buyer-kit-contracts" in workflow["jobs"]
    steps = workflow["jobs"]["buyer-kit-contracts"]["steps"]
    assert any(step.get("name") == "Compile foundry scripts" for step in steps)
    catalog_step = next(step for step in steps if step.get("name") == "Validate catalog count")
    assert "python - <<'PY'" in catalog_step["run"]
    assert "Validated 250 unique untrained SKUs" in catalog_step["run"]
