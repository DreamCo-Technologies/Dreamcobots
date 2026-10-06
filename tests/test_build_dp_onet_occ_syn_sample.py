"""Offline tests for tools/build_dp_onet_occ_syn_sample.py (DP-ONET-OCC-SYN 0.0.2 sample).

The builder needs the pinned O*NET 31.0 zip to run end to end; these tests cover what can be checked
without it: the committed rows still match the row schema and the card renderer, the zip pin is
enforced, the declared attribution satisfies the license gate, and nothing is marked sellable.
"""
from __future__ import annotations

import io
import json
import re
import sys
import zipfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools import build_dp_onet_occ_syn_sample as builder  # noqa: E402
from tools.minimal_json_schema import load_schema, validate  # noqa: E402

PKG = ROOT / "data" / "dreamco_knowledge" / "packages" / builder.SKU / builder.SAMPLE_VERSION
ROWS = PKG / "sample" / "occupations.jsonl"
CARDS = PKG / "sample" / "occupation_cards.md"
ROW_SCHEMA = ROOT / "schemas" / "dp_onet_occ_syn.row.schema.json"
GATE_CONFIG = ROOT / "config" / "license_provenance_gate.json"


def committed_rows() -> list[dict]:
    return [json.loads(line) for line in ROWS.read_text(encoding="utf-8").splitlines() if line.strip()]


def test_committed_rows_match_row_schema():
    rows = committed_rows()
    assert rows, "sample has no rows"
    schema = load_schema(ROW_SCHEMA)
    for row in rows:
        assert validate(row, schema) == [], row.get("onet_soc_code")


def test_committed_rows_are_unique_and_sorted():
    codes = [row["onet_soc_code"] for row in committed_rows()]
    assert codes == sorted(codes)
    assert len(codes) == len(set(codes))


def test_cards_are_reproducible_from_committed_rows():
    assert builder.render_cards(committed_rows()) == CARDS.read_text(encoding="utf-8")


def test_cards_end_with_full_attribution():
    assert CARDS.read_text(encoding="utf-8").rstrip().endswith(builder.ATTRIBUTION_TEXT)


def test_declared_attribution_satisfies_license_gate_rules():
    rules = json.loads(GATE_CONFIG.read_text(encoding="utf-8"))["license_rules"]
    required = [el for rule in rules for el in rule.get("required_in_declared_attribution", [])]
    assert required, "gate config declares no package-level attribution elements"
    for el in required:
        assert re.search(el["pattern"].replace("{version}", re.escape(builder.ONET_VERSION)), builder.ATTRIBUTION_TEXT), el["id"]


def test_candidate_record_is_never_sellable_by_default():
    cand = builder.candidate_record()
    assert cand["scorecard_score"] is None
    assert cand["owner_approval"] is None
    assert cand["flags"] == []
    assert "sellable" not in json.dumps(cand).lower()


def test_zip_pin_is_enforced_before_parsing(tmp_path):
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        for name in builder.FILES:
            zf.writestr(builder.MEMBER_PREFIX + name, "O*NET-SOC Code\n")
    fake = tmp_path / builder.ZIP_NAME
    fake.write_bytes(buf.getvalue())
    with pytest.raises(SystemExit, match="refusing to build"):
        builder.load_tables(fake, "0" * 64)
    tables, hashes = builder.load_tables(fake, builder.sha256_bytes(fake.read_bytes()))
    assert set(tables) == set(builder.FILES) == set(hashes)


def test_package_pins_the_onet_zip():
    sha = builder.pinned_zip_sha(PKG / "provenance_manifest.json")
    assert re.fullmatch(r"[0-9a-f]{64}", sha)
