"""Guard the Bootcamp workflow's 65-lane model-kit generation and evidence upload."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github/workflows/buddy-bootcamp-curriculum.yml"


def test_bootcamp_generates_and_checks_all_division_model_kit_blueprints():
    text = WORKFLOW.read_text(encoding="utf-8")
    assert "tools/build_division_learning_model_kits.py" in text
    assert "python tools/build_division_learning_model_kits.py --write" in text
    assert "python tools/build_division_learning_model_kits.py --check" in text
    assert "tests.test_division_learning_model_kits" in text
    assert "config/generated/division-learning-model-kits/" in text
    assert "config/dreamco-universal-division-mastery-contract.json" in text
