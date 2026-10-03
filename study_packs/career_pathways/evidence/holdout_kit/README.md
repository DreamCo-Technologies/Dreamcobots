# Blind holdout grading kit (v3: rubric discrimination)

The kit is for the owner (Irean), currently the only available human grader. It checks whether the rubric, applied blind by a human, separates full-strength answers from subtly weakened ones. It has 18 new scenario prompts across 13 authored majors: 6 for Computer Science (11.0701), and 1 each for Computer Engineering, Registered Nursing, Psychology, Biology, Mechanical Engineering, Civil Engineering, Accounting, Marketing, Elementary Education, Chemistry, Statistics and Social Work.

The prompts and candidate answers were written for this kit only. They do not appear in the published study plans, `data/practice_tasks.json`, `authored/`, the pack's READMEs and docs, the O*NET text or the earlier v1 and v2 kits, and a test checks that no 5-word run is shared. The candidate answers are not learner responses. Some are full-strength and some are subtly weakened on one rubric criterion. How many are weakened is drawn at random for each kit and is secret; it is not a fixed fraction, and it is not written anywhere you can see. Every answer has the same shape: five labelled points of similar length. Length and layout tell you nothing.

**No grades have been entered. No holdout evidence exists until this sheet is filled in, declared final and scored.**

## Replacement notes

The v1 kit (12 items drawn from the authored practice tasks, with `_key.json` in this folder) was deleted on 2026-10-02. It was not blind: its prompts and answers matched published content, and its key was committed and could be regenerated.

The v2 draw (16 items, committed in def1d2d) was replaced on 2026-10-02 before anyone graded it, after the Data-Package Merchant's blindness audit: it always weakened the same number of answers, it had no false-alarm penalty, single-item majors could produce passing records, the sheet was not locked to the final declaration, and its key was stored in plaintext. The v2 items are public in git history, so drawing them again would have let anyone compare the two versions of any item whose shown version changed. This v3 kit therefore uses 18 newly written items (none reused from v2, six of them for Computer Science), a new seed and nonce, and the fixes described below.

Kits are not evidence, so replacing them does not affect the append-only evidence in `data/dreamco_knowledge/evidence/`.

## What is here

- `items.md`: the 18 items to grade. `items.json` has the same content.
- `grading_sheet.csv`: the blank sheet, one row per item.
- `KEY_COMMITMENT.txt`: the sha256 of the answer key. The key itself is kept by the builder, encrypted, outside the repository; it is not in this folder or anywhere in the repo. The key contains a random 256-bit nonce, so the hash cannot be matched by guessing. Scoring refuses any key that does not match this hash, so the key cannot be changed after you grade.

## How to grade (about 70 to 85 minutes)

1. Read each item in `items.md`: the major, a scenario prompt, a candidate answer, and a 3-criterion rubric.
2. Score each criterion in `grading_sheet.csv`, judging only against that item's rubric:
   - 0: missing or wrong.
   - 1: partly there, vague, or with a real flaw.
   - 2: clearly and correctly covered.
3. Grade each item on its own merits. Do not try to balance scores across items or assume any particular number of weak answers. Marking a criterion down on an answer that is actually full-strength counts against the kit (see the false-alarm rule), so only mark down what the rubric really finds missing.
4. Fill in `factually_correct` with `yes`, `no` or `unsure`. This is your judgment of whether the answer contains anything wrong for the field.
5. Use `comments` for anything you would change in the prompt, rubric or answer.
6. Put your name in `grader`, and the date and time in `graded_at` (ISO 8601 with offset, e.g. `2026-10-05T14:30:00-05:00`), on every row. Use the same name on every row: a sheet with more than one grader name cannot be scored. Do not edit `item_id`, `major` or the criterion columns.
7. Optional: `python score_holdout.py` checks only that the sheet is complete and well formed. It never opens the key and prints no scores; it prints the same message for every complete sheet.
8. When you are done, lock the sheet by declaring grading final:
   `python score_holdout.py --declare-final --grader "<your name>"`
   This writes `GRADING_FINAL.txt` in this folder with one line:
   `FINAL: grader=<your name>; declared_at=<ISO date-time with offset>; sheet_sha256=<sha256 of grading_sheet.csv>`
   (You can also write that line yourself; `sha256sum grading_sheet.csv` gives the hash.) After that, do not change the sheet: scoring refuses a sheet whose sha256 differs from `sheet_sha256`.
