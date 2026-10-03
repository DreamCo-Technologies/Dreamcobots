"""Check a filled-in blind holdout grading sheet and, once grading is declared final, score it into holdout evidence.

GRADER: you may run the default dry run to check that your sheet is complete. It prints no scores. When you are done,
run --declare-final --grader "<your name>" (or write GRADING_FINAL.txt yourself, see the kit README), then commit and
push grading_sheet.csv and GRADING_FINAL.txt. Do not run --finalize yourself; the builder runs it after that.

Dry run (default): validates the sheet's completeness and format only. It never reads the key, prints no per-item,
per-major or per-asset scores, and gives the same output and exit code for every complete, well-formed sheet.

--declare-final --grader NAME: validates the sheet, requires that every row names exactly that grader, and writes
evidence/holdout_kit/GRADING_FINAL.txt with the line
    FINAL: grader=<name>; declared_at=<ISO 8601 date-time with offset>; sheet_sha256=<sha256 of grading_sheet.csv>
It never reads the key. After that the sheet is locked: --finalize refuses a sheet whose sha256 differs.

--finalize: all git work uses /usr/bin/git (never PATH) with a minimal sanitized environment (see
verify_holdout.GitSession). It requires, in a clone of github.com/DreamCo-Technologies/Dreamcobots (strict URL check) on
an allowed branch (edu-career-pathways/majors-onet-study-plans or main), with the kit at
<repo root>/study_packs/career_pathways/evidence/holdout_kit and the output in that pack: grading_sheet.csv and
GRADING_FINAL.txt tracked and clean; their last commit (grading_commit) contained in the real remote branch tip from
`git ls-remote`, checked in a fresh fetch of the remote (local refs are never used; an unreachable remote is a refusal);
and no commit reachable from the remote tips that already holds FINALIZED.txt, REVEALED_KEY.json or a results file for
this key commitment. The sheet, GRADING_FINAL.txt, items.json and KEY_COMMITMENT.txt are then read exactly once, with
`git show <grading_commit>:<path>`, and those exact bytes are hashed and graded; the working-tree files are never used
for scoring. Only then does it decrypt the PRIVATE key in memory (outside the repo, see holdout_crypto.py), verify its
sha256 against KEY_COMMITMENT.txt and the items.json hash, and write, per asset with kit items:
    data/dreamco_knowledge/evidence/holdout/<asset_id>/<YYYYMMDD>-<NN>.results.json
    data/dreamco_knowledge/evidence/holdout/<asset_id>/<YYYYMMDD>-<NN>.json   (evidence record)
plus evidence/holdout_kit/REVEALED_KEY.json (the exact plaintext key, nonce and seed included, so anyone can recompute
the commitment and every score) and evidence/holdout_kit/FINALIZED.txt. Commit and push those, then have someone other
than the scorer run verify_holdout.py on each record: the scorer cannot prove its own push on a shared box.

TEST ONLY: DREAMCO_HOLDOUT_TEST_ONLY_SKIP_GIT=1 (skips the git checks and reads the working tree once) or any change to
REMOTE_FETCH_URL marks every record test_only, names the URL actually used, and forces passed=false.

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
  * per asset, on that asset's own items: at least 4 kit items with at least one full-strength and one weakened item
    (an asset with fewer items only counts toward the kit-level check and its record cannot pass); detection rate >= 0.8
    and false-alarm rate <= 0.2 on its own items; agreement >= 0.8 (fraction of the asset's criterion scores inside the
    key's accepted band: 1-2 for full-strength criteria, 0-1 for the weakened criterion) AND strictly above the asset's
    own baseline_score; and no full-strength item judged factually incorrect.
"""
import argparse, csv, datetime, hashlib, io, json, os, pathlib, re

import holdout_crypto
import verify_holdout as vh   # stdlib-only: hardened git session, strict URL parsing, remote checks (and the verifier)

