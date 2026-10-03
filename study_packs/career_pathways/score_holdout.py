"""Check a filled-in blind holdout grading sheet and, once grading is declared final, score it into holdout evidence.

GRADER: you may run the default dry run to check that your sheet is complete. It prints no scores.
Do not run --finalize yourself; the builder runs it after you create GRADING_FINAL.txt.

Dry run (default): validates the sheet's completeness and format only. It does not read the key and prints no
per-item, per-major or per-asset scores.

--finalize: requires evidence/holdout_kit/GRADING_FINAL.txt containing the line
    FINAL: grader=<name>; declared_at=<ISO 8601 date-time with offset>
then reads the PRIVATE key (outside the repo), verifies its sha256 against KEY_COMMITMENT.txt and the items.json hash,
computes the scores and writes, per asset with kit items:
    data/dreamco_knowledge/evidence/holdout/<asset_id>/<YYYYMMDD>-<NN>.results.json
    data/dreamco_knowledge/evidence/holdout/<asset_id>/<YYYYMMDD>-<NN>.json   (evidence record)

Pass rule (documented in evidence/holdout_kit/README.md):
  * kit-level discrimination, required before ANY record can pass:
      - detection rate >= 0.8: a weakened item counts as detected when the grader's score on its weakened criterion is
        <= 1 and lower than the mean of its other two criteria;
      - mean gap >= 1.0 on the 0-2 scale: mean of all criterion scores on full-strength items minus mean of the
        weakened-criterion scores on weakened items.
    Giving every criterion the same score (for example all 2s) detects nothing and fails.
  * per asset: agreement >= 0.8 (fraction of the asset's criterion scores inside the key's accepted band: 1-2 for
    full-strength criteria, 0-1 for the weakened criterion) and no full-strength item judged factually incorrect.
"""
import argparse, csv, datetime, hashlib, json, os, pathlib, re

ROOT = pathlib.Path(__file__).resolve().parent
PRIVATE = pathlib.Path(os.environ.get("DREAMCO_HOLDOUT_PRIVATE_DIR", "/workspace/edu-career-pathways-private"))
DETECTION_MIN, GAP_MIN, AGREEMENT_MIN = 0.8, 1.0, 0.8
EVIDENCE_ROOT = "study_packs/career_pathways/data/dreamco_knowledge/evidence"
SPLIT = "blind_holdout_v2_rubric_discrimination"
FINAL_RX = re.compile(r"^FINAL: grader=(?P<grader>[^;]+); declared_at=(?P<at>\S+)\s*$", re.M)
METRIC = ("per-asset agreement: fraction of the asset's criterion scores inside the sealed key's accepted band (1-2 for "
          "full-strength criteria, 0-1 for the weakened criterion). passed requires kit-level discrimination (detection rate "
          f">= {DETECTION_MIN} and mean gap >= {GAP_MIN}), agreement >= {AGREEMENT_MIN}, and no full-strength item judged "
          "factually incorrect")


def sha(b):
    return hashlib.sha256(b).hexdigest()


def iso_with_offset(v):
    try:
        return datetime.datetime.fromisoformat(v).tzinfo is not None
    except ValueError:
        return False


def load_sheet(path, items):
    ids = [i["item_id"] for i in items]
    crit = {i["item_id"]: [c["criterion"] for c in i["rubric"]] for i in items}
    rows = list(csv.DictReader(open(path, newline="")))
    errs, out = [], {}
    for r in rows:
        hid = (r.get("item_id") or "").strip()
        if hid not in crit:
            errs.append(f"unknown item_id {hid!r}"); continue
        if hid in out:
            errs.append(f"{hid}: duplicate row"); continue
        for i in (1, 2, 3):
            if (r.get(f"criterion_{i}") or "").strip() != crit[hid][i - 1]:
                errs.append(f"{hid}: criterion_{i} was edited")
        scores = []
        for i in (1, 2, 3):
            v = (r.get(f"score_{i}") or "").strip()
            if v not in ("0", "1", "2"):
                errs.append(f"{hid}: score_{i} must be 0, 1 or 2")
            else:
                scores.append(int(v))
        fc = (r.get("factually_correct") or "").strip().lower()
        if fc not in ("yes", "no", "unsure"):
            errs.append(f"{hid}: factually_correct must be yes, no or unsure")
        if not (r.get("grader") or "").strip():
            errs.append(f"{hid}: grader is empty")
        if not iso_with_offset((r.get("graded_at") or "").strip()):
            errs.append(f"{hid}: graded_at must be ISO 8601 with offset, e.g. 2026-10-05T14:30:00-05:00")
        out[hid] = {"scores": scores, "factually_correct": fc, "comments": (r.get("comments") or "").strip(),
                    "grader": (r.get("grader") or "").strip(), "graded_at": (r.get("graded_at") or "").strip()}
    missing = [h for h in ids if h not in out]
    if missing:
        errs.append(f"rows missing for: {', '.join(missing)}")
    return out, errs


