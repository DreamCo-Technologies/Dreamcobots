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
9. Commit `grading_sheet.csv` and `GRADING_FINAL.txt` in git and push the commit (recommended: as a signed commit from your own computer; see "Signed grading commit" below). Push to the pull-request branch `edu-career-pathways/majors-onet-study-plans` (or `main`) of github.com/DreamCo-Technologies/Dreamcobots. Scoring refuses a sheet or declaration that is not committed, has uncommitted changes, or whose commit is not on one of those branches on GitHub.

Do not run `score_holdout.py --finalize` yourself, and do not look at its output before you have declared grading final.

## Scoring (builder, after GRADING_FINAL.txt is committed and pushed)

Run this from a git clone of github.com/DreamCo-Technologies/Dreamcobots (such as `/workspace/dc-ecp`), on the branch the grading commit was pushed to, with network access to GitHub:

```
python score_holdout.py --finalize --run-id <YYYYMMDD>-<NN> [--require-signer <key>]
git add data/dreamco_knowledge/evidence/holdout evidence/holdout_kit/REVEALED_KEY.json evidence/holdout_kit/FINALIZED.txt
git commit -m "holdout evidence" && git push        # ONE reveal commit: evidence, REVEALED_KEY.json and FINALIZED.txt together
python score_holdout.py --record-shas --run-id <YYYYMMDD>-<NN>
git add evidence/holdout_kit/VERIFIED_SHAS.json && git commit -m "holdout verified SHAs" && git push
# then: python build.py, and ask someone else to run verify_holdout.py (and keep their own copy of VERIFIED_SHAS.json)
```

The reveal must be its own later commit: `REVEALED_KEY.json` is added exactly once, after the grading commit, in the same commit as the evidence and `FINALIZED.txt`, and is never changed afterward. `--record-shas` runs `verify_holdout.verify()` on every record of the run and writes `VERIFIED_SHAS.json` with `grading_commit`, `reveal_commit`, `remote_branch` and `remote_tip_sha` (refusing unless every record verifies with the same SHAs).

`--finalize` takes these steps. Every git call uses `/usr/bin/git` by absolute path (checked to be a root-owned executable; `git` is never looked up on `PATH`) with a minimal environment built from scratch: no inherited `GIT_*`, proxy or other variables, `HOME` and `XDG_*` in an empty temporary directory, `GIT_CONFIG_NOSYSTEM=1`, `GIT_CONFIG_GLOBAL=/dev/null`, and overrides for repository settings that could run commands (`core.fsmonitor`, hooks).
1. Local clone: the kit directory must be exactly `<repo root>/study_packs/career_pathways/evidence/holdout_kit` and the output directory `<repo root>/study_packs/career_pathways/data/dreamco_knowledge/evidence/holdout`; `--sheet`, if given, must be the canonical `grading_sheet.csv`; the branch must be `edu-career-pathways/majors-onet-study-plans` or `main`; its remote URL must normalize to `github.com/DreamCo-Technologies/Dreamcobots` under a strict parse (https with no userinfo, port, query or fragment; `ssh://git@github.com/...`; or `git@github.com:...`; host exactly github.com; owner and repo in any case, with or without `.git`); no `url.*.insteadOf` rewriting; the sheet and `GRADING_FINAL.txt` tracked and clean. Their last commit is `grading_commit`.
2. Real remote: `git ls-remote https://github.com/DreamCo-Technologies/Dreamcobots.git` for the allowed branches, then a fresh blobless fetch of them into a new temporary repository (the tips must match what ls-remote reported). `grading_commit` must equal or be an ancestor of the branch tip. Local `refs/remotes/...` are never used, and an unreachable remote is a refusal.
3. Reveal order and a frozen sheet: it refuses if `REVEALED_KEY.json` exists at `grading_commit` or in any of its ancestors, or if the sheet or `GRADING_FINAL.txt` changes on the remote after `grading_commit` (on any commit between it and the tip, or at the tip). With `--require-signer`, `grading_commit` must also carry a valid signature from that key (same check as the verifier).
4. A kit is scored once, enforced by history: it refuses if any commit reachable from the remote tips already contains `FINALIZED.txt`, `REVEALED_KEY.json` or a holdout results file for this key commitment, and also if any of those exists in the working tree.
5. Inputs read once: `grading_sheet.csv`, `GRADING_FINAL.txt`, `items.json` and `KEY_COMMITMENT.txt` are read exactly once each, with `git show <grading_commit>:study_packs/career_pathways/evidence/holdout_kit/<file>`. Those exact bytes are hashed and graded; the working-tree files are never used for scoring, so swapping the sheet after the commit changes nothing. The sheet's sha256 must equal `sheet_sha256`, and the sheet must name exactly one grader, the one declared.
6. Key: it decrypts the private key in memory, refuses unless its sha256 equals `key_sha256` in `KEY_COMMITMENT.txt`, and checks `items.json` against the commitment.
7. Output: one record per asset with kit items, `holdout:<asset_id>:<run>` under `data/dreamco_knowledge/evidence/holdout/<asset_id>/`, plus its results file; then `REVEALED_KEY.json` (the exact plaintext key, including its nonce and draw seed) and `FINALIZED.txt` here. Each record has source_type human_evaluation, transformation original_evaluation, split `holdout`, `grading_commit`, `remote_url`, `remote_branch`, `remote_tip_sha`, `test_only`, integrity_hash = sha256 of its results file, and `results_path` relative to the same repository root as `evidence_root` (`study_packs/career_pathways/data/dreamco_knowledge/evidence`).

