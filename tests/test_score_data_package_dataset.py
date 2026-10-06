"""Tests for the dataset QA scorecard (tools/score_data_package_dataset.py), the DP-ONET-OCC-SYN sample generator
(tools/build_dp_onet_occ_syn_sample.py), the committed 0.0.2 sample package, and the 0.1.1 declared-attribution rule
in tools/license_provenance_gate.py.

The O*NET fixtures below are tiny synthetic tables with the O*NET 31.0 column layout; they are not O*NET data."""
import copy
import csv
import hashlib
import io
import json
import sys
import zipfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools import build_dp_onet_occ_syn_sample as gen  # noqa: E402
from tools import build_sellable_data_package as builder  # noqa: E402
from tools import license_provenance_gate as gate  # noqa: E402
from tools import score_data_package_dataset as qa  # noqa: E402
from tools.minimal_json_schema import load_schema, validate  # noqa: E402

PKG2 = ROOT / "data" / "dreamco_knowledge" / "packages" / "DP-ONET-OCC-SYN" / "0.0.2"
ASSET2 = PKG2 / "assets" / gen.ASSET_ID
RATING_COLS = ["O*NET-SOC Code", "Element ID", "Element Name", "Scale ID", "Data Value", "N", "Recommend Suppress",
               "Date", "Domain Source"]

OCCS = [  # code, title, description, job zone
    ("11-1011.00", "Fixture Chief Planner", "Determines and formulates fixture policies and provides overall direction for imaginary organizations.", 5),
    ("11-3031.00", "Fixture Ledger Manager", "Plans and coordinates imaginary ledger reviews across several invented departments every quarter.", 4),
    ("11-9199.00", "Fixture Site Coordinator", "Coordinates invented site visits and keeps synthetic schedules for pretend teams in a test.", 3),
    ("15-1252.00", "Fixture Code Builder", "Writes and tests invented programs that run only inside this unit test fixture environment.", 4),
    ("15-1211.00", "Fixture Systems Reviewer", "Reviews made up system requirements and drafts test plans for synthetic computer networks.", 4),
    ("15-2011.00", "Fixture Risk Counter", "Counts invented risks using made up statistics for imaginary insurance products and plans.", 5),
]
KNOWLEDGE = [("2.C.1.a", "Administration and Management"), ("2.C.1.b", "Administrative"), ("2.C.3.a", "Computers and Electronics"),
             ("2.C.4.a", "Mathematics"), ("2.C.2.a", "Production and Processing"), ("2.C.7.a", "English Language")]
SKILLS = [("2.A.1.a", "Reading Comprehension"), ("2.A.1.b", "Active Listening"), ("2.A.2.a", "Critical Thinking"),
          ("2.B.1.a", "Social Perceptiveness")]
ACTIVITIES = [("4.A.1.a.1", "Getting Information"), ("4.A.2.a.1", "Judging Qualities"), ("4.A.4.a.1", "Interpreting Information"),
              ("4.A.3.a.1", "Performing General Physical Activities"), ("4.A.3.b.1", "Working with Computers"),
              ("4.A.4.c.1", "Performing Administrative Activities")]


def _val(code: str, eid: str) -> str:
    h = int(hashlib.sha256(f"{code}|{eid}".encode()).hexdigest()[:8], 16)
    return f"{1.5 + (h % 340) / 100:.2f}"  # 1.50 .. 4.89


def _csv(header: list[str], rows: list[list]) -> bytes:
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator="\n")
    w.writerow(header)
    w.writerows(rows)
    return buf.getvalue().encode("utf-8")


def _ratings(elements, sources=("Incumbent", "Analyst")) -> bytes:
    rows = []
    for code, *_ in OCCS:
        for i, (eid, name) in enumerate(elements):
            rows.append([code, eid, name, "IM", _val(code, eid), "25", "N", "08/2025", sources[i % len(sources)]])
            rows.append([code, eid, name, "LV", "3.00", "25", "N", "08/2025", sources[i % len(sources)]])
    return _csv(RATING_COLS, rows)