ROOT = pathlib.Path(__file__).resolve().parent
PRIVATE = pathlib.Path(os.environ.get("DREAMCO_HOLDOUT_PRIVATE_DIR", "/workspace/edu-career-pathways-private"))
DETECTION_MIN, FALSE_ALARM_MAX, GAP_MIN, AGREEMENT_MIN = 0.8, 0.2, 1.0, 0.8
MIN_ITEMS_PER_MAJOR = 4
PACK_PATH = vh.PACK_PATH                              # pack location inside the repository
EVIDENCE_ROOT = f"{PACK_PATH}/data/dreamco_knowledge/evidence"
PATHS_RELATIVE_TO = "repository root (the directory that contains study_packs/); evidence_root and results_path share it"
SPLIT = "holdout"
OWNER_NAMES = {"irean", "irean jordan", "ireanjordan24"}
TEST_ONLY_SKIP_GIT_ENV = "DREAMCO_HOLDOUT_TEST_ONLY_SKIP_GIT"
CANONICAL_REPO = vh.CANONICAL_REPO
CANONICAL_REMOTE_URL = vh.CANONICAL_REMOTE_URL
ALLOWED_BRANCHES = vh.ALLOWED_BRANCHES
# What `git ls-remote` and `git fetch` contact. Changing it (in code or by monkeypatching) is TEST ONLY: finalize then
# labels every record test_only, names the URL actually used, and forces passed=false.
REMOTE_FETCH_URL = vh.CANONICAL_FETCH_URL
KIT_REL = vh.KIT_REL
OUT_REL = vh.OUT_REL
normalize_remote = vh.normalize_remote
FINAL_RX = re.compile(r"^FINAL: grader=(?P<grader>[^;]+); declared_at=(?P<at>[^;\s]+); sheet_sha256=(?P<sheet>[0-9a-f]{64})\s*$",
                      re.M)
METRIC = ("per-asset agreement: fraction of the asset's criterion scores inside the sealed key's accepted band (1-2 for "
          "full-strength criteria, 0-1 for the weakened criterion). passed requires kit-level discrimination (detection rate "
          f">= {DETECTION_MIN}, false-alarm rate <= {FALSE_ALARM_MAX} and mean gap >= {GAP_MIN}); at least "
          f"{MIN_ITEMS_PER_MAJOR} kit items for the asset with at least one full-strength and one weakened item; on the "
          f"asset's own items detection rate >= {DETECTION_MIN} and false-alarm rate <= {FALSE_ALARM_MAX}; agreement >= "
          f"{AGREEMENT_MIN} and strictly above the asset's baseline_score; no full-strength item judged factually incorrect; "
          "and a sheet and GRADING_FINAL.txt committed in the canonical repository and contained in the real remote branch "
          "tip (grading_commit, remote_tip_sha)")
BASELINE_DEFINITION = (
    "baseline_score is the highest expected agreement (same metric as score) that a grader who cannot tell full-strength "
    "from weakened answers would get on this asset's items, over three reference graders: (a) uniform random, each "
    "criterion scored 0, 1 or 2 with equal probability; (b) all 2s; (c) the shortcut grader, who scores one criterion 0 "
    "and the other two 2 on every item, picking the true weakened criterion on weakened items (its best case) and a "
    "uniformly random criterion on full-strength items. Computed exactly from the key's accepted bands. A record can pass "
    "only if score is strictly above baseline_score, in addition to the kit-level and per-asset detection and false-alarm "
    "rules.")


def sha(b):
    return vh.sha(b)


def iso_with_offset(v):
    try:
        return datetime.datetime.fromisoformat(v).tzinfo is not None
    except ValueError:
        return False


def norm_name(v):
    return " ".join(str(v).split())


def load_sheet(sheet_bytes, items):
    """Grades parsed from the exact bytes of the sheet (read once by the caller)."""
    ids = [i["item_id"] for i in items]
    crit = {i["item_id"]: [c["criterion"] for c in i["rubric"]] for i in items}
    rows = list(csv.DictReader(io.StringIO(sheet_bytes.decode("utf-8"), newline="")))
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


def _flagged(s):
    """A full-strength item shows the detection pattern on its lowest criterion (a false alarm)."""
    return _marked_down(s, s.index(min(s)))


def _detect_flag(pairs, grades):
    weak = [(h, k) for h, k in pairs if k["candidate_type"] == "weakened"]
    full = [(h, k) for h, k in pairs if k["candidate_type"] == "full_strength"]
    detected = [h for h, k in weak if _marked_down(grades[h]["scores"], k["weakened_criterion"] - 1)]
    false_alarms = [h for h, _ in full if _flagged(grades[h]["scores"])]
    return weak, full, detected, false_alarms


def discrimination(key, grades):
    weak, full, detected, false_alarms = _detect_flag(list(key["items"].items()), grades)
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


def _baselines_exact(key_items):
    rnd = sum(sum(len(set(b) & {0, 1, 2}) / 3 for b in k["accepted_scores"]) / 3 for k in key_items) / len(key_items)
    all2 = sum(_agree([2, 2, 2], k["accepted_scores"]) for k in key_items) / len(key_items)
    sc = 0.0
    for k in key_items:
        if k["candidate_type"] == "weakened":
            c = k["weakened_criterion"] - 1
            sc += _agree([0 if i == c else 2 for i in range(3)], k["accepted_scores"])
        else:
            sc += sum(_agree([0 if i == c else 2 for i in range(3)], k["accepted_scores"]) for c in range(3)) / 3
    return {"uniform_random": rnd, "all_2s": all2, "shortcut_one_criterion_0": sc / len(key_items)}