9. Commit `grading_sheet.csv` and `GRADING_FINAL.txt` in git and push the commit. Scoring refuses a sheet or declaration that is not committed, has uncommitted changes, or whose commit is not on a remote-tracking branch.

Do not run `score_holdout.py --finalize` yourself, and do not look at its output before you have declared grading final.

## Scoring (builder, after GRADING_FINAL.txt is committed and pushed)

Run this from a git clone of the repository (the sheet and `GRADING_FINAL.txt` must be inside its work tree):

```
python score_holdout.py --finalize --run-id <YYYYMMDD>-<NN>
python build.py      # links passing records into asset.json validation_evidence_ids.holdout
```

`--finalize` takes these steps:
1. It checks `GRADING_FINAL.txt`: the sheet's sha256 must equal `sheet_sha256`, and the sheet must name exactly one grader, the one declared.
2. It checks git, before the key is touched: the sheet and `GRADING_FINAL.txt` must be inside the repository's work tree (a sheet outside the repo is refused), tracked, free of uncommitted changes, identical to their committed version at `HEAD`, and the last commit that touched them must be contained in a remote-tracking branch (pushed). That commit's SHA is recorded as `grading_commit`.
3. It refuses if this key commitment was already scored (`FINALIZED.txt` here, or any holdout results file with the same `key_sha256`). A kit is scored once; a second `--finalize` under a new run id is refused.
4. It decrypts the private key in memory, checks its sha256 against `KEY_COMMITMENT.txt`, and checks that `items.json` is unchanged.
5. It writes one record per asset with kit items: `holdout:<asset_id>:<run>` under `data/dreamco_knowledge/evidence/holdout/<asset_id>/`, and then `FINALIZED.txt` here. Each record has source_type human_evaluation, transformation original_evaluation, split `holdout`, `grading_commit`, integrity_hash = sha256 of its results file, and `results_path` relative to the same repository root as `evidence_root` (`study_packs/career_pathways/data/dreamco_knowledge/evidence`).

For the test suite only, `DREAMCO_HOLDOUT_TEST_ONLY_SKIP_GIT=1` skips the git checks. A run under it records `grading_commit: null`, says TEST ONLY in its limitations and can never produce a passing record.

## Pass rule

A record can pass only if the grader discriminated across the whole kit. All three of these must hold:

- **Detection rate ≥ 0.8.** A weakened item counts as detected when its weakened criterion is scored ≤ 1 and lower than the mean of that item's other two criteria.
- **False-alarm rate ≤ 0.2.** A full-strength item counts as flagged when its lowest criterion is scored ≤ 1 and lower than the mean of its other two criteria (the same pattern as a detection). The kit fails if more than 20% of the full-strength items are flagged.
- **Mean gap ≥ 1.0 on the 0-2 scale.** This is the mean of all criterion scores on full-strength items minus the mean of the weakened-criterion scores on weakened items.

Giving everything the same score (for example all 2s) detects nothing and fails every record. Marking one criterion down on every item (the shortcut grader) flags every full-strength item and fails every record; the tests check that this shortcut passes in none of thousands of random keys while a perfect grader passes in all of them.

Given kit-level discrimination, each asset's record also needs all of these, computed on that asset's own items:
- It has at least 4 kit items, with at least one full-strength and one weakened item. Majors with a single item count only toward the kit-level check; their records cannot pass. In this kit only Computer Science has enough items, and the draw always gives it both kinds.
- **Asset detection rate ≥ 0.8** on its own weakened items (same definition of detected as above). With few weakened items in an asset this means all or nearly all of them.
- **Asset false-alarm rate ≤ 0.2** on its own full-strength items (same definition of flagged as above).
- Agreement ≥ 0.8. This is the fraction of its criterion scores inside the key's accepted band: 1-2 for full-strength criteria, 0-1 for the weakened criterion.
- **Agreement strictly above the asset's own `baseline_score`** (compared exactly, before rounding).
- No full-strength item judged factually incorrect.