def fixture_members() -> dict[str, bytes]:
    tasks = []
    for n, (code, title, *_rest) in enumerate(OCCS):
        tasks += [[code, str(100 + 3 * n), f"Handle fixture duty alpha number {n} for the {title.lower()} role in tests.", "Core"],
                  [code, str(101 + 3 * n), f"Record fixture duty beta number {n} in a pretend tracking sheet.", "Core"],
                  [code, str(102 + 3 * n), f"Occasionally assist with fixture duty gamma number {n}.", "Supplemental"]]
    return {
        "occupation_data.csv": _csv(["O*NET-SOC Code", "Title", "Description"], [[c, t, d] for c, t, d, _ in OCCS]),
        "job_zones.csv": _csv(["O*NET-SOC Code", "Title", "Job Zone"], [[c, t, str(z)] for c, t, _, z in OCCS]),
        "knowledge.csv": _ratings(KNOWLEDGE),
        "essential_skills.csv": _ratings(SKILLS),
        "work_activities.csv": _ratings(ACTIVITIES),
        "task_statements.csv": _csv(["O*NET-SOC Code", "Task ID", "Task", "Task Type"], tasks),
    }


def write_zip(path: Path, members: dict[str, bytes]) -> Path:
    with zipfile.ZipFile(path, "w") as zf:
        for name in sorted(members):  # fixed order + fixed date => stable bytes
            info = zipfile.ZipInfo(gen.MEMBER_PREFIX + name, date_time=(2026, 10, 5, 0, 0, 0))
            zf.writestr(info, members[name])
    return path


def write_pin(pkg: Path, zip_path: Path) -> Path:
    pkg.mkdir(parents=True, exist_ok=True)
    pm = {"planned_sources": [{"source_id": "onet_db_31_0", "downloads": [
        {"name": gen.ZIP_NAME, "sha256": hashlib.sha256(zip_path.read_bytes()).hexdigest()}]}]}
    p = pkg / "provenance_manifest.json"
    p.write_text(json.dumps(pm), encoding="utf-8")
    return p


@pytest.fixture
def built(tmp_path):
    """A fixture O*NET zip, a pinned package dir and a generated sample: (pkg, zip_path, build_result)."""
    z = write_zip(tmp_path / gen.ZIP_NAME, fixture_members())
    pkg = tmp_path / "pkg"
    pm = write_pin(pkg, z)
    res = gen.build(z, pkg, pm, "2026-10-05T16:52:00-05:00")
    return pkg, z, res


def rows_of(pkg: Path) -> list[dict]:
    return [json.loads(line) for line in (pkg / "sample" / "occupations.jsonl").read_text(encoding="utf-8").splitlines()]


def write_rows(pkg: Path, rows: list[dict]) -> None:
    (pkg / "sample" / "occupations.jsonl").write_text("".join(json.dumps(r, sort_keys=True) + "\n" for r in rows), encoding="utf-8")


def status(report: dict, cid: str) -> str:
    return next(c for c in report["checks"] if c["id"] == cid)["status"]


# ------------------------------------------------------------------ generator

def test_generator_refuses_unpinned_zip(tmp_path):
    z = write_zip(tmp_path / gen.ZIP_NAME, fixture_members())
    with pytest.raises(SystemExit, match="refusing to build"):
        gen.load_tables(z, "0" * 64)


def test_selection_is_stratified_and_deterministic(tmp_path):
    z = write_zip(tmp_path / gen.ZIP_NAME, fixture_members())
    tables, _ = gen.load_tables(z, hashlib.sha256(z.read_bytes()).hexdigest())
    picked = gen.select_occupations(tables)
    assert picked == gen.select_occupations(tables)
    assert len(picked) == 4 and sorted({c[:2] for c in picked}) == ["11", "15"]
    assert sum(c.startswith("11") for c in picked) == 2


