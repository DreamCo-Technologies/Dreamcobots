import csv, hashlib, json, os, pathlib, re
import pandas as pd
import pytest
ROOT = pathlib.Path(__file__).resolve().parents[1]
import sys; sys.path.insert(0, str(ROOT)); import build

PLANS = sorted((ROOT / "study_plans").glob("*.md"))
SCHEMAS = {"provenance": "data_package_asset_provenance.schema.json",
           "license_gate": "data_package_license_gate.schema.json",
           "asset": "data_package_synthesis_asset.schema.json"}


def schema_dir():
    """Live DreamCo schemas if present (env, repo root, merchant checkout), else the vendored snapshot in tests/schemas."""
    for d in [os.environ.get("DREAMCO_SCHEMAS_DIR"), ROOT.parents[1] / "schemas", "/workspace/dp-merchant/schemas"]:
        if d and all((pathlib.Path(d) / f).is_file() for f in SCHEMAS.values()):
            return pathlib.Path(d)
    return ROOT / "tests" / "schemas"


def validator(kind):
    jsonschema = pytest.importorskip("jsonschema")
    schema = json.loads((schema_dir() / SCHEMAS[kind]).read_text())
    return jsonschema.Draft202012Validator(schema, format_checker=jsonschema.FormatChecker())


def sha(p):
    return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()


def sidecar(plan):
    return plan.with_suffix("")


def test_links_exist_in_official_sources():
    cw = build.load_crosswalk(); pairs = set(zip(cw.cip, cw.soc))
    occ = set(pd.read_csv(ROOT/"raw/occupation_data.csv", dtype=str)["O*NET-SOC Code"])
    rows = list(csv.DictReader(open(ROOT/"data/major_to_onet.csv")))
    assert len(rows) > 0
    for r in rows:
        assert (r["cip_code"], r["onet_soc_code"]) in pairs
        assert r["onet_soc_code"] in occ


def test_exactly_27_majors():
    assert len(json.loads((ROOT/"data/majors_selected.json").read_text())) == 27 == len(PLANS)


def test_every_plan_has_provenance():
    assert len(PLANS) >= 20
    for p in PLANS:
        t = p.read_text(); assert "**Provenance.**" in t and "CC BY 4.0" in t and "not O*NET data" in t


def test_footer_trademark_modification_and_version_statements():
    for p in PLANS:
        t = p.read_text()
        assert "O*NET\u00ae is a trademark of USDOL/ETA." in t, p.name
        assert "DreamCo has modified all or some of this information" in t, p.name
        assert "USDOL/ETA has not approved, endorsed, or tested these modifications" in t, p.name
        assert "O*NET 31.0 Database" in t and "Pinned version: O*NET 31.0" in t, p.name
        assert re.search(r"crosswalk[^.]*CC BY 4\.0", t), p.name
        assert "Essential Skills and Transferable Skills" in t, p.name


def test_sources_pinned_in_sources_md_match_raw_files():
    pins = build.load_pins()  # raises if any raw file differs from raw/SOURCES.md
    for name in build.SOURCE_FILES:
        assert sha(ROOT/"raw"/name) == pins[name][0]
        assert re.match(r"\d{4}-\d{2}-\d{2}$", pins[name][1])


@pytest.mark.parametrize("plan", PLANS, ids=[p.stem for p in PLANS])
def test_gate_files_exist_and_validate(plan):
    d = sidecar(plan)
    for f in ["provenance.json", "license_gate.json", "asset.json", "candidate.json", "plan.json"]:
        assert (d / f).is_file(), f"{d.name}/{f} missing"
    for kind, f in [("provenance", "provenance.json"), ("license_gate", "license_gate.json"), ("asset", "asset.json")]:
        errs = sorted(validator(kind).iter_errors(json.loads((d / f).read_text())), key=str)
        assert not errs, f"{d.name}/{f}: {[e.message for e in errs][:5]}"


