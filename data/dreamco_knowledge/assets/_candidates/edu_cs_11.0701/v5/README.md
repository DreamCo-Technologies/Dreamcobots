# edu_cs_11.0701: v5 holdout-kit blindness audit (PR #12441 @ def1d2d)

Audited 2026-10-02 ~20:00–20:45 CT in the read-only worktree `<workspace>/edu-pr12441-v5` (HEAD def1d2d42). Approach: grader-adversary, using only the repo, its git history (all 7 PR commits) and public O*NET text. Nothing under `<workspace>/edu-career-pathways-private/` was opened, listed, read or stat'ed. The real key was never read. Every pass-rule test used synthetic keys. No commits, pushes, comments or messages.

**Not re-scored.** The CS plan markdown is unchanged from v4. plan.json only adds `target_plausibility: null`, and the asset sidecars only re-link the append-only regression records (01–04). The v4 score still stands.

## Verdict: FAIL (not ready to send to Irean), but close

The blindness of the items themselves holds up: lookup, shape, git history and the dry-run oracle reveal nothing about which items are weakened. Two problems remain:

1. **Prior-information leak.** The committed `make_holdout_kit.py` fixes the number of weakened items at exactly half (`n // 2` = 8 of 16). The README says "do not assume any particular number of weak answers", and the public code contradicts it.
2. **Pass-rule hole.** The rule has no false-alarm (specificity) term. A grader who marks one criterion 0 on *every* answer, and does not distinguish full answers from weakened ones, passes kit-level discrimination whenever they pick the relatively weakest criterion. Separately, 12 of the 13 per-asset records would rest on a single item.

## Claims

| Claim | Result |
|---|---|
| 16 new items, 4 for CS, shape-normalized | VERIFIED. 16 items: 4 CS + 12 other authored majors (1 each). Every answer is exactly 5 `- **Label:** text` bullets of exactly 1 sentence each, 102–124 words. |
| No 5-word run shared with published content | VERIFIED (independent re-run, wider corpus than their test). |
| Key outside repo; only a nonce'd sha256 commitment committed | VERIFIED from the repo side (see check 3). Whether a nonce is actually present can only be inferred from code, because the key is off-limits. |
| Dry run shows no scores | VERIFIED (check 4). |
| Pass rule: ≥80% detection + mean gap ≥1.0 | IMPLEMENTED AS STATED, but not sound (check 5). |

## Checks

**1. Verbatim / paraphrase overlap: PASS.**
- Corpus: all 2,088 published plan .md/plan.json files, `data/practice_tasks.json`, `authored/*.json`, every tracked README/.md in the repo (kit excluded), O*NET 31.0 (tasks, occupation descriptions, job-zone reference) and O*NET 30.3 (tasks, descriptions). Also the deleted v1 kit from git history.
- 5-grams: 0 hits for prompts, answers and rubrics against every source.
- 4-grams: published-corpus density is at most 5.3% for prompts and at most 0.8% for answers, with 0 against O*NET.
- 3-grams: at most 15% (prompts) and 7% (answers), all common phrasing.
- TF-IDF cosine of each answer against 101,502 published strings (scenarios, reference outlines, rubrics, O*NET task text, v1 kit): best match per answer is 0.11–0.28, median about 0.15. No answer has a published near-twin.
- Highest within-kit pair cosine is 0.14, so no full/weak pair of the same source appears in the kit.
- Conclusion: lookup cannot tell strong from weak.

**2. Shape / stylistic cues: PASS.** The key is not available, so I checked whether any feature splits the 16 answers into a natural 8/8 or near-8/8 grouping.
- Uniform across all 16 answers: sentence count (5), parentheses, colons, dashes (all 0).
- Narrow bands with no gap: characters (690–796), words, bullet length, words per sentence, commas, Flesch-Kincaid grade (9.6–13.3).
- Features that vary with the field (digits, capitalized tool names, hedge words, %, "e.g."): none gives a clean split. The largest gap that leaves at least 5 items on each side is 25% of the range, at a 10/6 split ("bullets without a digit"). That is consistent with numeric-heavy fields, not with labels.
- Rubric-keyword coverage of the weakest criterion is continuous (largest mid gap 0.095 on a 0.78 range).
- Bullet labels are free-form and do not mirror criterion names in a pattern.
- Residual (not a leak): the weakness is in the content, which is the intended signal.