def test_suppressed_ratings_are_excluded_and_counted(tmp_path):
    members = fixture_members()
    text = members["knowledge.csv"].decode()
    code = OCCS[0][0]
    # Suppress the highest IM knowledge rating of the first occupation.
    best = max(KNOWLEDGE, key=lambda e: float(_val(code, e[0])))
    line = f"{code},{best[0]},{best[1]},IM,{_val(code, best[0])},25,N"
    assert line in text
    members["knowledge.csv"] = text.replace(line, line[:-1] + "Y").encode()
    z = write_zip(tmp_path / gen.ZIP_NAME, members)
    tables, hashes = gen.load_tables(z, hashlib.sha256(z.read_bytes()).hexdigest())
    row = gen.build_row(code, tables, hashes)
    assert best[0] not in [e["element_id"] for e in row["top_knowledge"]]
    assert row["data_confidence"]["suppressed_ratings_excluded"] == 1


def test_rows_carry_attribution_license_split_and_no_verbatim_text(built):
    pkg, _, res = built
    rows = rows_of(pkg)
    assert len(rows) == res["rows"] == 4
    schema = load_schema(ROOT / "schemas" / "dp_onet_occ_syn.row.schema.json")
    descriptions = {c: d for c, _, d, _ in OCCS}
    for r in rows:
        assert validate(r, schema) == []
        assert r["license"]["onet_derived_fields"] and r["license"]["dreamco_fields"]
        assert "O*NET 31.0 Database" in r["license"]["attribution"]
        assert descriptions[r["onet_soc_code"]] not in json.dumps(r)
        assert {s["source_id"] for s in r["source_refs"]} == {"onet_db_31_0", "dreamco_synthesis"}
    cards = (pkg / "sample" / "occupation_cards.md").read_text(encoding="utf-8")
    for needle in ("O*NET 31.0 Database", "CC BY 4.0", "O*NET\u00ae is a trademark of USDOL/ETA",
                   "has not approved, endorsed, or tested these modifications"):
        assert needle in cards


def test_generated_asset_records_stay_below_sale(built):
    pkg, _, _ = built
    adir = pkg / "assets" / gen.ASSET_ID
    prov = json.loads((adir / "provenance.json").read_text())
    cand = json.loads((adir / "candidate.json").read_text())
    asset = json.loads((adir / "asset.json").read_text())
    assert validate(prov, load_schema(ROOT / "schemas" / "data_package_asset_provenance.schema.json")) == []
    assert cand["owner_approval"] is None and cand["scorecard_score"] is None
    assert all(v == [] for v in asset["validation_evidence_ids"].values())
    assert "creativecommons.org/licenses/by/4.0" in prov["attribution_text"]
    assert "O*NET\u00ae is a trademark of USDOL/ETA" in prov["attribution_text"]


# ------------------------------------------------------------------ QA scorecard

def test_clean_fixture_sample_passes(built):
    pkg, z, _ = built
    report = qa.score(pkg, onet_zip=z, evaluated_at="2026-10-05T17:00:00-05:00")
    assert report["overall_status"] in ("pass", "warn"), report["failed_checks"]
    for cid in ("completeness", "schema_validity", "referential_integrity", "deduplication", "value_ranges",
                "freshness_version_match", "provenance_coverage"):
        assert status(report, cid) == "pass", (cid, next(c for c in report["checks"] if c["id"] == cid)["reasons"])
    assert report["failed_checks"] == []
    assert "NOT a sale approval" in report["truth_boundary"]


def test_csv_dir_reference_also_works(built, tmp_path):
    pkg, _, _ = built
    d = tmp_path / "csv"
    d.mkdir()
    for name, data in fixture_members().items():
        (d / name).write_bytes(data)
    report = qa.score(pkg, onet_csv_dir=d)
    assert status(report, "referential_integrity") == "pass"


def test_no_reference_is_not_run_and_fails_overall(built):
    pkg, _, _ = built
    report = qa.score(pkg)
    assert status(report, "referential_integrity") == "not_run"
    assert report["overall_status"] == "fail"
    assert "referential_integrity" in report["failed_checks"]


