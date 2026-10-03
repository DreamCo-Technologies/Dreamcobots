"""Enumerate field paths of the pack's output files (used by tests and to maintain docs/data_dictionary.json)."""
import csv, glob, json, pathlib, re

ROOT = pathlib.Path(__file__).resolve().parents[1]
# Parents whose children are map entries keyed by data (SOC code, item id, file name, kind); shown as <key>.
MAP_PARENTS = {"knowledge_weighting.weights", "[].knowledge_weighting.weights", "counts_by_kind_and_status",
               "counts_by_kind_and_status.<key>", "baseline.files", "current.files", "items", "inputs", "items.<key>.weakening"}
FILES = {
    "data/majors_selected.json": "data/majors_selected.json",
    "data/practice_tasks.json": "data/practice_tasks.json",
    "data/major_to_onet.csv": "data/major_to_onet.csv",
    "data/coverage.csv": "data/coverage.csv",
    "study_plans/<stem>/plan.json": "study_plans/*/plan.json",
    "study_plans/<stem>/provenance.json": "study_plans/*/provenance.json",
    "study_plans/<stem>/asset.json": "study_plans/*/asset.json",
    "study_plans/<stem>/candidate.json": "study_plans/*/candidate.json",
    "study_plans/<stem>/license_gate.json": "study_plans/*/license_gate.json",
    "data/dreamco_knowledge/evidence/regression/<asset_id>/<run>.json": "data/dreamco_knowledge/evidence/regression/*/*[0-9].json",
    "data/dreamco_knowledge/evidence/regression/<asset_id>/<run>.results.json": "data/dreamco_knowledge/evidence/regression/*/*.results.json",
    "evidence/holdout_kit/items.json": "evidence/holdout_kit/items.json",
    "evidence/holdout_kit/_key.json": "evidence/holdout_kit/_key.json",
    "evidence/holdout_kit/grading_sheet.csv": "evidence/holdout_kit/grading_sheet.csv",
}


def walk(x, p, out):
    if isinstance(x, dict):
        for k, v in x.items():
            q = f"{p}.<key>" if p in MAP_PARENTS or (p.endswith("items") and re.fullmatch(r"H\d\d", k)) else (f"{p}.{k}" if p else k)
            out.add(q)
            walk(v, q, out)
    elif isinstance(x, list):
        for v in x:
            q = f"{p}[]"
            walk(v, q, out)


def paths(pattern, sample=None):
    files = sorted(glob.glob(str(ROOT / FILES[pattern])))
    if sample:
        files = files[:sample] + files[-sample:]
    out = set()
    for f in files:
        if f.endswith(".csv"):
            out |= set(next(csv.reader(open(f))))
        else:
            walk(json.load(open(f)), "", out)
    return out


if __name__ == "__main__":
    for pat in FILES:
        ps = sorted(paths(pat))
        print(f"## {pat} ({len(ps)})")
        for p in ps:
            print("  ", p)