`baseline_score` is the highest expected agreement on that asset's items among three graders who cannot tell the answer types apart (uniform random scores; all 2s; the shortcut grader in its best case, which marks the true weakened criterion down on weakened items and a random criterion on full-strength items), computed exactly from the key. Agreement alone can be beaten by such graders (all 2s scores well when most of an asset's items are full-strength). The kit-level checks alone are not enough either: a grader who is perfect on the other majors and gives all 2s on Computer Science used to pass the kit-level checks and the agreement threshold for Computer Science in about 40% of random keys. The per-asset detection, false-alarm and above-baseline checks close that: the tests check that this grader, all 2s, all 0s, all 1s, the shortcut grader and a grader who marks the wrong criterion on Computer Science pass no record in 2,000 random keys each, that a perfect grader passes Computer Science in every key, and that an honest grader who detects about 95% of weakened answers (with a 1% false-alarm rate) passes Computer Science in most keys (about 87% in the test's simulation). The results file lists each check under `pass_checks` and the asset's counts under `asset_discrimination`.

The results file also reports, for majors that happen to have both answer types, how many weakened items scored below every full-strength item of that major. This is for information only.

The draw rule (how many answers are weakened, and how many of those are Computer Science items) is in `make_holdout_kit.py` (`draw_weak`). The number drawn for this kit is stored only in the encrypted key.

**Item order.** The order Q01 to Q18 is the result of the single `rng.shuffle` in the accepted draw. The builder did not inspect the order before accepting it, and no draw was rejected or repeated because of its order or of which answers it weakened. Earlier draws were discarded only because the private source text changed (the first used the retired v2 source; one failed the 5-word overlap check and the text was rewritten; one was rerun by mistake with the same source). The private acceptance checks included a shape check that uses the labels and would have forced a redraw if it had failed; it never failed. That five of the six Computer Science items fall in Q01 to Q05 is chance, not a choice.

## Threat model and key storage

The answer key and the authoring source (both answer versions of every item) are stored outside the repository in `/workspace/edu-career-pathways-private/` only as AES-256-GCM files (`holdout_key.json.enc`, `holdout_source.json.enc`), with the key derived by scrypt from a passphrase kept outside `/workspace` and outside the repo (`/home/box/.ecp-holdout/passphrase`, mode 600 in a mode 700 directory). The plaintext key is never written to disk; `--finalize` decrypts it in memory. GCM authentication means a modified file fails to decrypt, and the commitment (sha256 of the plaintext key) is checked after decryption.

This protects against a casual read: listing or opening the private folder reveals nothing about which answers are weakened. It does not protect against a deliberate attempt. **The passphrase is on the same shared box as the encrypted key.** Every agent runs under the same account, so any agent could read the passphrase and decrypt the key if it set out to. File permissions do not separate agents, and encryption with an on-box passphrase only raises the effort of a look. What this kit relies on is that the grader is a human (Irean) with no reason to look, and that agents are instructed not to decrypt or reveal the key. A grader who wanted to cheat could; this kit measures whether the rubric discriminates for an honest grader.

**Before any sale-grade use**, move the passphrase off the box (for example to the owner's password manager or another machine no agent can reach), delete it from `/home/box/.ecp-holdout/`, and supply it only for the scoring step, after `GRADING_FINAL.txt` and the sheet are committed and pushed. Then no one on the box can decrypt the key while grading is open. This has not been done for this kit: the passphrase is still at `/home/box/.ecp-holdout/passphrase`. The test suite never reads the real private folder or passphrase; it uses temporary made-up keys only, so it can be run by anyone.

## Limitations

There is one grader, and that grader is also the owner, so the result is not independent of DreamCo. Each record's limitations text is built from the grader actually named on the sheet and in `GRADING_FINAL.txt`. There are few items per asset, and only Computer Science can produce a passing per-asset record; with its few weakened items, a single miss fails it. The candidate answers were written by the builder, not by learners. The result shows whether the rubrics discriminate when a human applies them; it says nothing about learning outcomes.
