"""Turn a filled-in blind holdout grading sheet into holdout evidence records.

Reads evidence/holdout_kit/grading_sheet.csv (filled in by the human grader) and the sealed key
evidence/holdout_kit/_key.json, checks that every kit item is unchanged since the kit was drawn, and computes:
  * per criterion: whether the human score is in the key's accepted band
  * per item: discrimination for weakened answers (weakened criterion scored below the other two)
For each study plan (asset) with items in the kit it writes, with --write:
  data/dreamco_knowledge/evidence/holdout/<asset_id>/<YYYYMMDD>-<NN>.results.json
  data/dreamco_knowledge/evidence/holdout/<asset_id>/<YYYYMMDD>-<NN>.json   (evidence record)
The record has the config/evidence_provenance_schema.json fields plus split/n_items/metric/score/threshold/passed.
Without --write it only prints. It never invents or fills in grades.

Usage: python score_holdout.py --sheet evidence/holdout_kit/grading_sheet.csv [--write] [--run-id YYYYMMDD-NN]
"""
import argparse, csv, datetime, hashlib, json, pathlib, re

ROOT = pathlib.Path(__file__).resolve().parent
KIT = ROOT / "evidence" / "holdout_kit"
THRESHOLD = 0.8
METRIC = ("fraction of the asset's graded rubric criteria whose blind human score falls in the sealed key's accepted band "
          "(reference-outline answers: 1-2; deliberately weakened criterion: 0-1; other criteria of weakened answers: 1-2); "
          "passed also requires no reference-outline answer judged factually incorrect")


def sha(b):
    return hashlib.sha256(b).hexdigest()


def content_hash(t):
    keep = {k: t[k] for k in ("practice_id", "onet_soc_code", "onet_task_id", "prompt", "rubric", "reference_answer_outline")}
    return sha(json.dumps(keep, sort_keys=True, ensure_ascii=False).encode())


def load_sheet(path, key):
    rows = list(csv.DictReader(open(path, newline="")))
    errs, out = [], {}
    for r in rows:
        hid = (r.get("item_id") or "").strip()
        if hid not in key["items"]:
            errs.append(f"unknown item_id {hid!r}"); continue
        scores = []
        for i in (1, 2, 3):
            v = (r.get(f"score_{i}") or "").strip()
            if v not in ("0", "1", "2"):
                errs.append(f"{hid}: score_{i} must be 0, 1 or 2 (got {v!r})")
            else:
                scores.append(int(v))
        fc = (r.get("factually_correct") or "").strip().lower()
        if fc not in ("yes", "no", "unsure"):
            errs.append(f"{hid}: factually_correct must be yes, no or unsure")
        if not (r.get("grader") or "").strip():
            errs.append(f"{hid}: grader is empty")
        ga = (r.get("graded_at") or "").strip()
        try:
            if datetime.datetime.fromisoformat(ga).tzinfo is None:
                raise ValueError
        except ValueError:
            errs.append(f"{hid}: graded_at must be ISO 8601 with offset (got {ga!r})")
        out[hid] = {"scores": scores, "factually_correct": fc, "comments": (r.get("comments") or "").strip(),
                    "grader": (r.get("grader") or "").strip(), "graded_at": ga}
    missing = sorted(set(key["items"]) - set(out))
    if missing:
        errs.append(f"items missing from sheet: {missing}")
    if errs:
        raise SystemExit("grading sheet incomplete or invalid:\n  " + "\n  ".join(errs))
    return out