**3. Key recoverability: PASS, with one leak.**
- `make_holdout_kit.py` takes the seed from `secrets.randbits(128)` and the nonce from `secrets.token_hex(32)` (256-bit). Both are stored only in the private key. The script needs the private `holdout_source.json` and exits without it. There is no fixed seed.
- `KEY_COMMITMENT.txt` is byte-identical to the current script's template, and its items hash matches `items.json` (9be037cf…). Brute-forcing it would require guessing the 256-bit nonce, the 128-bit seed and the private source hash, so it is infeasible. The nonce is not committed.
- Git history: across all 7 PR commits, the only key-like file is the v1 `_key.json` (1cda014). It maps the deleted v1 items, and the v1 items share 0 5-grams with v2 items, so it reveals nothing about v2. No `holdout_source`/`holdout_key` blob exists in any commit. The PR timeline shows no force-pushes, so no lost intermediate commits.
- No ignored or untracked leftovers in the worktree. A name-only search of `<workspace>/edu-career-pathways` found no holdout/key files.
- Q-ids are assigned after a secret shuffle. Filenames carry no per-item hashes. The test fixture's synthetic labels are not the real ones.
- **Leak:** the public code fixes the weakened count at exactly 8 of 16, contradicting the README.
- **Operational caveat (not verified, since the path is off-limits):** the default key path is on this shared box under the same Unix user every agent uses. `chmod 600` does not protect against that user.

**4. Oracle behaviour: PASS.**
- Dry run on a scratch copy, with the private-dir env var pointed at an empty scratch dir and `--key` at a non-existent file. All-2s, all-1s, all-0s and three random sheets each gave exit 0 and byte-identical stdout ("Sheet format OK … No scores were computed"), in about 36–38 ms each.
- Errors depend only on the sheet (blank sheet: exit 1, format error).
- The dry-run code path never opens the key. Without GRADING_FINAL.txt, `--finalize` refuses before reading the key. A forged key is refused ("sha256 differs").
- Scratch outputs were deleted. No `evidence/holdout` dir and no GRADING_FINAL.txt exists in the v3/v4/v5 worktrees or dp-merchant.

**5. Pass-rule soundness: FAIL.** Simulated with `discrimination()` imported from their `score_holdout.py`, over 4,000 synthetic keys matching the public structure (8 of 16 weakened, CS = 4 items, 12 single-item majors).
- **Degenerate graders:** all 2s, all 1s and all 0s pass 0%. Uniform random passes 0.03%. One random criterion = 0 on every item passes 0.35%. Fine.
- **Hole:** a grader who finds the relatively weakest criterion in every answer (95% hit rate on weakened ones) and scores it 0 on *every* item passes kit discrimination **97.6%** of the time. It produces about 6.4 passing asset records per kit, and the CS record passes 66% of the time. The reason: detection only measures hits, and the gap uses the mean of all three full-strength criteria (diluted to 1.33), so false alarms on full items cost nothing at kit level.
- **Proposed fix:** adding "false-alarm rate on full-strength items ≤ 0.2" (any criterion ≤1 and below the mean of the other two) drops that strategy to 0%. The ideal grader still passes 100% and all degenerate graders 0%.
- **Detection threshold:** detection is kit-level. 0.8 of 8 weakened means **at least 7 of 8**.
- **CS:** its weakened count is hypergeometric (k = 0/1/2/3/4 with P = 3.8/24.6/43.1/24.6/3.8%). CS agreement ≥0.8 needs at least 10 of 12 criterion scores in band. 7.7% of draws give CS no within-asset contrast.
- **The other 12 assets get n_items = 1 records:** agreement ≥0.8 there means 3 of 3, so one item decides a "passed" record.
- **Re-finalize loophole:** the sheet is not locked at GRADING_FINAL time. `--finalize` can be re-run with a new `--run-id` after edits, and append-only only blocks reusing an id.
- **Honesty:** `n_items` is the true per-asset count, and `grader` comes from the sheet. But the `limitations` text "single human grader who is also the owner" is hard-coded whoever the grader is, and nothing checks that there is a single grader or that it equals the declared_final grader.