def test_unpinned_reference_zip_is_rejected(built, tmp_path):
    pkg, _, _ = built
    members = fixture_members()
    members["occupation_data.csv"] += b"99-9999.00,Extra,Extra row\n"
    other = write_zip(tmp_path / "other.zip", members)
    report = qa.score(pkg, onet_zip=other)
    assert status(report, "referential_integrity") == "not_run"
    assert any("reference rejected" in n for n in report["inputs"]["reference_notes"])


def test_unknown_code_and_wrong_value_fail_referential_integrity(built):
    pkg, z, _ = built
    rows = rows_of(pkg)
    rows[0]["onet_soc_code"] = "99-0000.00"
    rows[0]["record_id"] = rows[0]["record_id"].rsplit("/", 1)[0] + "/99-0000.00"
    rows[1]["top_knowledge"][0]["importance"] = 4.99
    write_rows(pkg, rows)
    report = qa.score(pkg, onet_zip=z)
    ref = next(c for c in report["checks"] if c["id"] == "referential_integrity")
    assert ref["status"] == "fail"
    assert ref["metrics"]["codes_resolve"] < 1 and ref["metrics"]["values_match_source"] < 1
    assert report["overall_status"] == "fail"


def test_duplicate_rows_fail_dedup(built):
    pkg, z, _ = built
    rows = rows_of(pkg)
    write_rows(pkg, rows + [copy.deepcopy(rows[0])])
    report = qa.score(pkg, onet_zip=z)
    assert status(report, "deduplication") == "fail"
    assert report["overall_status"] == "fail"


def test_out_of_range_values_fail(built):
    pkg, z, _ = built
    rows = rows_of(pkg)
    rows[0]["capability_lenses"]["digital_and_records"] = 1.7
    rows[1]["job_zone"] = 9
    write_rows(pkg, rows)
    report = qa.score(pkg, onet_zip=z)
    vr = next(c for c in report["checks"] if c["id"] == "value_ranges")
    assert vr["status"] == "fail" and vr["metrics"]["values_in_range"] == 0.5


def test_inconsistent_preparation_band_fails(built):
    pkg, z, _ = built
    rows = rows_of(pkg)
    for r in rows:
        r["preparation_band"] = "extensive" if r["job_zone"] != 5 else "medium"
    write_rows(pkg, rows)
    assert status(qa.score(pkg, onet_zip=z), "value_ranges") == "fail"


def test_missing_provenance_ref_fails(built):
    pkg, z, _ = built
    rows = rows_of(pkg)
    rows[2]["source_refs"] = [s for s in rows[2]["source_refs"] if s.get("file") != "job_zones.csv"]
    write_rows(pkg, rows)
    report = qa.score(pkg, onet_zip=z)
    pc = next(c for c in report["checks"] if c["id"] == "provenance_coverage")
    assert pc["status"] == "fail"
    assert any("job_zone has no pinned source_ref" in r for r in pc["reasons"])


def test_tampered_member_hash_fails_freshness(built):
    pkg, z, _ = built
    rows = rows_of(pkg)
    for s in rows[0]["source_refs"]:
        if s.get("file") == "knowledge.csv":
            s["file_sha256"] = "f" * 64
    write_rows(pkg, rows)
    assert status(qa.score(pkg, onet_zip=z), "freshness_version_match") == "fail"


def test_wrong_source_version_fails_freshness(built):
    pkg, z, _ = built
    rows = rows_of(pkg)
    rows[0]["source_version"] = "O*NET 30.3"
    write_rows(pkg, rows)
    assert status(qa.score(pkg, onet_zip=z), "freshness_version_match") == "fail"


