"""Check a filled-in blind holdout grading sheet and, once grading is declared final, score it into holdout evidence.

GRADER: you may run the default dry run to check that your sheet is complete. It prints no scores. When you are done,
run --declare-final --grader "<your name>" (or write GRADING_FINAL.txt yourself, see the kit README).
Do not run --finalize yourself; the builder runs it after GRADING_FINAL.txt exists.

Dry run (default): validates the sheet's completeness and format only. It never reads the key, prints no per-item,
per-major or per-asset scores, and gives the same output and exit code for every complete, well-formed sheet.

--declare-final --grader NAME: validates the sheet, requires that every row names exactly that grader, and writes
evidence/holdout_kit/GRADING_FINAL.txt with the line
    FINAL: grader=<name>; declared_at=<ISO 8601 date-time with offset>; sheet_sha256=<sha256 of grading_sheet.csv>
It never reads the key. After that the sheet is locked: --finalize refuses a sheet whose sha256 differs.

--finalize: requires GRADING_FINAL.txt (with sheet_sha256), then decrypts the PRIVATE key in memory (outside the repo,
see holdout_crypto.py), verifies its sha256 against KEY_COMMITMENT.txt and the items.json hash, and writes, per asset
with kit items:
    data/dreamco_knowledge/evidence/holdout/<asset_id>/<YYYYMMDD>-<NN>.results.json
    data/dreamco_knowledge/evidence/holdout/<asset_id>/<YYYYMMDD>-<NN>.json   (evidence record)
plus evidence/holdout_kit/FINALIZED.txt. A key commitment is scored once: a second --finalize for the same key_sha256 is
refused, under any run id.

Pass rule (documented in evidence/holdout_kit/README.md):
  * kit-level discrimination, required before ANY record can pass:
      - detection rate >= 0.8: a weakened item counts as detected when the grader's score on its weakened criterion is
        <= 1 and lower than the mean of its other two criteria;
      - false-alarm rate <= 0.2: a full-strength item counts as flagged when its lowest criterion score is <= 1 and lower
        than the mean of its other two criteria (the same pattern as a detection);
      - mean gap >= 1.0 on the 0-2 scale: mean of all criterion scores on full-strength items minus mean of the
        weakened-criterion scores on weakened items.
    Giving every criterion the same score (for example all 2s) detects nothing and fails; marking one criterion down on
    every item raises a false alarm on every full-strength item and fails.
  * per asset: at least 4 kit items with at least one full-strength and one weakened item (an asset with fewer items
    only counts toward the kit-level check and its record cannot pass), agreement >= 0.8 (fraction of the asset's
    criterion scores inside the key's accepted band: 1-2 for full-strength criteria, 0-1 for the weakened criterion),
    and no full-strength item judged factually incorrect.
"""
import argparse, csv, datetime, hashlib, json, os, pathlib, re

import holdout_crypto

ROOT = pathlib.Path(__file__).resolve().parent
PRIVATE = pathlib.Path(os.environ.get("DREAMCO_HOLDOUT_PRIVATE_DIR", "/workspace/edu-career-pathways-private"))
DETECTION_MIN, FALSE_ALARM_MAX, GAP_MIN, AGREEMENT_MIN = 0.8, 0.2, 1.0, 0.8
MIN_ITEMS_PER_MAJOR = 4
PACK_PATH = "study_packs/career_pathways"            # pack location inside the repository
EVIDENCE_ROOT = f"{PACK_PATH}/data/dreamco_knowledge/evidence"
PATHS_RELATIVE_TO = "repository root (the directory that contains study_packs/); evidence_root and results_path share it"
SPLIT = "holdout"
OWNER_NAMES = {"irean", "irean jordan", "ireanjordan24"}
FINAL_RX = re.compile(r"^FINAL: grader=(?P<grader>[^;]+); declared_at=(?P<at>[^;\s]+); sheet_sha256=(?P<sheet>[0-9a-f]{64})\s*$",
                      re.M)
METRIC = ("per-asset agreement: fraction of the asset's criterion scores inside the sealed key's accepted band (1-2 for "
          "full-strength criteria, 0-1 for the weakened criterion). passed requires kit-level discrimination (detection rate "
          f">= {DETECTION_MIN}, false-alarm rate <= {FALSE_ALARM_MAX} and mean gap >= {GAP_MIN}), at least "
          f"{MIN_ITEMS_PER_MAJOR} kit items for the asset with at least one full-strength and one weakened item, agreement "
          f">= {AGREEMENT_MIN}, and no full-strength item judged factually incorrect")