**Publishing the reveal.** Once the evidence, `REVEALED_KEY.json` and `FINALIZED.txt` are committed and pushed, anyone can recompute the commitment (sha256 of `REVEALED_KEY.json` must equal `key_sha256`) and every score from the committed sheet. The key is revealed only after grading is final and scored; until then it stays encrypted outside the repo.

**Test-only runs.** `DREAMCO_HOLDOUT_TEST_ONLY_SKIP_GIT=1` (skips the git, remote and canonical-path checks and reads the working tree once) or any change to `REMOTE_FETCH_URL` in `score_holdout.py` (the URL that ls-remote and fetch contact) marks the run TEST ONLY: every record gets `test_only: true`, names the URL actually used, says TEST ONLY in its limitations, and has `passed: false` whatever the pass rule says (`rule_passed` in the results file shows the rule's outcome). The test suite never contacts the network: its runner points `REMOTE_FETCH_URL` at a local bare repository in a temporary folder, so all of its finalize runs are test-only.

## Independent verification (verify_holdout.py)

The scorer runs on a shared box, so it cannot prove its own push or its own arithmetic: anyone who can write to the box could put a fake `git` earlier on `PATH`, edit `score_holdout.py`, or change `REMOTE_FETCH_URL`. The hardening above stops the easy versions of this, but the trust rests on `verify_holdout.py` being run by **someone other than the scorer**, on their own machine. It uses only the Python standard library and `/usr/bin/git`.

CLI:
```
python verify_holdout.py data/dreamco_knowledge/evidence/holdout/<asset_id>/<run>.json [--repo-url URL] [--reveal-commit SHA] [--results RESULTS.json]
        [--expect-shas VERIFIED_SHAS.json | --expect-shas grading_commit=SHA,reveal_commit=SHA,remote_tip_sha=SHA]
        [--require-signer SHA256:<ssh fingerprint> | --require-signer allowed_signers | --require-signer owner-gpg-key.asc] [--json]
```
Exit code 0 means accepted, 1 rejected (the reasons are printed), 2 a usage error. `--repo-url` must normalize to the canonical repository (default `https://github.com/DreamCo-Technologies/Dreamcobots.git`); git always contacts the canonical https URL. The reveal commit is the single commit that added `REVEALED_KEY.json`; `--reveal-commit`, if given, must equal it. It always prints the verified SHAs (`grading_commit`, `reveal_commit`, `remote_branch`, `remote_tip_sha`).

`--expect-shas` compares against SHAs recorded earlier: `VERIFIED_SHAS.json`, a saved `--json` result (its `shas`), or `key=value` pairs. It rejects unless `grading_commit` and `reveal_commit` are equal to the recorded ones and the recorded `remote_tip_sha` is still reachable from an allowed tip. Keep your own copy of the file: a copy inside the repo can be rewritten by the same force-push it is meant to catch.

`--require-signer` (optional; the owner decides whether to make it mandatory) requires `grading_commit` to carry a valid signature from a registered key: an SSH fingerprint `SHA256:...` or an SSH `allowed_signers` file (checked with `/usr/bin/git verify-commit` and `gpg.ssh.allowedSignersFile`, using `/usr/bin/ssh-keygen`), or an ASCII-armored GPG public key file (imported into a temporary `GNUPGHOME` that holds only that key, checked with `verify-commit` and `/usr/bin/gpg`; the signing key's fingerprint must belong to the file). A bare GPG fingerprint is refused, since verifying it needs the key itself. All of this runs in the same sanitized environment as the other git calls.

API (importable by a gate):
```python
import verify_holdout
r = verify_holdout.verify("…/<run>.json")      # or a dict; optional repo_url=, reveal_commit=, results=,
                                                # expect_shas= (dict, path or "k=v,..."), require_signer= (as the CLI)
r["accepted"]   # True only if every check passed and nothing is test-only
r["ok"], r["errors"], r["checks"], r["recomputed"]
r["shas"]       # {"grading_commit", "reveal_commit", "remote_branch", "remote_tip_sha"}: store these
```

What it checks:
1. `git ls-remote` of the canonical repository for `edu-career-pathways/majors-onet-study-plans` and `main`, a fresh blobless fetch of them into a temporary repository, and that `grading_commit` and `remote_tip_sha` are reachable from one of those tips.
2. Reveal order: `REVEALED_KEY.json` is absent at `grading_commit` and in all of its ancestors; it is added exactly once in the history of the allowed tip (never modified, removed or re-added), in a `reveal_commit` that descends from `grading_commit`; and it is unchanged at the tip.
3. The sheet and `GRADING_FINAL.txt` are byte-identical at `grading_commit`, at `reveal_commit` and at every commit on the path between them. The record and results file are unchanged from `reveal_commit` to the tip.
4. Every results file, holdout record and `FINALIZED.txt` for this key commitment, anywhere in the history reachable from the allowed tips, names the same `grading_commit`.
5. With `git show`: the sheet, `GRADING_FINAL.txt`, `items.json` and `KEY_COMMITMENT.txt` at `grading_commit`, and `REVEALED_KEY.json`, the results file and the record at `reveal_commit` (the record must equal the committed record, and the results file must hash to `integrity_hash`).
6. `sheet_sha256`, the key commitment (sha256 of `REVEALED_KEY.json`), the items hash, that key and items agree, and that the sheet names only the declared grader.
7. Optional: `--expect-shas` and `--require-signer`, as above.
8. It recomputes every score, baseline, pass check and the pass decision with its own implementation of the pass rule (a test checks it agrees exactly with `score_holdout.py` on thousands of random keys and sheets), and requires the record and results file to match exactly.

A test-only record (or a verification against a non-canonical remote, which only the test suite can do through the private `_test_remote` argument) can be consistent (`ok`) but is never `accepted`.

**Force-push after the reveal.** None of the checks above can stop someone with push access from rewriting the branch later (for example, re-grading and building a new history that looks honest). Two things guard against that: branch protection on GitHub that blocks force-pushes and deletions on `edu-career-pathways/majors-onet-study-plans` and `main`, and the recorded SHAs (`VERIFIED_SHAS.json`, or a verifier's own saved result) checked with `--expect-shas`. Branch protection needs repository admin rights, so only the owner can turn it on; this pack does not change repository settings.

## Signed grading commit (recommended)

Every agent on the shared box pushes as `ireanjordan24`, so an unsigned grading commit does not show that Irean made it: any agent could commit a sheet and `GRADING_FINAL.txt` in his name. A commit signed on Irean's own computer, with a key that never touches the box, does. Signing is optional in code for now; the owner decides whether `--require-signer` becomes mandatory.

On your own computer (git 2.34 or newer, with OpenSSH):
1. Once: `ssh-keygen -t ed25519 -f ~/.ssh/dreamco_signing` (choose a passphrase).
2. Once, in your clone: `git config gpg.format ssh` and `git config user.signingkey ~/.ssh/dreamco_signing.pub`.
3. Once: register the public key. Send the owner and verifier the line `ireanjordan24 namespaces="git" ` followed by the contents of `~/.ssh/dreamco_signing.pub` (that line is an `allowed_signers` file), or its fingerprint from `ssh-keygen -lf ~/.ssh/dreamco_signing.pub`.
4. After grading and `--declare-final`: `git checkout edu-career-pathways/majors-onet-study-plans`, `git pull`, then `git add study_packs/career_pathways/evidence/holdout_kit/grading_sheet.csv study_packs/career_pathways/evidence/holdout_kit/GRADING_FINAL.txt` and `git commit -S -m "holdout grading final"`.
5. `git push origin edu-career-pathways/majors-onet-study-plans`.
6. Optional check: with `git config gpg.ssh.allowedSignersFile <the allowed_signers file>`, `git log --show-signature -1` shows "Good "git" signature".

Then scoring uses `--require-signer <allowed_signers file or fingerprint>`, and verifiers pass the same value to `verify_holdout.py`. GPG works too (`git commit -S` with a GPG key); register the ASCII-armored public key (`gpg --armor --export <key id>`).

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

This protects against a casual read: listing or opening the private folder reveals nothing about which answers are weakened. After scoring, the key is published as `REVEALED_KEY.json`, so the encryption only matters while grading is open. It does not protect against a deliberate attempt. **The passphrase is on the same shared box as the encrypted key.** Every agent runs under the same account, so any agent could read the passphrase and decrypt the key if it set out to. File permissions do not separate agents, and encryption with an on-box passphrase only raises the effort of a look. What this kit relies on is that the grader is a human (Irean) with no reason to look, and that agents are instructed not to decrypt or reveal the key. A grader who wanted to cheat could; this kit measures whether the rubric discriminates for an honest grader.

**Before any sale-grade use**, move the passphrase off the box (for example to the owner's password manager or another machine no agent can reach), delete it from `/home/box/.ecp-holdout/`, and supply it only for the scoring step, after `GRADING_FINAL.txt` and the sheet are committed and pushed. Then no one on the box can decrypt the key while grading is open. This has not been done for this kit: the passphrase is still at `/home/box/.ecp-holdout/passphrase`. The test suite never reads the real private folder or passphrase; it uses temporary made-up keys only, so it can be run by anyone.

## Limitations

There is one grader, and that grader is also the owner, so the result is not independent of DreamCo. Each record's limitations text is built from the grader actually named on the sheet and in `GRADING_FINAL.txt`. There are few items per asset, and only Computer Science can produce a passing per-asset record; with its few weakened items, a single miss fails it. The candidate answers were written by the builder, not by learners. The result shows whether the rubrics discriminate when a human applies them; it says nothing about learning outcomes.
