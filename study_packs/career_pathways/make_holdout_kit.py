"""Build the blind holdout grading kit in evidence/holdout_kit/.

GRADER: DO NOT OPEN THIS FILE. It contains the answer key (which candidate answers were weakened, and how).

12 items are drawn with a fixed seed from the 162 authored practice tasks (authored/practice_tasks_authored.json).
None of them was used to tune anything: no model or grader has seen graded answers for any authored task. Six
candidate answers are the authored reference outline as written; six are deliberately weakened copies in which the
content for one rubric criterion is removed or replaced with a vague line. Item order and the H01-H12 labels are
shuffled with the same seed. Outputs:
  evidence/holdout_kit/README.md          instructions for the grader
  evidence/holdout_kit/items.md           blind items: scenario prompt, candidate answer, rubric
  evidence/holdout_kit/items.json         the same, machine-readable (no key)
  evidence/holdout_kit/grading_sheet.csv  blank sheet: scores 0-2 per criterion, factual check, comments
  evidence/holdout_kit/_key.json          SEALED answer key and item hashes (grader must not open)
Usage: python make_holdout_kit.py   (refuses to overwrite a grading sheet that already contains scores)
"""
import csv, datetime, hashlib, json, pathlib, random

ROOT = pathlib.Path(__file__).resolve().parent
KIT = ROOT / "evidence" / "holdout_kit"
SEED = 20261002
N_ITEMS, N_WEAK = 12, 6
# practice_id -> (weakened criterion index 0-2, {outline index: replacement text or None to delete})
WEAKENING = {
    "11.0701-P6": (1, {2: "The work looks manageable in the time available."}),
    "40.0501-P4": (2, {3: "Next steps to be agreed after the tests come back.", 4: None}),
    "42.0101-P1": (2, {4: None}),
    "44.0701-P2": (1, {1: "Contact notes are added to the file when time allows."}),
    "51.2001-P2": (1, {2: None}),
    "52.0801-P6": (0, {0: "Documents: whatever the bank asks for.", 3: None}),
}


def content_hash(t):
    keep = {k: t[k] for k in ("practice_id", "onet_soc_code", "onet_task_id", "prompt", "rubric", "reference_answer_outline")}
    return hashlib.sha256(json.dumps(keep, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def main():
    sheet = KIT / "grading_sheet.csv"
    if sheet.exists():
        rows = list(csv.DictReader(open(sheet)))
        if any(r.get(f"score_{i}", "").strip() for r in rows for i in (1, 2, 3)):
            raise SystemExit("grading_sheet.csv already contains scores; refusing to overwrite")
    tasks = json.loads((ROOT / "authored/practice_tasks_authored.json").read_text())["tasks"]
    by = {t["practice_id"]: t for t in tasks}
    rng = random.Random(SEED)
    sel = sorted(rng.sample(sorted(by), N_ITEMS))
    weak = sorted(rng.sample(sel, N_WEAK))
    assert sorted(WEAKENING) == weak, "WEAKENING must cover exactly the seeded weakened items"
    order = list(sel)
    rng.shuffle(order)
    majors = {m["cip"]: m for m in json.loads((ROOT / "data/majors_selected.json").read_text())}
    items, key = [], {}
    for n, pid in enumerate(order, 1):
        t = by[pid]
        hid = f"H{n:02d}"
        outline = list(t["reference_answer_outline"])
        if pid in WEAKENING:
            crit, edits = WEAKENING[pid]
            outline = [edits[i] if i in edits else x for i, x in enumerate(outline)]
            outline = [x for x in outline if x is not None]
            expected = [2, 2, 2]; expected[crit] = 0
            accept = [[1, 2], [1, 2], [1, 2]]; accept[crit] = [0, 1]
            kind = "weakened"
        else:
            crit, expected, accept, kind = None, [2, 2, 2], [[1, 2], [1, 2], [1, 2]], "reference_outline"
        answer = "\n".join(f"- {x}" for x in outline)
        items.append({"item_id": hid, "prompt": t["prompt"], "candidate_answer": answer,
                      "rubric": [{"criterion": c["criterion"], "description": c["description"], "points": c["points"]} for c in t["rubric"]]})
        cip = pid.rsplit("-P", 1)[0]
        key[hid] = {"practice_id": pid, "asset_id": majors[cip]["asset_id"], "cip": cip, "candidate_type": kind,
                    "weakened_criterion": None if crit is None else crit + 1,
                    "weakening": None if crit is None else {str(k): v for k, v in WEAKENING[pid][1].items()},
                    "expected_scores": expected, "accepted_scores": accept,
                    "candidate_answer_sha256": hashlib.sha256(answer.encode()).hexdigest(),
                    "authored_item_sha256": content_hash(t)}
    now = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
    KIT.mkdir(parents=True, exist_ok=True)
    (KIT / "items.json").write_text(json.dumps({"kit": "edu-career-pathways blind holdout v1", "created_at": now,
                                                "n_items": len(items), "items": items}, indent=2, ensure_ascii=False) + "\n")
    md = ["# Blind holdout items (edu-career-pathways, kit v1)", "",
          "Grade each candidate answer against its own rubric. Record scores in `grading_sheet.csv`. See README.md first.", ""]
    for it in items:
        md += [f"## {it['item_id']}", "", "**Scenario prompt**", "", it["prompt"], "", "**Candidate answer (outline form)**", "",
               it["candidate_answer"], "", "**Rubric (score each criterion 0, 1 or 2)**", ""]
        md += [f"{i}. {c['criterion']}: {c['description']}" for i, c in enumerate(it["rubric"], 1)]
        md += [""]
    (KIT / "items.md").write_text("\n".join(md))
    with open(sheet, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["item_id", "criterion_1", "score_1", "criterion_2", "score_2", "criterion_3", "score_3",
                    "factually_correct", "comments", "grader", "graded_at"])
        for it in items:
            r = it["rubric"]
            w.writerow([it["item_id"], r[0]["criterion"], "", r[1]["criterion"], "", r[2]["criterion"], "", "", "", "", ""])
    (KIT / "_key.json").write_text(json.dumps({
        "WARNING": "SEALED ANSWER KEY. The grader must not open this file (or make_holdout_kit.py) before submitting grades.",
        "kit": "edu-career-pathways blind holdout v1", "created_at": now, "seed": SEED,
        "selection": f"random.Random({SEED}).sample of {N_ITEMS} of the {len(by)} authored practice_ids (sorted), then {N_WEAK} of those chosen as weakened, then order shuffled",
        "never_used_in_tuning": "No graded answers, model outputs or grader feedback existed for any authored task when this kit was drawn; these 12 items must not be edited or used to tune prompts, rubrics or outlines.",
        "scoring_rule": ("A criterion score agrees with the key when it is in accepted_scores. Reference-outline answers: expected 2, accepted 1-2. "
                         "Weakened answers: the weakened criterion expected 0, accepted 0-1; the other criteria expected 2, accepted 1-2."),
        "items": key}, indent=2, ensure_ascii=False) + "\n")
    print(f"kit written: {len(items)} items ({N_WEAK} weakened) -> {KIT}")


if __name__ == "__main__":
    main()