def baselines(key_items):
    """Exact expected agreement of the three reference graders in BASELINE_DEFINITION over these key items."""
    b = _baselines_exact(key_items)
    return round(max(b.values()), 4), {k: round(v, 4) for k, v in b.items()}


def eligibility(its):
    n_full = sum(i["candidate_type"] == "full_strength" for i in its)
    n_weak = len(its) - n_full
    ok = len(its) >= MIN_ITEMS_PER_MAJOR and n_full >= 1 and n_weak >= 1
    reason = None if ok else (f"{len(its)} kit item(s); a per-asset record needs at least {MIN_ITEMS_PER_MAJOR} items with at "
                              "least one full-strength and one weakened item. These items count only toward the kit-level check.")
    return {"min_items": MIN_ITEMS_PER_MAJOR, "n_items": len(its), "n_full_strength": n_full, "n_weakened": n_weak,
            "eligible": ok, "reason": reason}


def evaluate(key, grades):
    """Kit-level discrimination plus every asset's pass decision. Pure function of the key and the grades (no I/O), so
    the tests can run it on many made-up keys. Returns (kit_discrimination, {asset_id: asset result})."""
    disc = discrimination(key, grades)
    by_asset = {}
    for h, k in key["items"].items():
        by_asset.setdefault(k["asset_id"], []).append((h, k))
    out = {}
    for aid, pairs in sorted(by_asset.items()):
        kis = [k for _, k in pairs]
        n_in = sum(s in b for h, k in pairs for s, b in zip(grades[h]["scores"], k["accepted_scores"]))
        agreement_exact = n_in / (3 * len(pairs))
        base_exact = max(_baselines_exact(kis).values())
        base, base_all = baselines(kis)
        elig = eligibility(kis)
        weak, full, detected, false_alarms = _detect_flag(pairs, grades)
        det_rate = len(detected) / len(weak) if weak else None
        fa_rate = len(false_alarms) / len(full) if full else None
        bad_full = [h for h, k in full if grades[h].get("factually_correct") == "no"]
        checks = {"kit_discrimination": bool(disc["passed"]),
                  "eligible": elig["eligible"],
                  "asset_detection_rate": det_rate is not None and det_rate >= DETECTION_MIN,
                  "asset_false_alarm_rate": fa_rate is not None and fa_rate <= FALSE_ALARM_MAX,
                  "agreement_min": agreement_exact >= AGREEMENT_MIN,
                  "agreement_above_baseline": agreement_exact > base_exact + 1e-12,
                  "no_full_strength_judged_incorrect": not bad_full}
        out[aid] = {"score": round(agreement_exact, 4), "baseline_score": base, "baselines": base_all, "eligibility": elig,
                    "asset_discrimination": {"n_weakened": len(weak), "detected": len(detected),
                                             "detection_rate": None if det_rate is None else round(det_rate, 4),
                                             "n_full_strength": len(full), "false_alarms": len(false_alarms),
                                             "false_alarm_rate": None if fa_rate is None else round(fa_rate, 4),
                                             "detection_min": DETECTION_MIN, "false_alarm_max": FALSE_ALARM_MAX},
                    "full_strength_judged_incorrect": bad_full, "checks": checks, "passed": all(checks.values())}
    return disc, out


def limitations_text(grader, n_items, elig, git_note=None):
    owner = norm_name(grader).casefold() in OWNER_NAMES or norm_name(grader).casefold().startswith("irean")
    t = (f"One human grader, {grader}: the only grader named on the sheet and the grader declared in GRADING_FINAL.txt. "
         + ("The grader is the owner of DreamCo, so the result is not independent of DreamCo. " if owner else
            "This script does not verify the grader's independence from DreamCo. ")
         + "Candidate answers were written by the builder for the kit and are not learner responses; the result shows whether "
           "the rubrics discriminate when a human applies them, not learning outcomes. "
         + f"This asset has {n_items} kit item(s) ({elig['n_full_strength']} full-strength, {elig['n_weakened']} weakened).")
    if not elig["eligible"]:
        t += " Too few items for a per-asset result: the record cannot pass."
    if git_note:
        t += " " + git_note
    return t


def parse_final(final_bytes):
    m = FINAL_RX.search(final_bytes.decode("utf-8", "replace")) if final_bytes is not None else None
    if not m or not iso_with_offset(m["at"]):
        raise SystemExit("GRADING_FINAL.txt with 'FINAL: grader=<name>; declared_at=<ISO with offset>; sheet_sha256=<sha256 of "
                         "grading_sheet.csv>' is required before --finalize")
    return {"grader": norm_name(m["grader"]), "declared_at": m["at"], "sheet_sha256": m["sheet"]}


