"""Build the blind holdout grading kit (v3) in evidence/holdout_kit/.

The kit is a rubric-discrimination check: can the grader tell full-strength candidate answers from subtly weakened
ones using the rubric? The items are NEW scenario prompts written for the kit only; they appear nowhere in the
published plans, data/practice_tasks.json, authored/, the READMEs, O*NET text or the earlier v1/v2 kits (a test checks
for shared 5-word runs). Items of a kit that was ever committed are not reused: a new draw of the same items could
expose both answer versions of an item through the git diff. Candidate answers are written for the kit; they are not
learner responses.

Inputs (PRIVATE, outside the repo; never committed or synced; encrypted at rest, see holdout_crypto.py):
  $DREAMCO_HOLDOUT_PRIVATE_DIR (default /workspace/edu-career-pathways-private)/holdout_source.json.enc
      both a full-strength and a weakened version of every candidate answer, with identical structure
  $DREAMCO_HOLDOUT_PASSPHRASE_FILE (default /home/box/.ecp-holdout/passphrase): decryption passphrase, outside
      /workspace and outside the repo
Outputs:
  PRIVATE  holdout_key.json.enc        encrypted key: which version each item shows, expected score bands, a 256-bit
                                       random nonce and the secret seed. The plaintext key is never written to disk.
  KIT      items.json, items.md        blind items: prompt, candidate answer, rubric (no key information)
  KIT      grading_sheet.csv           blank sheet
  KIT      KEY_COMMITMENT.txt          sha256 of the plaintext key bytes (which contain the nonce), so the key cannot be
                                       brute-forced from the items and cannot be changed after grading

How many answers are weakened is itself secret. It is drawn from the private seed for every kit (draw_weak below): the
total is uniform in N_WEAK_TOTAL and the Computer Science share is uniform in N_WEAK_CS, so CS (the only major with
enough items for a per-major record) always has at least one full-strength and one weakened item. The drawn count is
stored only in the encrypted key and is never printed or published.

The seed comes from secrets.randbits(128) at draw time and is stored only in the encrypted key, so this script cannot
regenerate the key from committed inputs. Running it again draws a NEW kit; it refuses if the kit has a grading sheet
with scores, a GRADING_FINAL.txt or a FINALIZED.txt, and refuses to replace an existing kit unless --redraw is given.
Usage: python make_holdout_kit.py [--redraw]
"""
import argparse, csv, datetime, hashlib, json, os, pathlib, random, secrets

import holdout_crypto

ROOT = pathlib.Path(__file__).resolve().parent
KIT = ROOT / "evidence" / "holdout_kit"
PRIVATE = pathlib.Path(os.environ.get("DREAMCO_HOLDOUT_PRIVATE_DIR", "/workspace/edu-career-pathways-private"))
KIT_NAME = "edu-career-pathways blind holdout v3 (rubric discrimination)"
SHEET_COLUMNS = ["item_id", "major", "criterion_1", "score_1", "criterion_2", "score_2", "criterion_3", "score_3",
                 "factually_correct", "comments", "grader", "graded_at"]
# Score bands used for agreement (the pass rule itself is in score_holdout.py).
FULL_BAND, WEAK_BAND = [1, 2], [0, 1]
CS_CIP = "11.0701"
N_WEAK_TOTAL = (6, 10)   # inclusive range of the secret total number of weakened items
N_WEAK_CS = (1, 3)       # inclusive range of the secret number of weakened CS items
MIN_CS_ITEMS = 4         # = score_holdout.MIN_ITEMS_PER_MAJOR; CS must be able to produce a per-major record


def sha(b):
    return hashlib.sha256(b).hexdigest()


def answer_text(bullets):
    return "\n".join(f"- {b}" for b in bullets)


