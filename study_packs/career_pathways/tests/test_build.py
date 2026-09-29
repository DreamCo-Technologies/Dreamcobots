import csv, pathlib, pandas as pd
ROOT = pathlib.Path(__file__).resolve().parents[1]
import sys; sys.path.insert(0, str(ROOT)); import build

def test_links_exist_in_official_sources():
    cw = build.load_crosswalk(); pairs = set(zip(cw.cip, cw.soc))
    occ = set(pd.read_csv(ROOT/"raw/occupation_data.csv", dtype=str)["O*NET-SOC Code"])
    rows = list(csv.DictReader(open(ROOT/"data/major_to_onet.csv")))
    assert len(rows) > 0
    for r in rows:
        assert (r["cip_code"], r["onet_soc_code"]) in pairs
        assert r["onet_soc_code"] in occ

def test_every_plan_has_provenance():
    plans = list((ROOT/"study_plans").glob("*.md")); assert len(plans) >= 20
    for p in plans:
        t = p.read_text(); assert "**Provenance.**" in t and "CC BY 4.0" in t and "not O*NET data" in t
