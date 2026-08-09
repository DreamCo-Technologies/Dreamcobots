import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "tools" / "generate_library_specialist_registry.py"

spec = importlib.util.spec_from_file_location("library_specialist_registry", MODULE_PATH)
assert spec and spec.loader
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def test_registry_has_unique_specialist_ids():
    registry = module.build_registry()
    ids = [item["id"] for item in registry["specialists"]]
    assert len(ids) == len(set(ids))


def test_registry_never_false_certifies_discovery_records():
    registry = module.build_registry()
    assert registry["truthContract"]["recordMeansCertified"] is False
    assert registry["summary"]["certified"] == 0
    assert all(item["certified"] is False for item in registry["specialists"])
    assert all(item["evidenceRequiredForCertification"] is True for item in registry["specialists"])


def test_existing_javascript_dependencies_become_specialists():
    registry = module.build_registry()
    ids = {item["id"] for item in registry["specialists"]}
    assert "javascript:react" in ids
    assert "javascript:express" in ids
    assert "javascript:openai" in ids


def test_python_seed_has_data_and_web_specialists():
    registry = module.build_registry()
    ids = {item["id"] for item in registry["specialists"]}
    assert "python:numpy" in ids
    assert "python:pandas" in ids
    assert "python:fastapi" in ids


def test_global_ecosystem_targets_are_broad():
    registry = module.build_registry()
    targets = {item["id"] for item in registry["ecosystemDiscoveryTargets"]}
    for expected in {"python", "javascript", "java", "dotnet", "rust", "go", "ruby", "php", "dart", "swift", "cpp", "r", "julia", "haskell", "elixir", "terraform", "embedded"}:
        assert expected in targets