def parse_commitment(commit_bytes):
    return dict(l.split(": ", 1) for l in commit_bytes.decode("utf-8").splitlines() if ": " in l)


def check_local_clone(g, kit, out_dir):
    """Local facts, via /usr/bin/git in the sanitized session: the canonical kit and output paths in a clone whose branch
    remote is the canonical repository, on an allowed branch, with the grading files tracked and clean. Returns
    (grading_commit, head, remote_branch, files)."""
    kit = pathlib.Path(kit).resolve()
    r = g.run(kit, "rev-parse", "--show-toplevel")
    if r.returncode:
        raise SystemExit(f"{kit} is not inside a git repository; --finalize scores only a committed and pushed sheet")
    top = pathlib.Path(r.stdout.strip()).resolve()
    if kit != top / KIT_REL:
        raise SystemExit(f"the kit directory must be <repo root>/{KIT_REL}; got {kit}. Refusing to score a copy of the kit")
    if pathlib.Path(out_dir).resolve() != top / OUT_REL:
        raise SystemExit(f"the output directory must be <repo root>/{OUT_REL} inside the canonical pack; got {out_dir}")
    rel = [f"{KIT_REL}/grading_sheet.csv", f"{KIT_REL}/GRADING_FINAL.txt"]
    for rp in rel:
        if g.run(top, "ls-files", "--error-unmatch", "--", rp).returncode:
            raise SystemExit(f"{rp} is not committed in git; commit and push the sheet and GRADING_FINAL.txt first")
    dirty = g.run(top, "status", "--porcelain", "--untracked-files=no", "--", *rel).stdout.strip()
    if dirty:
        raise SystemExit("the sheet or GRADING_FINAL.txt has uncommitted changes; commit and push them first:\n" + dirty)
    commit = g.run(top, "log", "-1", "--format=%H", "--", *rel).stdout.strip()
    head = g.run(top, "rev-parse", "HEAD").stdout.strip()
    branch = g.run(top, "symbolic-ref", "-q", "--short", "HEAD").stdout.strip()
    if not branch:
        raise SystemExit("HEAD is detached; check out the branch the grading commit was pushed to")
    remote = g.run(top, "config", "--get", f"branch.{branch}.remote").stdout.strip() or "origin"
    merge = g.run(top, "config", "--get", f"branch.{branch}.merge").stdout.strip()
    remote_branch = merge[len("refs/heads/"):] if merge.startswith("refs/heads/") else branch
    if remote_branch not in ALLOWED_BRANCHES:
        raise SystemExit(f"branch {remote_branch!r} is not an allowed grading branch ({', '.join(ALLOWED_BRANCHES)})")
    url = g.run(top, "config", "--get", f"remote.{remote}.url").stdout.strip()
    if normalize_remote(url) != CANONICAL_REPO:
        raise SystemExit(f"the remote {remote!r} of branch {branch!r} is not {CANONICAL_REMOTE_URL} (strict https or ssh "
                         "form); refusing to score a kit outside the canonical repository")
    if g.run(top, "config", "--get-regexp", r"^url\..*\.(insteadof|pushinsteadof)$").stdout.strip():
        raise SystemExit("git url rewriting (url.*.insteadOf) is configured; refusing, because it could redirect the remote")
    return commit, head, remote_branch, rel


def prior_finalizations(root, kit, key_sha):
    """Run ids already scored for this key commitment in the working tree (FINALIZED.txt, REVEALED_KEY.json, holdout
    results files). The git-history check is separate (verify_holdout.GitSession.finalizations)."""
    runs = set()
    fp = kit / "FINALIZED.txt"
    if fp.is_file():
        d = dict(l.split(": ", 1) for l in fp.read_text().splitlines() if ": " in l)
        if d.get("key_sha256") == key_sha:
            runs.add(d.get("run_id", "?"))
    if (kit / "REVEALED_KEY.json").exists():
        runs.add("REVEALED_KEY.json")
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
    p.write_text(f"FINAL: grader={name}; declared_at={at}; sheet_sha256={vh.sha(sheet_bytes)}\n")
    print(f"wrote {p}. The sheet is now locked: do not change grading_sheet.csv. Commit and push grading_sheet.csv and "
          "GRADING_FINAL.txt.")