def draw_weak(rng, items):
    """Secret draw of the weakened source ids: total in N_WEAK_TOTAL, of which N_WEAK_CS are CS items. Every major with
    at least MIN_CS_ITEMS items ends up with at least one item of each type."""
    cs = sorted(i["source_id"] for i in items if i["cip"] == CS_CIP)
    other = sorted(i["source_id"] for i in items if i["cip"] != CS_CIP)
    if len(cs) < MIN_CS_ITEMS or len(cs) <= N_WEAK_CS[1]:
        raise SystemExit(f"the source needs at least {max(MIN_CS_ITEMS, N_WEAK_CS[1] + 1)} CS items")
    n_cs = rng.randint(*N_WEAK_CS)
    n_total = rng.randint(*N_WEAK_TOTAL)
    if n_total - n_cs > len(other):
        raise SystemExit("not enough non-CS items for the weakened draw")
    weak = set(rng.sample(cs, n_cs)) | set(rng.sample(other, n_total - n_cs))
    by_major = {}
    for i in items:
        by_major.setdefault(i["cip"], []).append(i["source_id"] in weak)
    for cip, flags in by_major.items():
        if len(flags) >= MIN_CS_ITEMS and (all(flags) or not any(flags)):
            raise SystemExit(f"{cip}: a major with {len(flags)} items must have both item types")
    return weak


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--redraw", action="store_true", help="replace an existing (ungraded) kit with a new draw")
    a = ap.parse_args()
    src_p = PRIVATE / "holdout_source.json.enc"
    if (PRIVATE / "holdout_source.json").is_file():
        raise SystemExit(f"{PRIVATE / 'holdout_source.json'} is plaintext; encrypt it first: "
                         "python holdout_crypto.py encrypt <path> holdout_source")
    if not src_p.is_file():
        raise SystemExit(f"private kit source not found: {src_p} (it is never committed)")
    for d in (PRIVATE.resolve(), holdout_crypto.passphrase_path().resolve()):
        if d == ROOT.resolve() or ROOT.resolve() in d.parents:
            raise SystemExit(f"{d} must be outside the pack")
    if PRIVATE.resolve() in holdout_crypto.passphrase_path().resolve().parents:
        raise SystemExit("the passphrase must not be stored in the private directory next to the encrypted files")
    sheet = KIT / "grading_sheet.csv"
    if sheet.is_file():
        for r in csv.DictReader(open(sheet, newline="")):
            if any((r.get(f"score_{i}") or "").strip() for i in (1, 2, 3)):
                raise SystemExit("grading_sheet.csv already contains scores; refusing to redraw the kit")
    for f in ("GRADING_FINAL.txt", "FINALIZED.txt"):
        if (KIT / f).exists():
            raise SystemExit(f"{f} exists; this kit has been graded and cannot be redrawn")
    if (KIT / "KEY_COMMITMENT.txt").is_file() and not a.redraw:
        raise SystemExit("a kit already exists; use --redraw to replace it with a new draw (the old key becomes useless)")
    passphrase = holdout_crypto.read_passphrase()
    src_b = holdout_crypto.decrypt_bytes(src_p.read_bytes(), passphrase, "holdout_source")
    src = json.loads(src_b)
    majors = {m["cip"]: m for m in json.loads((ROOT / "data/majors_selected.json").read_text())}
    seed = secrets.randbits(128)
    rng = random.Random(seed)
    items = sorted(src["items"], key=lambda i: i["source_id"])
    weak_ids = draw_weak(rng, items)
    rng.shuffle(items)
    now = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
    pub, key_items = [], {}
    for k, it in enumerate(items, 1):
        qid = f"Q{k:02d}"
        weak = it["source_id"] in weak_ids
        ans = answer_text(it["weakened"] if weak else it["full"])
        m = majors[it["cip"]]
        if m["tier"] != "authored":
            raise SystemExit(f"{it['cip']} is not an authored major")
        pub.append({"item_id": qid, "major": f"{m['title']} (CIP {it['cip']})", "prompt": it["prompt"],
                    "candidate_answer": ans, "rubric": it["rubric"]})
        wc = it["weakened_criterion"] if weak else None
        exp = [2, 2, 2] if not weak else [0 if c == wc else 2 for c in (1, 2, 3)]
        acc = [FULL_BAND] * 3 if not weak else [WEAK_BAND if c == wc else FULL_BAND for c in (1, 2, 3)]
        key_items[qid] = {"source_id": it["source_id"], "cip": it["cip"], "asset_id": m["asset_id"],
                          "candidate_type": "weakened" if weak else "full_strength", "weakened_criterion": wc,
                          "expected_scores": exp, "accepted_scores": acc, "candidate_answer_sha256": sha(ans.encode()),
                          "prompt_sha256": sha(it["prompt"].encode())}
    KIT.mkdir(parents=True, exist_ok=True)
    for old in ("_key.json", "items.json", "items.md", "grading_sheet.csv"):
        (KIT / old).unlink(missing_ok=True)
    items_doc = {"kit": KIT_NAME, "created_at": now, "n_items": len(pub), "items": pub}
    items_b = (json.dumps(items_doc, indent=2, ensure_ascii=False) + "\n").encode()
    (KIT / "items.json").write_bytes(items_b)
    L = [f"# Blind holdout items ({KIT_NAME})", "", f"Drawn {now}. {len(pub)} items. Read `README.md` first. "
         "Score each candidate answer against its own rubric, 0 to 2 per criterion, in `grading_sheet.csv`.", ""]
    for p in pub:
        L += [f"## {p['item_id']}. {p['major']}", "", "**Scenario prompt.** " + p["prompt"], "", "**Candidate answer.**", "",
              p["candidate_answer"], "", "**Rubric (0 to 2 points each).**", ""]
        L += [f"{i}. {c['criterion']}: {c['description']}" for i, c in enumerate(p["rubric"], 1)] + [""]
    (KIT / "items.md").write_text("\n".join(L))
    with open(KIT / "grading_sheet.csv", "w", newline="") as fh:
        w = csv.writer(fh); w.writerow(SHEET_COLUMNS)
        for p in pub:
            c = [x["criterion"] for x in p["rubric"]]
            w.writerow([p["item_id"], p["major"], c[0], "", c[1], "", c[2], "", "", "", "", ""])
    key = {"WARNING": "PRIVATE ANSWER KEY. Not committed, not synced, not for the grader.",
           "kit": KIT_NAME, "created_at": now, "nonce": secrets.token_hex(32), "seed": f"{seed:032x}",
           "items_json_sha256": sha(items_b), "source_sha256": sha(src_b),
           "n_items": len(pub), "n_weakened": len(weak_ids), "items": key_items}
    key_b = (json.dumps(key, indent=2) + "\n").encode()
    holdout_crypto.write_encrypted(PRIVATE / "holdout_key.json.enc", key_b, passphrase, "holdout_key")
    (PRIVATE / "holdout_key.json").unlink(missing_ok=True)  # never keep a plaintext key (old draws included)
    (KIT / "KEY_COMMITMENT.txt").write_text(
        f"kit: {KIT_NAME}\ncreated_at: {now}\nkey_sha256: {sha(key_b)}\nitems_json_sha256: {sha(items_b)}\n"
        "algorithm: sha256 over the exact plaintext bytes of the private answer key (JSON)\n"
        "key_storage: holdout_key.json.enc outside the repository, AES-256-GCM with a scrypt-derived key; the passphrase "
        "is stored outside /workspace and outside the repository. score_holdout.py --finalize decrypts it in memory.\n"
        "note: the key is kept by the builder and is not available to the grader. It contains a 256-bit random nonce, so "
        "this hash cannot be matched by guessing which answers are weakened. score_holdout.py --finalize refuses a key "
        "whose sha256 differs from key_sha256, or items.json whose sha256 differs from items_json_sha256, and scores a "
        "given key_sha256 only once.\n")
    print(f"kit drawn: {len(pub)} items; key encrypted outside the repo; commitment {sha(key_b)[:12]}...")


if __name__ == "__main__":
    main()