BASELINE_DEFINITION = (
    "baseline_score is the highest expected agreement (same metric as score) that a grader who cannot tell full-strength "
    "from weakened answers would get on this asset's items, over three reference graders: (a) uniform random, each "
    "criterion scored 0, 1 or 2 with equal probability; (b) all 2s; (c) the shortcut grader, who scores one criterion 0 "
    "and the other two 2 on every item, picking the true weakened criterion on weakened items (its best case) and a "
    "uniformly random criterion on full-strength items. Computed exactly from the key's accepted bands. score above "
    "baseline_score is necessary but not sufficient; the kit-level rule is what rules these graders out.")


def sha(b):
    return hashlib.sha256(b).hexdigest()


def iso_with_offset(v):
    try:
        return datetime.datetime.fromisoformat(v).tzinfo is not None
    except ValueError:
        return False


def norm_name(v):
    return " ".join(str(v).split())


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
                    "grader": norm_name(r.get("grader") or ""), "graded_at": (r.get("graded_at") or "").strip()}
    missing = [h for h in ids if h not in out]
    if missing:
        errs.append(f"rows missing for: {', '.join(missing)}")
    return out, errs


def _marked_down(s, c):
    """The grader marked criterion c (0-based) of score vector s down: <= 1 and below the mean of the other two."""
    others = [x for i, x in enumerate(s) if i != c]
    return s[c] <= 1 and s[c] < sum(others) / 2


def discrimination(key, grades):
    weak = [(h, k) for h, k in key["items"].items() if k["candidate_type"] == "weakened"]
    full = [(h, k) for h, k in key["items"].items() if k["candidate_type"] == "full_strength"]
    detected = [h for h, k in weak if _marked_down(grades[h]["scores"], k["weakened_criterion"] - 1)]
    false_alarms = []
    for h, _ in full:
        s = grades[h]["scores"]
        if _marked_down(s, s.index(min(s))):
            false_alarms.append(h)
    if not full or not weak:
        raise SystemExit("the key must contain both full-strength and weakened items")
    full_mean = sum(sum(grades[h]["scores"]) for h, _ in full) / (3 * len(full))
    weak_mean = sum(grades[h]["scores"][k["weakened_criterion"] - 1] for h, k in weak) / len(weak)
    rate, fa_rate, gap = len(detected) / len(weak), len(false_alarms) / len(full), full_mean - weak_mean
    by_major = {}
    for h, k in key["items"].items():
        by_major.setdefault(k["cip"], []).append((k["candidate_type"], sum(grades[h]["scores"]), h))
    per_major = {}
    for cip, xs in by_major.items():
        f = [t for c, t, _ in xs if c == "full_strength"]; wk = [t for c, t, _ in xs if c == "weakened"]
        if f and wk:
            per_major[cip] = {"weakened_below_every_full": sum(1 for t in wk if t < min(f)), "n_weakened": len(wk), "n_full": len(f)}
    return {"n_weakened": len(weak), "n_full_strength": len(full), "detected": len(detected), "detection_rate": round(rate, 4),
            "false_alarms": len(false_alarms), "false_alarm_rate": round(fa_rate, 4),
            "full_strength_mean": round(full_mean, 4), "weakened_criterion_mean": round(weak_mean, 4),
            "mean_gap": round(gap, 4), "detection_min": DETECTION_MIN, "false_alarm_max": FALSE_ALARM_MAX, "gap_min": GAP_MIN,
            "passed": rate >= DETECTION_MIN and fa_rate <= FALSE_ALARM_MAX and gap >= GAP_MIN,
            "per_major_with_both_types": per_major}


def _agree(scores, bands):
    return sum(s in b for s, b in zip(scores, bands)) / 3


def baselines(key_items):
    """Exact expected agreement of the three reference graders in BASELINE_DEFINITION over these key items."""
    rnd = sum(sum(len(set(b) & {0, 1, 2}) / 3 for b in k["accepted_scores"]) / 3 for k in key_items) / len(key_items)
    all2 = sum(_agree([2, 2, 2], k["accepted_scores"]) for k in key_items) / len(key_items)
    sc = 0.0
    for k in key_items:
        if k["candidate_type"] == "weakened":
            c = k["weakened_criterion"] - 1
            sc += _agree([0 if i == c else 2 for i in range(3)], k["accepted_scores"])
        else:
            sc += sum(_agree([0 if i == c else 2 for i in range(3)], k["accepted_scores"]) for c in range(3)) / 3
    sc /= len(key_items)
    b = {"uniform_random": round(rnd, 4), "all_2s": round(all2, 4), "shortcut_one_criterion_0": round(sc, 4)}
    return round(max(b.values()), 4), b