def test_verbatim_onet_text_fails_synthesis(built):
    pkg, z, _ = built
    rows = rows_of(pkg)
    code = rows[0]["onet_soc_code"]
    desc = next(d for c, _, d, _ in OCCS if c == code)
    rows[0]["dreamco_synthesis"]["analysis"]["improve"].append("Copied: " + desc)
    write_rows(pkg, rows)
    report = qa.score(pkg, onet_zip=z)
    syn = next(c for c in report["checks"] if c["id"] == "synthesis_perspective")
    assert syn["status"] == "fail" and syn["metrics"]["no_verbatim_onet_text"] < 1
    assert any("verbatim" in r for r in syn["reasons"])


def test_unparseable_line_fails_schema(built):
    pkg, z, _ = built
    with (pkg / "sample" / "occupations.jsonl").open("a", encoding="utf-8") as fh:
        fh.write("{not json\n")
    report = qa.score(pkg, onet_zip=z)
    assert status(report, "schema_validity") == "fail"


def test_cli_exit_codes(built, tmp_path, capsys):
    pkg, z, _ = built
    out = tmp_path / "qa.json"
    assert qa.main([str(pkg), "--onet-zip", str(z), "--out", str(out), "--evaluated-at", "2026-10-05T17:00:00-05:00"]) == 0
    assert json.loads(out.read_text())["evaluated_at"] == "2026-10-05T17:00:00-05:00"
    assert qa.main([str(pkg)]) == 1
    assert qa.main([str(tmp_path / "missing")]) == 2
    capsys.readouterr()


def test_scorecard_config_is_consistent():
    cfg = json.loads(qa.CONFIG.read_text(encoding="utf-8"))
    weights = sum(c["weight"] for c in cfg["checks"].values())
    assert abs(weights - 1.0) < 1e-9
    required = {"completeness", "schema_validity", "referential_integrity", "deduplication", "value_ranges",
                "freshness_version_match", "provenance_coverage", "synthesis_perspective"}
    assert set(cfg["checks"]) == required
    for c in cfg["checks"].values():
        for m in c["metrics"].values():
            assert 0 <= m["warn_min"] <= m["pass_min"] <= 1
    assert {f.__name__ for f in qa.CHECKS} and len(qa.CHECKS) == len(required)


# ------------------------------------------------------------------ committed 0.0.2 package

def test_package_002_is_populated_valid_and_not_for_sale(capsys):
    manifest = json.loads((PKG2 / "manifest.json").read_text(encoding="utf-8"))
    assert validate(manifest, load_schema(ROOT / "schemas" / "data_package.manifest.schema.json")) == []
    assert manifest["version"] == "0.0.2" and manifest["included_asset_ids"] == [gen.ASSET_ID]
    assert manifest["scorecard_score"] is None and manifest["commercial_tier"] is None
    assert manifest["stripe_price_id"] is None and manifest["sales_channel"] == "none"
    assert manifest["release_level"] != "sellable_verified"
    assert "price" not in json.dumps(manifest).lower().replace("stripe_price_id", "").replace("no price", "")
    rows = rows_of(PKG2)
    assert 25 <= len(rows) <= 50
    assert builder.main([str(PKG2), "--structure-only"]) == 0
    assert builder.main([str(PKG2)]) == 1  # sellable build refuses
    capsys.readouterr()


