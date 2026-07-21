from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
ORIGINAL_BOTS_DIR = ROOT / "original-bots"


def test_original_recovered_systems_have_local_code():
    files = [
        path
        for path in ORIGINAL_BOTS_DIR.rglob("*.py")
        if path.name != "__init__.py"
        and ("bot" in path.stem.lower() or "agent" in path.stem.lower() or "orchestrator" in path.stem.lower())
    ]
    assert files, "recovered original bot or agent code must be preserved"
    for path in files:
        text = path.read_text(encoding="utf-8", errors="ignore")
        assert text.strip(), path


def test_original_recovered_systems_stay_reference_until_promoted():
    marker = ORIGINAL_BOTS_DIR / "README.md"
    assert ORIGINAL_BOTS_DIR.exists()
    if marker.exists():
        text = marker.read_text(encoding="utf-8", errors="ignore").lower()
        assert "archive" in text or "original" in text or "recovered" in text