**6. Evidence-record compliance: PASS (with nits).** A synthetic finalize run (synthetic kit and key, real v5 CS asset.json, scratch tree, since deleted) wrote `holdout:edu-cs-11.0701:20261002-01`.
- It resolved under our gate's `resolve_evidence_ids` with repo root = scratch tree: (1 resolved, 0 problems). kind = holdout, path `<evidence_root>/holdout/edu-cs-11.0701/<run>.json`, all 10 required fields plus the 6 result fields present. source_type `human_evaluation` and transformation `original_evaluation` are both allowed by policy. integrity_hash matches the results file.
- Nits:
  - `split` is `blind_holdout_v2_rubric_discrimination`, not `holdout`.
  - There is no `baseline_score`, which was in my original field list but is not required by the resolver.
  - `results_path` is pack-relative while `evidence_root` is repo-relative.
- **Our side:** the resolver counts a conforming record even when `passed` is false. Their build.py links only passing records, but the gate should check `passed is True` itself.

## Re-gate, 27 authored plans (`--repo-root` = v5 worktree)

27/27 come out `approved_for_private_use`, with rights ceiling approved_for_sale. The only failures are `scorecard_threshold` and `owner_approval`. `synthesis_asset_record` is **warn-only** ("only 1 perspective"). CS resolves 4 regression ids under `study_packs/career_pathways/data/dreamco_knowledge/evidence`. Output: `gate_authored_v5.json`.

## Minimal fixes before sending

1. Draw the weakened count secretly, e.g. `rng.randint(6, 10)` from the secret seed, and stratify so CS gets 1–3 weakened. Then redraw the kit, which costs nothing since it is ungraded.
2. Add a kit-level false-alarm limit: at most 20% of full-strength items flagged (or base the gap on each item's minimum criterion). Re-run the degenerate-grader tests with a "flag one criterion on every item" grader.
3. Do not let a per-asset record pass with n_items < 4 or without at least 1 full and 1 weakened item. Mark those records informational / `passed: false`, or add items.
4. Lock the sheet: GRADING_FINAL.txt records `sheet_sha256`, and `--finalize` refuses on mismatch and refuses a second finalize for the same `key_sha256`.
5. Record hygiene:
   - set `split: "holdout"` and move the kit name to another field;
   - add `baseline_score` (e.g. the chance-level agreement);
   - build `limitations` from the actual graders and require a single grader equal to the declared_final grader;
   - make `results_path` consistent with `evidence_root`.
6. Operational: keep the private key off this shared box/user, or encrypt it at rest until finalize.
7. Our gate (dp-merchant): count only records with `passed: true` toward `min_validation_evidence_ids`.

Scripts used: `overlap.py`, `shape.py`, `passrule.py`, `gate_v5.py` (this folder; paths point at the scratch/worktree locations used).

## Follow-up (2026-10-02 ~20:15 CT): gate counts only `passed: true` evidence

Fix 7 above is done in dp-merchant (untracked, not committed).
- `resolve_evidence_records` returns three things: the number of records that count, the problems, and the not-passed notes. `resolve_evidence_ids` keeps its two-value return, and its count is now passed-only.
- A conforming record whose `passed` is not `True` (false, null, "true", 1) is listed as `<id> resolved but passed is not true` and does not count. It never causes a rights failure.
- If the remaining passing records fall short of `min_validation_evidence_ids`, the check fails at sale scope (cap approved_for_private_use).

Tests: 49/49 pass. That is the existing 44 plus 5 new: 4 parametrized "does not count" cases, and a mixed case (1 passed + 1 failed still meets the minimum of 1).

Re-gate of the 27 authored plans: unchanged. All 27 are approved_for_private_use, the only failures are scorecard_threshold and owner_approval, and synthesis is warn-only. All 108 linked regression records have `passed: true`.