def test_package_002_gate_record_is_private_use_only():
    g = json.loads((ASSET2 / "license_gate.json").read_text(encoding="utf-8"))
    assert g["outcome"] == "approved_for_private_use"
    assert g["outcome"] != "approved_for_sale"
    assert set(g["failed_checks"]) == {"scorecard_threshold", "synthesis_asset_record", "owner_approval"}
    manifest = json.loads((PKG2 / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["assets"][0]["license_gate_outcome"] == g["outcome"]
    assert manifest["license_gate_status"] == "fail"


def test_package_002_gate_rerun_matches_and_rights_checks_pass(tmp_path, monkeypatch):
    monkeypatch.setattr(gate, "DEFAULT_REPO_ROOT", tmp_path)
    report = gate.evaluate(ASSET2, asset_root=PKG2, evaluated_at="2026-10-05T17:00:00-05:00")
    assert report["outcome"] == "approved_for_private_use"
    for cid in ("provenance_schema_conformance", "sources_pinned", "ownership_class_valid",
                "commercial_and_redistribution_rights", "attribution_present", "asset_file_integrity"):
        assert next(c for c in report["checks"] if c["id"] == cid)["status"] == "pass", cid


def test_package_002_files_keep_attribution():
    for name in ("LICENSE", "ATTRIBUTION.md", "dataset_card.md"):
        text = " ".join((PKG2 / name).read_text(encoding="utf-8").split())
        assert "O*NET 31.0 Database" in text, name
        assert "USDOL/ETA" in text, name
        assert "creativecommons.org/licenses/by/4.0" in text, name
    assert "has not approved, endorsed, or tested" in (PKG2 / "ATTRIBUTION.md").read_text(encoding="utf-8")


def test_package_002_quality_reports_are_honest():
    qr = json.loads((PKG2 / "quality_report.json").read_text(encoding="utf-8"))
    br = json.loads((PKG2 / "benchmark_report.json").read_text(encoding="utf-8"))
    assert qr["status"] != "pass" and br["status"] == "not_run"
    assert qr["scorecard"]["score"] is None


def test_package_001_skeleton_keeps_attribution_files():
    p1 = PKG2.parent / "0.0.1"
    assert (p1 / "ATTRIBUTION.md").is_file() and (p1 / "MODIFICATIONS.md").is_file()
    lic = " ".join((p1 / "LICENSE").read_text(encoding="utf-8").split()).replace("O*NET(R)", "O*NET\u00ae")
    assert "O*NET\u00ae is a trademark of USDOL/ETA" in lic
    assert "has not approved, endorsed, or tested these modifications" in lic


# ------------------------------------------------------------------ gate 0.1.1 declared attribution

def _gate_on_copy(tmp_path, monkeypatch, edit) -> dict:
    import shutil
    monkeypatch.setattr(gate, "DEFAULT_REPO_ROOT", tmp_path)
    root = tmp_path / "pkg"
    shutil.copytree(PKG2 / "sample", root / "sample")
    adir = root / "assets" / gen.ASSET_ID
    shutil.copytree(ASSET2, adir)
    prov = json.loads((adir / "provenance.json").read_text(encoding="utf-8"))
    edit(prov)
    (adir / "provenance.json").write_text(json.dumps(prov), encoding="utf-8")
    return gate.evaluate(adir, asset_root=root, evaluated_at="2026-10-05T17:00:00-05:00")


def test_declared_attribution_without_license_link_fails(tmp_path, monkeypatch):
    def edit(p):
        p["attribution_text"] = p["attribution_text"].replace(" (https://creativecommons.org/licenses/by/4.0/)", "")
    report = _gate_on_copy(tmp_path, monkeypatch, edit)
    att = next(c for c in report["checks"] if c["id"] == "attribution_present")
    assert att["status"] == "fail"
    assert any("license_link" in r for r in att["reasons"])
    assert report["outcome"] == "approved_for_private_use"


def test_declared_attribution_without_trademark_notice_fails(tmp_path, monkeypatch):
    def edit(p):
        p["attribution_text"] = p["attribution_text"].replace("O*NET\u00ae is a trademark of USDOL/ETA. ", "")
    report = _gate_on_copy(tmp_path, monkeypatch, edit)
    att = next(c for c in report["checks"] if c["id"] == "attribution_present")
    assert att["status"] == "fail"
    assert any("trademark_notice" in r for r in att["reasons"])


def test_gate_config_declares_new_requirements():
    cfg = json.loads((ROOT / "config" / "license_provenance_gate.json").read_text(encoding="utf-8"))
    rules = {r["id"]: r for r in cfg["license_rules"]}
    onet = next(r for rid, r in rules.items() if "onet" in rid and "crosswalk" not in rid)
    assert {e["id"] for e in onet["required_in_declared_attribution"]} == {"license_link", "trademark_notice"}
    assert gate.GATE_VERSION == "0.1.1"