def discrimination(key, grades):
    weak = [(h, k) for h, k in key["items"].items() if k["candidate_type"] == "weakened"]
    full = [(h, k) for h, k in key["items"].items() if k["candidate_type"] == "full_strength"]
    detected = []
    for h, k in weak:
        s = grades[h]["scores"]; w = k["weakened_criterion"] - 1
        others = [x for i, x in enumerate(s) if i != w]
        if s[w] <= 1 and s[w] < sum(others) / 2:
            detected.append(h)
    full_mean = sum(sum(grades[h]["scores"]) for h, _ in full) / (3 * len(full))
    weak_mean = sum(grades[h]["scores"][k["weakened_criterion"] - 1] for h, k in weak) / len(weak)
    rate = len(detected) / len(weak)
    by_major = {}
    for h, k in key["items"].items():
        by_major.setdefault(k["cip"], []).append((k["candidate_type"], sum(grades[h]["scores"]), h))
    per_major = {}
    for cip, xs in by_major.items():
        f = [t for c, t, _ in xs if c == "full_strength"]; wk = [t for c, t, _ in xs if c == "weakened"]
        if f and wk:
            per_major[cip] = {"weakened_below_every_full": sum(1 for t in wk if t < min(f)), "n_weakened": len(wk), "n_full": len(f)}
    return {"n_weakened": len(weak), "n_full_strength": len(full), "detected": len(detected), "detection_rate": round(rate, 4),
            "full_strength_mean": round(full_mean, 4), "weakened_criterion_mean": round(weak_mean, 4),
            "mean_gap": round(full_mean - weak_mean, 4), "detection_min": DETECTION_MIN, "gap_min": GAP_MIN,
            "passed": rate >= DETECTION_MIN and (full_mean - weak_mean) >= GAP_MIN,
            "per_major_with_both_types": per_major}