def eligibility(its):
    n_full = sum(i["candidate_type"] == "full_strength" for i in its)
    n_weak = len(its) - n_full
    ok = len(its) >= MIN_ITEMS_PER_MAJOR and n_full >= 1 and n_weak >= 1
    reason = None if ok else (f"{len(its)} kit item(s); a per-asset record needs at least {MIN_ITEMS_PER_MAJOR} items with at "
                              "least one full-strength and one weakened item. These items count only toward the kit-level check.")
    return {"min_items": MIN_ITEMS_PER_MAJOR, "n_items": len(its), "n_full_strength": n_full, "n_weakened": n_weak,
            "eligible": ok, "reason": reason}


def limitations_text(grader, its, elig):
    owner = norm_name(grader).casefold() in OWNER_NAMES or norm_name(grader).casefold().startswith("irean")
    t = (f"One human grader, {grader}: the only grader named on the sheet and the grader declared in GRADING_FINAL.txt. "
         + ("The grader is the owner of DreamCo, so the result is not independent of DreamCo. " if owner else
            "This script does not verify the grader's independence from DreamCo. ")
         + "Candidate answers were written by the builder for the kit and are not learner responses; the result shows whether "
           "the rubrics discriminate when a human applies them, not learning outcomes. "
         + f"This asset has {len(its)} kit item(s) ({elig['n_full_strength']} full-strength, {elig['n_weakened']} weakened).")
    if not elig["eligible"]:
        t += " Too few items for a per-asset result: the record cannot pass."
    return t


def parse_final(kit):
    decl_p = kit / "GRADING_FINAL.txt"
    m = FINAL_RX.search(decl_p.read_text()) if decl_p.is_file() else None
    if not m or not iso_with_offset(m["at"]):
        raise SystemExit(f"{decl_p} with 'FINAL: grader=<name>; declared_at=<ISO with offset>; sheet_sha256=<sha256 of "
                         "grading_sheet.csv>' is required before --finalize")
    return {"grader": norm_name(m["grader"]), "declared_at": m["at"], "sheet_sha256": m["sheet"]}


def read_commitment(kit):
    return dict(l.split(": ", 1) for l in (kit / "KEY_COMMITMENT.txt").read_text().splitlines() if ": " in l)


def prior_finalizations(root, kit, key_sha):
    """Run ids already scored for this key commitment (from FINALIZED.txt and from holdout results files)."""
    runs = set()
    fp = kit / "FINALIZED.txt"
    if fp.is_file():
        d = dict(l.split(": ", 1) for l in fp.read_text().splitlines() if ": " in l)
        if d.get("key_sha256") == key_sha:
            runs.add(d.get("run_id", "?"))
    for r in (root / "data/dreamco_knowledge/evidence/holdout").glob("*/*.results.json"):
        try:
            if json.loads(r.read_text()).get("key_sha256") == key_sha:
                runs.add(r.name.split(".")[0])
        except ValueError:
            runs.add(r.name.split(".")[0])
    return sorted(runs)


def declare_final(a, kit, grades, sheet_bytes):
    p = kit / "GRADING_FINAL.txt"
    if p.exists():
        raise SystemExit(f"{p} already exists; grading was already declared final")
    name = norm_name(a.grader or "")
    names = sorted({g["grader"] for g in grades.values()})
    if not name or names != [name]:
        raise SystemExit(f"every row's grader must be exactly {name!r}; the sheet names {names}")
    at = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
    p.write_text(f"FINAL: grader={name}; declared_at={at}; sheet_sha256={sha(sheet_bytes)}\n")
    print(f"wrote {p}. The sheet is now locked: do not change grading_sheet.csv.")


