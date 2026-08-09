import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools.library_specialist_registry import find_specialists, load_registry, validate_registry


def test_seed_registry_is_valid():
    records = load_registry()
    assert validate_registry(records) == []


def test_seed_registry_ids_are_unique():
    records = load_registry()
    ids = [record["id"] for record in records]
    assert len(ids) == len(set(ids))


def test_certified_record_requires_evidence():
    record = {
        "id": "python:example",
        "ecosystem": "python",
        "package": "example",
        "official_sources": ["https://example.com"],
        "certification": {"status": "certified"},
        "evidence": [],
    }
    errors = validate_registry([record])
    assert any("require evidence" in error for error in errors)


def test_search_by_capability():
    records = load_registry()
    matches = find_specialists(records, "tabular")
    assert any(record["id"] == "python:pandas" for record in matches)


def test_seed_file_is_json():
    path = ROOT / "data" / "library_specialists.seed.json"
    assert isinstance(json.loads(path.read_text(encoding="utf-8")), list)
