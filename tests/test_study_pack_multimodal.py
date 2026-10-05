"""Offline structure checks for study_packs/multimodal (no network, no weights)."""
import json
from pathlib import Path

import pytest

P = Path(__file__).resolve().parents[1] / "study_packs" / "multimodal"
pytestmark = pytest.mark.skipif(not P.exists(), reason="multimodal study pack not present")


def _j(name):
    return json.loads((P / name).read_text())


def test_layout():
    for f in ["README.md", "index.json", "sources.json", "evals.json", "drill_runner.py", "recipes/av_trainer_handoff.yaml"]:
        assert (P / f).exists(), f


def test_sources_pinned_and_licensed():
    src = _j("sources.json")
    assert src["train_allowed"] is False
    for m in src["models"]:
        assert len(m["revision"]) == 40, m["repo_id"]
        assert m["license"] and m["license"] != "TBD"
        if m["license"].startswith("cc-by-nc"):
            assert m["commercial_ok"] is False


def test_evals_reference_known_models():
    ids = {m["repo_id"] for m in _j("sources.json")["models"]}
    ev = _j("evals.json")
    assert ev["min_native_pass_rate"] >= 0.7
    for d in ev["drills"]:
        assert d["model"] in ids


def test_evidence_schema_if_present():
    f = P / "evidence" / "latest.json"
    if not f.exists():
        pytest.skip("no evidence yet")
    rep = json.loads(f.read_text())
    assert rep["total"] == len(rep["drills"])
    for d in rep["drills"]:
        assert d["status"] in {"PASS", "FAIL", "ERROR", "BLOCKED"}