def finalize(a, kit, items_doc, grades, sheet_bytes):
    root = pathlib.Path(a.root)
    decl = parse_final(kit)
    if sha(sheet_bytes) != decl["sheet_sha256"]:
        raise SystemExit("grading_sheet.csv does not match sheet_sha256 in GRADING_FINAL.txt (the sheet changed after "
                         "grading was declared final); refusing to score")
    graders = sorted({g["grader"] for g in grades.values()})
    if graders != [decl["grader"]]:
        raise SystemExit(f"the sheet must name exactly one grader, the one declared in GRADING_FINAL.txt "
                         f"({decl['grader']!r}); it names {graders}")
    grader = decl["grader"]
    commit = read_commitment(kit)
    run_id = a.run_id or datetime.datetime.now().astimezone().strftime("%Y%m%d") + "-01"
    if not re.fullmatch(r"\d{8}-\d{2}", run_id):
        raise SystemExit("--run-id must be YYYYMMDD-NN")
    prior = prior_finalizations(root, kit, commit["key_sha256"])
    if prior:
        raise SystemExit(f"this key commitment was already finalized (run {', '.join(prior)}); a kit is scored once")
    if sha((kit / "items.json").read_bytes()) != commit["items_json_sha256"]:
        raise SystemExit("items.json was changed after the kit was drawn; refusing to score")
    key_b = holdout_crypto.decrypt_bytes(pathlib.Path(a.key).read_bytes(), holdout_crypto.read_passphrase(a.passphrase_file),
                                         "holdout_key")
    if sha(key_b) != commit["key_sha256"]:
        raise SystemExit("key does not match KEY_COMMITMENT.txt (sha256 differs); refusing to score")
    key = json.loads(key_b)
    by_id = {i["item_id"]: i for i in items_doc["items"]}
    if set(key["items"]) != set(by_id):
        raise SystemExit("key and items.json list different items")
    for h, k in key["items"].items():
        if sha(by_id[h]["candidate_answer"].encode()) != k["candidate_answer_sha256"]:
            raise SystemExit(f"{h}: candidate answer differs from the key")
    disc = discrimination(key, grades)
    now = datetime.datetime.now().astimezone()
    per_asset, key_by_asset = {}, {}
    for h, k in key["items"].items():
        g = grades[h]
        agree = [s in band for s, band in zip(g["scores"], k["accepted_scores"])]
        key_by_asset.setdefault(k["asset_id"], []).append(k)
        per_asset.setdefault(k["asset_id"], []).append({
            "item_id": h, "candidate_type": k["candidate_type"], "weakened_criterion": k["weakened_criterion"],
            "expected_scores": k["expected_scores"], "accepted_scores": k["accepted_scores"], "human_scores": g["scores"],
            "criterion_agreement": agree, "factually_correct": g["factually_correct"], "comments": g["comments"]})
    majors = {m_["asset_id"]: m_ for m_ in json.loads((root / "data/majors_selected.json").read_text())}
    evaluator = (f"edu-career-pathways score_holdout.py sha256:{sha((ROOT / 'score_holdout.py').read_bytes())}; "
                 f"holdout_crypto.py sha256:{sha((ROOT / 'holdout_crypto.py').read_bytes())}")
    written = []
    for aid, its in sorted(per_asset.items()):
        cip = majors[aid]["cip"]
        stem = next((root / "study_plans").glob(f"{cip}_*.md")).stem
        asset = json.loads((root / "study_plans" / stem / "asset.json").read_text())
        agreement = round(sum(sum(i["criterion_agreement"]) for i in its) / (3 * len(its)), 4)
        bad_full = [i["item_id"] for i in its if i["candidate_type"] == "full_strength" and i["factually_correct"] == "no"]
        elig = eligibility(its)
        base, base_all = baselines(key_by_asset[aid])
        passed = bool(disc["passed"] and elig["eligible"] and agreement >= AGREEMENT_MIN and not bad_full)
        lim = limitations_text(grader, its, elig)
        results_path = f"{EVIDENCE_ROOT}/holdout/{aid}/{run_id}.results.json"
        results = {"schema": "dreamco.edu_career_pathways.holdout_results.v3", "asset_id": aid, "run_id": run_id,
                   "kit": key["kit"], "kit_created_at": key["created_at"], "key_sha256": sha(key_b),
                   "items_json_sha256": commit["items_json_sha256"], "grading_sheet_sha256": sha(sheet_bytes),
                   "graders": [grader], "declared_final": decl, "asset_integrity_hash": asset["integrity_hash"],
                   "split": SPLIT, "metric": METRIC, "threshold": AGREEMENT_MIN, "n_items": len(its), "score": agreement,
                   "baseline_score": base, "baselines": base_all, "baseline_definition": BASELINE_DEFINITION,
                   "per_asset_eligibility": elig, "passed": passed, "kit_discrimination": disc,
                   "full_strength_judged_incorrect": bad_full, "items": its, "limitations": lim}
        rb = (json.dumps(results, indent=2, ensure_ascii=False) + "\n").encode()
        rec = {"evidence_id": f"holdout:{aid}:{run_id}", "capability_id": "career-pathway-study-plan",
               "source_type": "human_evaluation", "source_reference": asset["integrity_hash"],
               "retrieved_at": now.isoformat(timespec="seconds"),
               "content_version": f"{aid} plan {asset['integrity_hash']}; {key['kit']} drawn {key['created_at']}",
               "license_or_usage_basis": f"DreamCo-original evaluation by human grader {grader} of DreamCo-original kit items.",
               "transformation": "original_evaluation", "evaluator_version": f"{evaluator}; human grader: {grader}",
               "integrity_hash": "sha256:" + sha(rb), "results_path": results_path, "evidence_root": EVIDENCE_ROOT,
               "paths_relative_to": PATHS_RELATIVE_TO, "split": SPLIT, "n_items": len(its), "metric": METRIC,
               "score": agreement, "baseline_score": base, "baseline_definition": BASELINE_DEFINITION,
               "threshold": AGREEMENT_MIN, "passed": passed, "grader": grader, "limitations": lim}
        out = root / "data/dreamco_knowledge/evidence/holdout" / aid
        if (out / f"{run_id}.json").exists():
            raise SystemExit(f"{out / (run_id + '.json')} exists; evidence is append-only, use a new --run-id")
        written.append((out, run_id, rb, rec))
    for out, run_id, rb, rec in written:
        out.mkdir(parents=True, exist_ok=True)
        (out / f"{run_id}.results.json").write_bytes(rb)
        (out / f"{run_id}.json").write_text(json.dumps(rec, indent=2, ensure_ascii=False) + "\n")
        print(rec["evidence_id"], f"n_items={rec['n_items']} score={rec['score']} baseline={rec['baseline_score']} passed={rec['passed']}")
    (kit / "FINALIZED.txt").write_text(f"key_sha256: {commit['key_sha256']}\nrun_id: {run_id}\n"
                                       f"grading_sheet_sha256: {sha(sheet_bytes)}\nfinalized_at: {now.isoformat(timespec='seconds')}\n"
                                       "note: this key commitment has been scored; score_holdout.py refuses to finalize it again.\n")
    print("kit discrimination:", json.dumps({k: v for k, v in disc.items() if k != "per_major_with_both_types"}))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sheet", default=None, help="default: <kit-dir>/grading_sheet.csv")
    ap.add_argument("--kit-dir", default=str(ROOT / "evidence" / "holdout_kit"))
    ap.add_argument("--key", default=str(PRIVATE / "holdout_key.json.enc"), help="encrypted private key (outside the repo)")
    ap.add_argument("--passphrase-file", default=None, help="default: $DREAMCO_HOLDOUT_PASSPHRASE_FILE or "
                    + holdout_crypto.DEFAULT_PASSPHRASE_FILE)
    ap.add_argument("--root", default=str(ROOT), help="pack root (for tests)")
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--finalize", action="store_true", help="score and write evidence (after GRADING_FINAL.txt exists)")
    g.add_argument("--declare-final", action="store_true", help="grader: lock the sheet by writing GRADING_FINAL.txt")
    ap.add_argument("--grader", default=None, help="with --declare-final: your name, as written on every sheet row")
    ap.add_argument("--run-id", default=None)
    a = ap.parse_args()
    kit = pathlib.Path(a.kit_dir)
    sheet = pathlib.Path(a.sheet or kit / "grading_sheet.csv")
    items_doc = json.loads((kit / "items.json").read_text())
    sheet_bytes = sheet.read_bytes()
    grades, errs = load_sheet(sheet, items_doc["items"])
    if errs:
        raise SystemExit("grading sheet incomplete or invalid:\n  " + "\n  ".join(errs))
    if a.declare_final:
        return declare_final(a, kit, grades, sheet_bytes)
    if not a.finalize:
        print(f"Sheet format OK: all {len(grades)} rows complete. No scores were computed (dry run). "
              "When grading is final, run --declare-final --grader \"<your name>\" and ask the builder to run --finalize.")
        return
    finalize(a, kit, items_doc, grades, sheet_bytes)


if __name__ == "__main__":
    main()