def finalize(a, kit, items_doc, grades, sheet_bytes):
    root = pathlib.Path(a.root)
    decl_p = kit / "GRADING_FINAL.txt"
    m = FINAL_RX.search(decl_p.read_text()) if decl_p.is_file() else None
    if not m or not iso_with_offset(m["at"]):
        raise SystemExit(f"{decl_p} with 'FINAL: grader=<name>; declared_at=<ISO with offset>' is required before --finalize")
    commit = dict(l.split(": ", 1) for l in (kit / "KEY_COMMITMENT.txt").read_text().splitlines() if ": " in l)
    key_p = pathlib.Path(a.key)
    key_b = key_p.read_bytes()
    if sha(key_b) != commit["key_sha256"]:
        raise SystemExit("key does not match KEY_COMMITMENT.txt (sha256 differs); refusing to score")
    if sha((kit / "items.json").read_bytes()) != commit["items_json_sha256"]:
        raise SystemExit("items.json was changed after the kit was drawn; refusing to score")
    key = json.loads(key_b)
    by_id = {i["item_id"]: i for i in items_doc["items"]}
    if set(key["items"]) != set(by_id):
        raise SystemExit("key and items.json list different items")
    for h, k in key["items"].items():
        if sha(by_id[h]["candidate_answer"].encode()) != k["candidate_answer_sha256"]:
            raise SystemExit(f"{h}: candidate answer differs from the key")
    disc = discrimination(key, grades)
    graders = sorted({g["grader"] for g in grades.values()})
    now = datetime.datetime.now().astimezone()
    run_id = a.run_id or now.strftime("%Y%m%d") + "-01"
    if not re.fullmatch(r"\d{8}-\d{2}", run_id):
        raise SystemExit("--run-id must be YYYYMMDD-NN")
    per_asset = {}
    for h, k in key["items"].items():
        g = grades[h]
        agree = [s in band for s, band in zip(g["scores"], k["accepted_scores"])]
        per_asset.setdefault(k["asset_id"], []).append({
            "item_id": h, "candidate_type": k["candidate_type"], "weakened_criterion": k["weakened_criterion"],
            "expected_scores": k["expected_scores"], "accepted_scores": k["accepted_scores"], "human_scores": g["scores"],
            "criterion_agreement": agree, "factually_correct": g["factually_correct"], "comments": g["comments"]})
    majors = {m_["asset_id"]: m_ for m_ in json.loads((root / "data/majors_selected.json").read_text())}
    evaluator = f"edu-career-pathways score_holdout.py sha256:{sha((ROOT / 'score_holdout.py').read_bytes())}"
    written = []
    for aid, its in sorted(per_asset.items()):
        cip = majors[aid]["cip"]
        stem = next((root / "study_plans").glob(f"{cip}_*.md")).stem
        asset = json.loads((root / "study_plans" / stem / "asset.json").read_text())
        agreement = round(sum(sum(i["criterion_agreement"]) for i in its) / (3 * len(its)), 4)
        bad_full = [i["item_id"] for i in its if i["candidate_type"] == "full_strength" and i["factually_correct"] == "no"]
        passed = bool(disc["passed"] and agreement >= AGREEMENT_MIN and not bad_full)
        results = {"schema": "dreamco.edu_career_pathways.holdout_results.v2", "asset_id": aid, "run_id": run_id,
                   "kit": key["kit"], "kit_created_at": key["created_at"], "key_sha256": sha(key_b),
                   "items_json_sha256": commit["items_json_sha256"], "grading_sheet_sha256": sha(sheet_bytes),
                   "graders": graders, "declared_final": {"grader": m["grader"].strip(), "declared_at": m["at"]},
                   "asset_integrity_hash": asset["integrity_hash"], "metric": METRIC, "threshold": AGREEMENT_MIN,
                   "n_items": len(its), "score": agreement, "passed": passed, "kit_discrimination": disc,
                   "full_strength_judged_incorrect": bad_full, "items": its,
                   "limitations": ("Rubric-discrimination check by a single human grader who is also the owner (not "
                                   "independent of DreamCo). Candidate answers were written for the kit and are not learner "
                                   "responses. Few items per asset.")}
        rb = (json.dumps(results, indent=2, ensure_ascii=False) + "\n").encode()
        rec = {"evidence_id": f"holdout:{aid}:{run_id}", "capability_id": "career-pathway-study-plan",
               "source_type": "human_evaluation", "source_reference": asset["integrity_hash"],
               "retrieved_at": now.isoformat(timespec="seconds"),
               "content_version": f"{aid} plan {asset['integrity_hash']}; {key['kit']} drawn {key['created_at']}",
               "license_or_usage_basis": "DreamCo-original evaluation by the owner of DreamCo-original kit items.",
               "transformation": "original_evaluation", "evaluator_version": f"{evaluator}; human grader(s): {', '.join(graders)}",
               "integrity_hash": "sha256:" + sha(rb), "results_path": f"data/dreamco_knowledge/evidence/holdout/{aid}/{run_id}.results.json",
               "evidence_root": EVIDENCE_ROOT, "split": SPLIT, "n_items": len(its), "metric": METRIC, "score": agreement,
               "threshold": AGREEMENT_MIN, "passed": passed, "grader": ", ".join(graders)}
        out = root / "data/dreamco_knowledge/evidence/holdout" / aid
        if (out / f"{run_id}.json").exists():
            raise SystemExit(f"{out / (run_id + '.json')} exists; evidence is append-only, use a new --run-id")
        written.append((out, run_id, rb, rec))
    for out, run_id, rb, rec in written:
        out.mkdir(parents=True, exist_ok=True)
        (out / f"{run_id}.results.json").write_bytes(rb)
        (out / f"{run_id}.json").write_text(json.dumps(rec, indent=2, ensure_ascii=False) + "\n")
        print(rec["evidence_id"], f"n_items={rec['n_items']} score={rec['score']} passed={rec['passed']}")
    print("kit discrimination:", json.dumps({k: v for k, v in disc.items() if k != "per_major_with_both_types"}))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sheet", default=None, help="default: <kit-dir>/grading_sheet.csv")
    ap.add_argument("--kit-dir", default=str(ROOT / "evidence" / "holdout_kit"))
    ap.add_argument("--key", default=str(PRIVATE / "holdout_key.json"), help="private key (outside the repo)")
    ap.add_argument("--root", default=str(ROOT), help="pack root (for tests)")
    ap.add_argument("--finalize", action="store_true", help="score and write evidence (after GRADING_FINAL.txt exists)")
    ap.add_argument("--run-id", default=None)
    a = ap.parse_args()
    kit = pathlib.Path(a.kit_dir)
    sheet = pathlib.Path(a.sheet or kit / "grading_sheet.csv")
    items_doc = json.loads((kit / "items.json").read_text())
    sheet_bytes = sheet.read_bytes()
    grades, errs = load_sheet(sheet, items_doc["items"])
    if errs:
        raise SystemExit("grading sheet incomplete or invalid:\n  " + "\n  ".join(errs))
    if not a.finalize:
        print(f"Sheet format OK: all {len(grades)} rows complete. No scores were computed (dry run). "
              "When grading is final, create GRADING_FINAL.txt and ask the builder to run --finalize.")
        return
    finalize(a, kit, items_doc, grades, sheet_bytes)


if __name__ == "__main__":
    main()