def _committed_inputs(kit, out_dir, run_id, test_reasons, require_signer=None):
    """Everything --finalize scores, read exactly once. Outside the test-only bypass the bytes come from `git show
    <grading_commit>:<path>` in a fresh mirror of the real remote, never from the working tree."""
    names = ("grading_sheet.csv", "GRADING_FINAL.txt", "items.json", "KEY_COMMITMENT.txt")
    if os.environ.get(TEST_ONLY_SKIP_GIT_ENV) == "1":
        data = {n: (kit / n).read_bytes() if (kit / n).is_file() else None for n in names}
        info = {"grading_commit": None, "remote_url": None, "remote_branch": None, "remote_tip_sha": None,
                "skipped": "; ".join(test_reasons)}
        return data, info
    try:
        with vh.GitSession(REMOTE_FETCH_URL) as g:
            commit, head, remote_branch, rel = check_local_clone(g, kit, out_dir)
            tips = g.ls_remote(ALLOWED_BRANCHES)
            if remote_branch not in tips:
                raise SystemExit(f"the remote has no branch refs/heads/{remote_branch}; push the grading commit to it first")
            g.fetch(tips)
            tip = tips[remote_branch]
            if not g.is_ancestor(commit, tip):
                raise SystemExit(f"grading commit {commit[:12]} is not contained in the real remote tip {tip[:12]} of "
                                 f"{remote_branch} (git ls-remote); push it to that branch first")
            rev_p = f"{KIT_REL}/REVEALED_KEY.json"
            if g.blob_id(commit, rev_p) or g.rev_list("--full-history", commit, "--", rev_p):
                raise SystemExit("REVEALED_KEY.json exists at the grading commit or before it; refusing to score")
            want = [g.blob_id(commit, p) for p in rel]
            later = [c[:12] for c in g.rev_list("--ancestry-path", f"{commit}..{tip}") if [g.blob_id(c, p) for p in rel] != want]
            if [g.blob_id(tip, p) for p in rel] != want or later:
                raise SystemExit(f"grading_sheet.csv or GRADING_FINAL.txt changes on the remote after the grading commit "
                                 f"({later[:3]}); pull, and commit the final sheet and declaration once")
            if require_signer is not None:
                ok_sig, detail = g.check_signer(commit, require_signer)
                if not ok_sig:
                    raise SystemExit(f"grading commit {commit[:12]} is not signed by the registered key: {detail}")
            data = {n: g.show(commit, f"{KIT_REL}/{n}") for n in names}
            if data["KEY_COMMITMENT.txt"] is not None:
                hist = g.finalizations(parse_commitment(data["KEY_COMMITMENT.txt"]).get("key_sha256", "?"))
                if hist:
                    raise SystemExit("this key commitment was already finalized in git history on the remote ("
                                     + ", ".join(hist[:5]) + "); a kit is scored once")
    except vh.VerifyError as e:
        raise SystemExit(f"{e}; refusing to score")
    used = CANONICAL_REMOTE_URL if REMOTE_FETCH_URL == vh.CANONICAL_FETCH_URL else REMOTE_FETCH_URL
    info = {"grading_commit": commit, "head_commit": head, "remote_url": used, "remote_branch": remote_branch,
            "remote_tip_sha": tip, "checked_against": "git ls-remote and a fresh fetch of the remote with /usr/bin/git in a "
            "sanitized environment; local refs are not used", "inputs_read_from": f"git show {commit}:<path>",
            "kit_dir": KIT_REL, "output_dir": OUT_REL, "files": rel,
            "repository_root": "git work tree containing the kit (path not recorded)"}
    if test_reasons:
        info["test_only"] = "; ".join(test_reasons)
    return data, info