def evaluate(key, grades):
    per = {}
    for hid, k in key["items"].items():
        g = grades[hid]
        agree = [s in band for s, band in zip(g["scores"], k["accepted_scores"])]
        item = {"item_id": hid, "practice_id": k["practice_id"], "candidate_type": k["candidate_type"],
                "weakened_criterion": k["weakened_criterion"], "expected_scores": k["expected_scores"],
                "accepted_scores": k["accepted_scores"], "human_scores": g["scores"], "criterion_agreement": agree,
                "factually_correct": g["factually_correct"], "comments": g["comments"]}
        if k["weakened_criterion"]:
            w = k["weakened_criterion"] - 1
            others = [s for i, s in enumerate(g["scores"]) if i != w]
            item["weakness_detected"] = g["scores"][w] < sum(others) / len(others)
        per.setdefault(k["asset_id"], []).append(item)
    return per


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sheet", required=True)
    ap.add_argument("--key", default=str(KIT / "_key.json"))
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--run-id", default=None)
    ap.add_argument("--root", default=str(ROOT), help="pack root (for tests)")
    a = ap.parse_args()
    root = pathlib.Path(a.root)
    key = json.loads(pathlib.Path(a.key).read_text())
    authored = {t["practice_id"]: t for t in json.loads((root / "authored/practice_tasks_authored.json").read_text())["tasks"]}
    changed = [hid for hid, k in key["items"].items() if content_hash(authored[k["practice_id"]]) != k["authored_item_sha256"]]
    if changed:
        raise SystemExit(f"kit items changed since the kit was drawn (re-draw the kit instead): {changed}")
    sheet_bytes = pathlib.Path(a.sheet).read_bytes()
    grades = load_sheet(a.sheet, key)
    graders = sorted({g["grader"] for g in grades.values()})
    per = evaluate(key, grades)
    now = datetime.datetime.now().astimezone()
    run_id = a.run_id or now.strftime("%Y%m%d") + "-01"
    assert re.fullmatch(r"\d{8}-\d{2}", run_id), run_id
    all_items = [i for v in per.values() for i in v]
    kit_summary = {"n_items": len(all_items),
                   "criterion_agreement": round(sum(sum(i["criterion_agreement"]) for i in all_items) / (3 * len(all_items)), 4),
                   "weakened_detected": sum(1 for i in all_items if i.get("weakness_detected")),
                   "weakened_total": sum(1 for i in all_items if i["weakened_criterion"]),
                   "reference_judged_incorrect": sum(1 for i in all_items if i["candidate_type"] == "reference_outline" and i["factually_correct"] == "no")}
    evaluator = f"edu-career-pathways score_holdout.py sha256:{sha((ROOT / 'score_holdout.py').read_bytes())}"
    majors = {m["asset_id"]: m for m in json.loads((root / "data/majors_selected.json").read_text())}
    for aid, items in sorted(per.items()):
        cip = majors[aid]["cip"]
        stem = next((root / "study_plans").glob(f"{cip}_*.md")).stem
        asset = json.loads((root / "study_plans" / stem / "asset.json").read_text())
        n_ok = sum(sum(i["criterion_agreement"]) for i in items)
        score = round(n_ok / (3 * len(items)), 4)
        bad_ref = [i["item_id"] for i in items if i["candidate_type"] == "reference_outline" and i["factually_correct"] == "no"]
        passed = score >= THRESHOLD and not bad_ref
        results = {"schema": "dreamco.edu_career_pathways.holdout_results.v1", "asset_id": aid, "run_id": run_id,
                   "kit": key["kit"], "kit_created_at": key["created_at"], "key_sha256": sha(pathlib.Path(a.key).read_bytes()),
                   "grading_sheet_sha256": sha(sheet_bytes), "graders": graders, "asset_integrity_hash": asset["integrity_hash"],
                   "metric": METRIC, "threshold": THRESHOLD, "n_items": len(items), "score": score, "passed": passed,
                   "reference_judged_incorrect": bad_ref, "items": items, "kit_summary": kit_summary,
                   "limitations": ("Single human grader who is also the owner (not independent of DreamCo); few items per asset; "
                                   "answers are outline-form reference or weakened outlines, not learner responses.")}
        rb = (json.dumps(results, indent=2, ensure_ascii=False) + "\n").encode()
        record = {"evidence_id": f"holdout:{aid}:{run_id}", "capability_id": "career-pathway-study-plan",
                  "source_type": "human_evaluation", "source_reference": asset["integrity_hash"],
                  "retrieved_at": now.isoformat(timespec="seconds"),
                  "content_version": f"{aid} plan {asset['integrity_hash']}; holdout kit {key['kit']} drawn {key['created_at']}",
                  "license_or_usage_basis": "DreamCo-original evaluation by the owner of DreamCo-original practice items.",
                  "transformation": "original_evaluation", "evaluator_version": evaluator + f"; human grader(s): {', '.join(graders)}",
                  "integrity_hash": "sha256:" + sha(rb), "results_path": f"data/dreamco_knowledge/evidence/holdout/{aid}/{run_id}.results.json",
                  "evidence_root": "study_packs/career_pathways/data/dreamco_knowledge/evidence",
                  "split": "blind_holdout_v1", "n_items": len(items), "metric": METRIC, "score": score,
                  "threshold": THRESHOLD, "passed": passed, "grader": ", ".join(graders)}
        print(aid, f"n_items={len(items)} score={score} passed={passed}")
        if a.write:
            out = root / "data/dreamco_knowledge/evidence/holdout" / aid
            out.mkdir(parents=True, exist_ok=True)
            if (out / f"{run_id}.json").exists():
                raise SystemExit(f"{out / (run_id + '.json')} exists; use a new --run-id")
            (out / f"{run_id}.results.json").write_bytes(rb)
            (out / f"{run_id}.json").write_text(json.dumps(record, indent=2, ensure_ascii=False) + "\n")
    print("kit summary:", json.dumps(kit_summary))
    if not a.write:
        print("dry run: nothing written (use --write)")


if __name__ == "__main__":
    main()