@pytest.mark.parametrize("plan", PLANS, ids=[p.stem for p in PLANS])
def test_provenance_content_and_hashes(plan):
    d = sidecar(plan)
    prov = json.loads((d / "provenance.json").read_text())
    asset = json.loads((d / "asset.json").read_text())
    cand = json.loads((d / "candidate.json").read_text())
    pins = build.load_pins()
    assert prov["integrity_hash"] == f"sha256:{sha(plan)}" == asset["integrity_hash"]
    for f in prov["asset_files"]:
        assert sha(ROOT / f["path"]) == f["sha256"], f["path"]
    for layer in ("human_layer", "machine_layer"):
        assert sha(ROOT / asset[layer]["path"]) == asset[layer]["sha256"]
    assert prov["ownership_class"] == asset["ownership_class"] == cand["ownership_class"]
    for s in prov["sources"]:
        assert s["ownership_class"] and s["license"] == "CC BY 4.0"
        assert s["commercial_use_allowed"] is True and s["redistribution_allowed"] is True
        hashes = [(f["name"], f["sha256"]) for f in s.get("files", [])] or [("Education_CIP_to_ONET_SOC.xlsx", s["sha256"])]
        for name, h in hashes:
            assert pins[name][0] == h
        if "db_31_0" in s["url"]:
            assert s["version"] == "31.0"
    comps = {c["component"]: c for c in prov["derived_components"]}
    assert comps["four_year_outline"]["ownership_class"] == "synthetic_generated_by_dreamco"
    assert comps["practice_tasks"]["ownership_class"] == "synthetic_generated_by_dreamco"
    # owner approval is never set by the build
    assert cand["owner_approval"] is None and cand["scorecard_score"] is None
    gate = json.loads((d / "license_gate.json").read_text())
    assert gate["sale_requirements"]["owner_approval_present"] is False
    assert gate["outcome"] != "approved_for_sale"
    assert gate["inputs"]["provenance_sha256"] == sha(d / "provenance.json")
    assert not [c["id"] for c in gate["checks"] if c["scope"] == "rights" and c["status"] == "fail"]


def test_year4_targets_are_not_manager_or_chief():
    linked = {}
    for r in csv.DictReader(open(ROOT/"data/major_to_onet.csv")):
        linked.setdefault(r["cip_code"], set()).add(r["onet_soc_code"])
    for m in json.loads((ROOT/"data/majors_selected.json").read_text()):
        ts = m["entry_targets"]
        assert 1 <= len(ts) <= 3, m["cip"]
        for t in ts:
            assert not re.search(r"Manager|Chief|Postsecondary|All Other", t["title"]), (m["cip"], t["title"])
            assert t["soc"] in linked[m["cip"]]
    for p in PLANS:
        y4 = next(l for l in p.read_text().splitlines() if l.startswith("4. Year 4"))
        assert not re.search(r"Manager|Chief", y4), (p.name, y4)


def test_practice_tasks_reference_real_tasks_of_linked_occupations():
    ts = pd.read_csv(ROOT/"raw/task_statements.csv", dtype={"O*NET-SOC Code": str})
    task_soc = dict(zip(ts["Task ID"].astype(int), ts["O*NET-SOC Code"]))
    task_text = dict(zip(ts["Task ID"].astype(int), ts["Task"]))
    linked = {}
    for r in csv.DictReader(open(ROOT/"data/major_to_onet.csv")):
        linked.setdefault(r["cip_code"], set()).add(r["onet_soc_code"])
    pt = json.loads((ROOT/"data/practice_tasks.json").read_text())["tasks"]
    per = {}
    for t in pt:
        per.setdefault(t["cip_code"], []).append(t)
        assert t["onet_task_id"] in task_soc, t["practice_id"]
        assert task_soc[t["onet_task_id"]] == t["onet_soc_code"], t["practice_id"]
        assert t["onet_soc_code"] in linked[t["cip_code"]], t["practice_id"]
        assert t["label"] == "DreamCo-original practice prompt" and t["prompt"].startswith("DreamCo-original practice prompt")
        assert len(t["rubric"]) == 3
        assert task_text[t["onet_task_id"]] not in t["prompt"]  # O*NET task text is referenced, not reproduced
    assert set(per) == set(linked)
    for cip, items in per.items():
        assert 5 <= len(items) <= 8, cip
    plans = {p.name.split("_")[0]: p.read_text() for p in PLANS}
    for t in pt:
        assert f"O*NET task {t['onet_task_id']}" in plans[t["cip_code"]]
        assert task_text[t["onet_task_id"]] not in plans[t["cip_code"]]