def finalize(a, kit):
    root = pathlib.Path(a.root)
    out_base = root / "data/dreamco_knowledge/evidence/holdout"
    run_id = a.run_id or datetime.datetime.now().astimezone().strftime("%Y%m%d") + "-01"
    if not re.fullmatch(r"\d{8}-\d{2}", run_id):
        raise SystemExit("--run-id must be YYYYMMDD-NN")
    test_reasons = []
    if os.environ.get(TEST_ONLY_SKIP_GIT_ENV) == "1":
        test_reasons.append(f"TEST ONLY: {TEST_ONLY_SKIP_GIT_ENV}=1 skipped the git, remote and canonical-path checks")
    if REMOTE_FETCH_URL != vh.CANONICAL_FETCH_URL:
        test_reasons.append(f"TEST ONLY: REMOTE_FETCH_URL was overridden to {REMOTE_FETCH_URL!r}, so the push was not "
                            "checked against the canonical remote")
    test_only = bool(test_reasons)
    data, git_info = _committed_inputs(kit, out_base, run_id, test_reasons, a.require_signer)
    sheet_bytes, final_b, items_b, commit_b = (data[n] for n in ("grading_sheet.csv", "GRADING_FINAL.txt", "items.json",
                                                                 "KEY_COMMITMENT.txt"))
    if sheet_bytes is None or items_b is None or commit_b is None:
        raise SystemExit("grading_sheet.csv, items.json or KEY_COMMITMENT.txt is missing at the grading commit")
    decl = parse_final(final_b)
    if vh.sha(sheet_bytes) != decl["sheet_sha256"]:
        raise SystemExit("grading_sheet.csv does not match sheet_sha256 in GRADING_FINAL.txt (the sheet changed after "
                         "grading was declared final); refusing to score")
    items_doc = json.loads(items_b)
    grades, errs = load_sheet(sheet_bytes, items_doc["items"])
    if errs:
        raise SystemExit("grading sheet incomplete or invalid:\n  " + "\n  ".join(errs))
    graders = sorted({g["grader"] for g in grades.values()})
    if graders != [decl["grader"]]:
        raise SystemExit(f"the sheet must name exactly one grader, the one declared in GRADING_FINAL.txt "
                         f"({decl['grader']!r}); it names {graders}")
    grader = decl["grader"]
    commit = parse_commitment(commit_b)
    prior = prior_finalizations(root, kit, commit["key_sha256"])
    if prior:
        raise SystemExit(f"this key commitment was already finalized (run {', '.join(prior)}); a kit is scored once")
    if vh.sha(items_b) != commit["items_json_sha256"]:
        raise SystemExit("items.json was changed after the kit was drawn; refusing to score")
    # the key is decrypted only now, after the declaration and the sheet are committed and pushed
    key_b = holdout_crypto.decrypt_bytes(pathlib.Path(a.key).read_bytes(), holdout_crypto.read_passphrase(a.passphrase_file),
                                         "holdout_key")
    if vh.sha(key_b) != commit["key_sha256"]:
        raise SystemExit("key does not match KEY_COMMITMENT.txt (sha256 differs); refusing to score")
    key = json.loads(key_b)
    by_id = {i["item_id"]: i for i in items_doc["items"]}
    if set(key["items"]) != set(by_id):
        raise SystemExit("key and items.json list different items")
    for h, k in key["items"].items():
        if vh.sha(by_id[h]["candidate_answer"].encode()) != k["candidate_answer_sha256"]:
            raise SystemExit(f"{h}: candidate answer differs from the key")
    disc, assets = evaluate(key, grades)
    now = datetime.datetime.now().astimezone()
    per_asset = {}
    for h, k in key["items"].items():
        g = grades[h]
        agree = [s in band for s, band in zip(g["scores"], k["accepted_scores"])]
        per_asset.setdefault(k["asset_id"], []).append({
            "item_id": h, "candidate_type": k["candidate_type"], "weakened_criterion": k["weakened_criterion"],
            "expected_scores": k["expected_scores"], "accepted_scores": k["accepted_scores"], "human_scores": g["scores"],
            "criterion_agreement": agree, "factually_correct": g["factually_correct"], "comments": g["comments"]})
    majors = {m_["asset_id"]: m_ for m_ in json.loads((root / "data/majors_selected.json").read_text())}
    evaluator = (f"edu-career-pathways score_holdout.py sha256:{vh.sha((ROOT / 'score_holdout.py').read_bytes())}; "
                 f"verify_holdout.py sha256:{vh.sha((ROOT / 'verify_holdout.py').read_bytes())}; "
                 f"holdout_crypto.py sha256:{vh.sha((ROOT / 'holdout_crypto.py').read_bytes())}")
    git_fields = {f: git_info[f] for f in ("grading_commit", "remote_url", "remote_branch", "remote_tip_sha")}
    written = []
    for aid, its in sorted(per_asset.items()):
        res_a = assets[aid]
        cip = majors[aid]["cip"]
        stem = next((root / "study_plans").glob(f"{cip}_*.md")).stem
        asset = json.loads((root / "study_plans" / stem / "asset.json").read_text())
        passed = bool(res_a["passed"]) and not test_only
        lim = limitations_text(grader, len(its), res_a["eligibility"], " ".join(test_reasons) or None)
        results_path = f"{EVIDENCE_ROOT}/holdout/{aid}/{run_id}.results.json"
        results = {"schema": "dreamco.edu_career_pathways.holdout_results.v5", "asset_id": aid, "run_id": run_id,
                   "kit": key["kit"], "kit_created_at": key["created_at"], "key_sha256": vh.sha(key_b),
                   "items_json_sha256": commit["items_json_sha256"], "grading_sheet_sha256": vh.sha(sheet_bytes),
                   "graders": [grader], "declared_final": decl, "grading_git": git_info, **git_fields,
                   "revealed_key_path": f"{KIT_REL}/REVEALED_KEY.json",
                   "asset_integrity_hash": asset["integrity_hash"], "split": SPLIT, "metric": METRIC,
                   "threshold": AGREEMENT_MIN, "n_items": len(its), "score": res_a["score"],
                   "baseline_score": res_a["baseline_score"], "baselines": res_a["baselines"],
                   "baseline_definition": BASELINE_DEFINITION, "per_asset_eligibility": res_a["eligibility"],
                   "asset_discrimination": res_a["asset_discrimination"], "pass_checks": res_a["checks"],
                   "rule_passed": bool(res_a["passed"]), "test_only": test_only, "test_only_reasons": test_reasons,
                   "passed": passed, "kit_discrimination": disc,
                   "full_strength_judged_incorrect": res_a["full_strength_judged_incorrect"], "items": its,
                   "limitations": lim}
        rb = (json.dumps(results, indent=2, ensure_ascii=False) + "\n").encode()
        rec = {"evidence_id": f"holdout:{aid}:{run_id}", "capability_id": "career-pathway-study-plan",
               "source_type": "human_evaluation", "source_reference": asset["integrity_hash"],
               "retrieved_at": now.isoformat(timespec="seconds"),
               "content_version": f"{aid} plan {asset['integrity_hash']}; {key['kit']} drawn {key['created_at']}",
               "license_or_usage_basis": f"DreamCo-original evaluation by human grader {grader} of DreamCo-original kit items.",
               "transformation": "original_evaluation", "evaluator_version": f"{evaluator}; human grader: {grader}",
               "integrity_hash": "sha256:" + vh.sha(rb), "results_path": results_path, "evidence_root": EVIDENCE_ROOT,
               "paths_relative_to": PATHS_RELATIVE_TO, "split": SPLIT, "n_items": len(its), "metric": METRIC,
               "score": res_a["score"], "baseline_score": res_a["baseline_score"], "baseline_definition": BASELINE_DEFINITION,
               "threshold": AGREEMENT_MIN, "passed": passed, "test_only": test_only, "grader": grader, **git_fields,
               "verification": "python verify_holdout.py <this record> (run by someone other than the scorer)",
               "limitations": lim}
        out = out_base / aid
        if (out / f"{run_id}.json").exists():
            raise SystemExit(f"{out / (run_id + '.json')} exists; evidence is append-only, use a new --run-id")
        written.append((out, run_id, rb, rec))
    for out, run_id, rb, rec in written:
        out.mkdir(parents=True, exist_ok=True)
        (out / f"{run_id}.results.json").write_bytes(rb)
        (out / f"{run_id}.json").write_text(json.dumps(rec, indent=2, ensure_ascii=False) + "\n")
        print(rec["evidence_id"], f"n_items={rec['n_items']} score={rec['score']} baseline={rec['baseline_score']} "
              f"passed={rec['passed']}" + (" (TEST ONLY)" if test_only else ""))
    # publish the reveal: the exact plaintext key bytes, so anyone can recompute the commitment and every score
    (kit / "REVEALED_KEY.json").write_bytes(key_b)
    (kit / "FINALIZED.txt").write_text(f"key_sha256: {commit['key_sha256']}\nrun_id: {run_id}\n"
                                       f"grading_sheet_sha256: {vh.sha(sheet_bytes)}\ngrading_commit: {git_info['grading_commit']}\n"
                                       f"remote_url: {git_info['remote_url']}\nremote_branch: {git_info['remote_branch']}\n"
                                       f"remote_tip_sha: {git_info['remote_tip_sha']}\ntest_only: {test_only}\n"
                                       f"revealed_key: REVEALED_KEY.json (sha256 = key_sha256)\n"
                                       f"finalized_at: {now.isoformat(timespec='seconds')}\n"
                                       "note: this key commitment has been scored; score_holdout.py refuses to finalize it again.\n")
    print("kit discrimination:", json.dumps({k: v for k, v in disc.items() if k != "per_major_with_both_types"}))
    print("Next: commit data/dreamco_knowledge/evidence/holdout/, evidence/holdout_kit/REVEALED_KEY.json and "
          "evidence/holdout_kit/FINALIZED.txt together in ONE commit (the reveal commit) on top of the grading commit, push it, "
          f"run `python score_holdout.py --record-shas --run-id {run_id}` and commit VERIFIED_SHAS.json, then have someone other "
          "than the scorer run verify_holdout.py on each record.")


def record_shas(a, kit):
    """After the reveal commit is pushed: verify every record of the run (verify_holdout.verify against the remote) and
    write evidence/holdout_kit/VERIFIED_SHAS.json with grading_commit, reveal_commit and the remote tip, so that a later
    force-push that rewrites history is detectable (verify_holdout --expect-shas)."""
    if not a.run_id or not re.fullmatch(r"\d{8}-\d{2}", a.run_id):
        raise SystemExit("--record-shas needs --run-id YYYYMMDD-NN")
    recs = sorted(pathlib.Path(a.root).glob(f"data/dreamco_knowledge/evidence/holdout/*/{a.run_id}.json"))
    if not recs:
        raise SystemExit(f"no holdout records for run {a.run_id}")
    test_remote = None if REMOTE_FETCH_URL == vh.CANONICAL_FETCH_URL else REMOTE_FETCH_URL
    shas, results = set(), []
    for p in recs:
        r = vh.verify(p, require_signer=a.require_signer, _test_remote=test_remote)
        if not r["ok"]:
            raise SystemExit(f"{p.name} ({p.parent.name}) does not verify: " + "; ".join(r["errors"][:5]))
        shas.add((r["shas"]["grading_commit"], r["shas"]["reveal_commit"], r["shas"]["remote_branch"], r["shas"]["remote_tip_sha"]))
        results.append(r)
    if len(shas) != 1:
        raise SystemExit(f"the records of run {a.run_id} verify against different commits: {sorted(shas)}")
    gc, reveal, branch, tip = shas.pop()
    out = {"run_id": a.run_id, "grading_commit": gc, "reveal_commit": reveal, "remote_branch": branch, "remote_tip_sha": tip,
           "remote_url": CANONICAL_REMOTE_URL if test_remote is None else test_remote, "test_only": test_remote is not None
           or any(r["record_test_only"] for r in results), "records": [p.parent.name for p in recs],
           "recorded_at": datetime.datetime.now().astimezone().isoformat(timespec="seconds"),
           "verifier": f"verify_holdout.py sha256:{vh.sha((ROOT / 'verify_holdout.py').read_bytes())}",
           "check_with": "python verify_holdout.py <record> --expect-shas evidence/holdout_kit/VERIFIED_SHAS.json"}
    (kit / "VERIFIED_SHAS.json").write_text(json.dumps(out, indent=2) + "\n")
    print(f"wrote {kit / 'VERIFIED_SHAS.json'}: grading_commit={gc} reveal_commit={reveal} remote_tip_sha={tip}. "
          "Commit and push it; keep a copy outside the repository too (a force-push could rewrite it).")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sheet", default=None, help="dry run only may use another path; --declare-final and --finalize "
                    "require <kit-dir>/grading_sheet.csv")
    ap.add_argument("--kit-dir", default=str(ROOT / "evidence" / "holdout_kit"))
    ap.add_argument("--key", default=str(PRIVATE / "holdout_key.json.enc"), help="encrypted private key (outside the repo)")
    ap.add_argument("--passphrase-file", default=None, help="default: $DREAMCO_HOLDOUT_PASSPHRASE_FILE or "
                    + holdout_crypto.DEFAULT_PASSPHRASE_FILE)
    ap.add_argument("--root", default=str(ROOT), help="pack root (for tests)")
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--finalize", action="store_true", help="score and write evidence (after GRADING_FINAL.txt is committed and pushed)")
    g.add_argument("--declare-final", action="store_true", help="grader: lock the sheet by writing GRADING_FINAL.txt")
    g.add_argument("--record-shas", action="store_true", help="after the reveal commit is pushed: verify the run and write "
                   "VERIFIED_SHAS.json (grading_commit, reveal_commit, remote tip)")
    ap.add_argument("--require-signer", default=None, help="optional: grading_commit must be signed by this key (SSH "
                    "fingerprint SHA256:..., allowed_signers file, or armored GPG public key file)")
    ap.add_argument("--grader", default=None, help="with --declare-final: your name, as written on every sheet row")
    ap.add_argument("--run-id", default=None)
    a = ap.parse_args()
    kit = pathlib.Path(a.kit_dir)
    canonical_sheet = kit / "grading_sheet.csv"
    if a.sheet and (a.finalize or a.declare_final) and pathlib.Path(a.sheet).resolve() != canonical_sheet.resolve():
        raise SystemExit(f"--sheet must be the canonical {canonical_sheet} for --declare-final and --finalize (non-canonical "
                         f"--sheet {a.sheet} refused)")
    if a.record_shas:
        return record_shas(a, kit)
    if a.finalize:
        return finalize(a, kit)  # reads every scoring input itself, once, from the grading commit
    sheet_bytes = pathlib.Path(a.sheet or canonical_sheet).read_bytes()
    items_doc = json.loads((kit / "items.json").read_bytes())
    grades, errs = load_sheet(sheet_bytes, items_doc["items"])
    if errs:
        raise SystemExit("grading sheet incomplete or invalid:\n  " + "\n  ".join(errs))
    if a.declare_final:
        return declare_final(a, kit, grades, sheet_bytes)
    print(f"Sheet format OK: all {len(grades)} rows complete. No scores were computed (dry run). "
          "When grading is final, run --declare-final --grader \"<your name>\" and ask the builder to run --finalize.")


if __name__ == "__main__":
    main()
