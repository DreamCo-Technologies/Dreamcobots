# v4 reviewer copy: edu-cs-11.0701 at PR #12441 head 1cda014 (Edu-Career-Pathways)

Reviewed 2026-10-02, about 19:07 to 19:50 CT.

- **Review setup:** PR head `1cda0140258492654803d03bd5e83810532a8cc7` was fetched to branch `pr-12441-v4` and checked out in a separate worktree, `<workspace>/edu-pr12441-v4`, which was kept read-only (`git status` is clean).
- **Where reruns happened:** reruns (build, tests, `score_holdout.py`) used scratch copies under `<workspace>/edu-v3-scratch/`. The fixture grading output from the `score_holdout.py` run was deleted afterwards.
- **Paths:** pack paths are relative to `study_packs/career_pathways/`. Merchant paths are relative to `<merchant-repo>`.
- **Scope of merchant edits:** the merchant-side changes below are untracked edits in `<merchant-repo>`. Nothing was committed or pushed.

## Result

| | v3 (687b3c1) | v4 (1cda014) |
|---|---|---|
| Triage, authored CS (`tools/score_data_package_candidate.py`) | 72.4, approved_for_private_use | **73.9, approved_for_private_use** (under 75) |
| Gate, authored CS (new gate, `--repo-root` = PR tree) | approved_for_private_use | **approved_for_private_use**, rights ceiling approved_for_sale. All 7 rights checks pass. Failed: `scorecard_threshold`, `owner_approval`. `synthesis_asset_record` = **warn** (1 perspective), and `regression:edu-cs-11.0701:20261002-03` **resolves**. |
| Gate, 27 authored plans | — | 27/27 same as CS. Each one's regression id resolves. |
| Gate, 1,017 generated plans | approved_for_private_use | 1,017/1,017 approved_for_private_use, rights ceiling approved_for_sale. Failed: `scorecard_threshold`, `synthesis_asset_record` (no evidence ids), `owner_approval`. Not re-scored (59.25 in v3). |
| Committed `license_gate.json` (their build, old gate) | — | All 1,044 fail `synthesis_asset_record` with "additional property 'evidence_root' not allowed". The new schema accepts the field. |

### Dimension changes, v3 → v4

Full reasons are in `candidate.json`.

| Dimension | v3 → v4 | Reason |
|---|---|---|
| rights_clarity | 88 → 91 | `plan.json` license block present in all 1,044 plans, with all notices. Per-item license objects added. Remaining gaps: the file-level `ownership_class` "mixed_per_item" is not a policy class, and DreamCo commercial terms are "not set". |
| data_quality | 66 → 69 | Entry-weighted means reproduce exactly (19 nonzero weights). Skipped elements are now stated. No human review yet. |
| provenance | 90 → 92 | Full `created_at` timestamps. Evidence resolves. Gate digests match. Remaining gaps: the v3 `-01`/`-02` records were deleted, and the digests will go stale when gate files are regenerated. |
| format/usability | 75 → 80 | The data dictionary covers every key. |
| Other six dimensions | unchanged | `training_relevance` 70, `freshness` 90, `coverage/diversity` 35, `benchmark_value` 40 (holdout kit is ungraded), `commercial_package_potential` 55, `maintenance/updateability` 88. |

## 1. `evidence_root` as used in v4

- **Value:** `study_packs/career_pathways/data/dreamco_knowledge/evidence` in all 1,044 `asset.json` files (27 authored and 1,017 generated). It is also written into each regression record and into `score_holdout.py` records.
- **Semantics:** a repo-relative directory, not relative to the asset dir. IDs resolve to `<repo>/<evidence_root>/<kind>/<asset_id>/<run>.json`. This matches `README.md`, `docs/DATA_DICTIONARY.md` and `tests/test_build.py`.
- **Record paths:** `results_path` inside records stays pack-relative (`data/dreamco_knowledge/evidence/...`). This is consistent, because the pack root is `<repo>/study_packs/career_pathways`.

## 2–3. Merchant changes (untracked; diff against `<workspace>/edu-v3-scratch/*.before.*`)

**`schemas/data_package_synthesis_asset.schema.json`**
- Adds optional `evidence_root`:
  - Type: string, minLength 1, default `data/dreamco_knowledge/evidence`.
  - Pattern: `^(?!/)(?!(?:.*/)?\.\.(?:/|$))[^\\]+$`. It rejects a leading `/`, any `..` segment and backslashes.
  - The description states the default and its meaning.
- Adds a description to `validation_evidence_ids` covering the ID format and resolution rules.
- `tools/minimal_json_schema.py` supports `pattern`. I cross-checked with real `jsonschema` (Draft 2020-12): the schema is valid, the v4 CS `asset.json` validates, and bad roots are rejected.

**`tools/license_provenance_gate.py`**
- The gate also enforces the `evidence_root` rule itself, through `evidence_root_error`.
- New `resolve_evidence_ids`. For each ID:
  - It must fullmatch `^(sandbox|benchmark|holdout|regression):<asset_id>:\d{8}-\d{2}$`, with the kind equal to the list key.
  - The path `<repo_root>/<evidence_root>/<kind>/<asset_id>/<run>.json` must stay inside the repo root after `resolve()`, so symlink escapes are caught.
  - The file must exist and parse as a JSON object.
  - `evidence_id` must equal the ID.
  - The record must have every `required_fields` entry from `config/evidence_provenance_schema.json`, plus `split`, `n_items`, `metric`, `score`, `threshold` and `passed`.
- In `check_synthesis_asset`:
  - Any malformed or unresolved ID is a sale-scope fail, capped at approved_for_private_use. It is never a rights fail.
  - Only resolved IDs count toward `min_validation_evidence_ids`.
  - Pass and warn results report "N validation evidence id(s) resolved under <root>".
- New `--repo-root` CLI option and `evaluate(..., repo_root=)` parameter. The default is `DEFAULT_REPO_ROOT = ROOT`, the merchant repo. `inputs.repo_root` is recorded in the output.
- **`schemas/data_package_license_gate.schema.json`:** `inputs.repo_root` added as an optional string.
- **`reports/DATA_PACKAGE_PRODUCT_PLAN.md` §5.2:** the evidence convention note now describes the ID format, `evidence_root`, record fields and resolution.

## 4. Tests

`tests/test_license_provenance_gate.py`: **44 passed** (22 old + 22 new).

- **One old fixture changed:** `complete_layers` used `holdout-run-001`, which is now malformed. It now uses `holdout:edu-cs-11.0701:20261002-01`. An autouse fixture gives each test its own repo root, and `make_asset` writes a conforming record for well-formed IDs. No old assertion changed.
- **New tests:**
  - `evidence_root` accepted, and IDs resolve under it.
  - Default root, plus the `--repo-root` CLI option, including a run against an empty root.
  - Bad `evidence_root` rejected by both schema and gate, for `../evidence`, `data/../../evidence`, `..`, `/abs/evidence`, a backslash, and the empty string.
  - Missing file fails sale.
  - Kind/key mismatch fails.
  - Malformed IDs fail: wrong format, wrong asset_id, bad date, a 1-digit run, an unknown kind, and a trailing newline.
  - One bad ID fails the check even when another ID resolves.
  - A record with the wrong `evidence_id`, or missing `passed` or `integrity_hash`, fails.
  - A non-JSON file fails.
  - A symlink escaping the repo root fails.

PR suite (`tests/test_build.py`) in a scratch copy with sha256-verified raw files: **2112 passed** (venv-ecp, with jsonschema).

## 5. v4 fix verification

**1. Attribution and license labels: PASS (one nit).**
- All 1,044 `plan.json` files have a `license` block with the CC BY 4.0 URL, the ® trademark notice, "DreamCo has modified…", the no-endorsement notice and the Crosswalk notice.
- `practice_tasks.json` has a file-level `license` object (URL, attribution, required_notices, `dreamco_commercial_terms` "not set") and a per-item `license` object:
  - Generated items (6,102): content_class "mixed: quoted O*NET … plus DreamCo template", `open_license_with_conditions`, `contains_third_party_text` true, plus modification and trademark notices.
  - Authored items (162): `synthetic_generated_by_dreamco`, with the O*NET reference fields listed under CC BY.
- Labels and authorship are now split per tier.
- Nit: the file-level `ownership_class` "mixed_per_item" is not a value in `config/buddy-training-data-provenance-policy.json`. Use `open_license_with_conditions` (the most restrictive class present) and keep `ownership_classes` as the per-tier map.

**2. Weighted knowledge averages and the skipped-element note: PASS.**
- My recomputation from O*NET 31.0 `knowledge.csv`, using their rule (targets weight 2; JZ4/5 or target-zone occupations weight 1; Manager, Chief, Postsecondary, All Other, Supervisor, Director and Treasurers titles, plus non-target other-zone occupations, weight 0), gives 19 nonzero weights and matches all 8 CS values exactly.
- The unweighted list is kept, and labeled, for comparison.
- The CS outline lists the 3 top elements it does not cover, with a reason for each.

**3. Data dictionary and full timestamps: PASS.**
- `docs/DATA_DICTIONARY.md` and `docs/data_dictionary.json` document every key of `plan.json` (both tiers), `practice_tasks.json`, `asset.json`, the regression record and the holdout kit.
- `created_at` is ISO 8601 with offset in all 1,044 `plan.json` and `asset.json` files and in `practice_tasks.json`.
- Provenance source `retrieved_at` values are still dates; this is documented as "download time not recorded".

**4. Evidence path: PASS.**
- All 27 authored `regression:<asset>:20261002-03` IDs resolve with the new resolver, using `--repo-root` set to the PR tree.
- All 27 records: `integrity_hash` matches the sha256 of the results file, and `source_reference` matches the asset `integrity_hash`.

**5. Regenerated regression gate hashes: PASS (two caveats).**
- `regression.py` now hashes each gate file as canonical JSON without `evaluated_at`. All 27 `-03` digests match the committed gate files, and the `md`, `majors_selected` and `practice_tasks` hashes all match.
- A rebuild in scratch is byte-identical to the commit, apart from `license_gate.json` files.
- Caveat (a): the committed gate files were produced by the old gate. Regenerating them with the new gate (warn instead of fail, plus `inputs.repo_root`) changes their content, so the `-03` digests will go stale. They should rerun regression, as `-04`, after regenerating the gates.
- Caveat (b): the baseline is still `8cc1ce1` (v2), not `687b3c1` (v3), so the v3→v4 changes were not regression-tested against the previous release.

**Generated-tier plausibility flags: present.**
- 887/1,017 plans carry `quality_flags`; for example, 14.4802 has 3 high-severity `low_title_overlap` flags.
- Supervisory tasks are now skipped (0 supervisory practice items remain; for example, 14.4802-P1 now cites a different task).
- The flags are informational only; the targets are unchanged. The 87% flag rate shows the lexical heuristic is noisy, which their own method note admits.

## Holdout kit check

`evidence/holdout_kit/`: 12 items, 6 weakened. I read `_key.json` only for its metadata and per-item field names, plus programmatic comparisons whose results are reported in aggregate below. No answers are reproduced here.

**Not trivially leaked into grader-facing files: PASS.**
- `README.md`, `items.md`, `items.json` and `grading_sheet.csv` contain no `candidate_type`, practice_id, expected or accepted scores, or "weakened" labels.
- The items carry only `item_id`, `prompt`, `candidate_answer` and `rubric`.
- No other docs reference kit item types.

**"Sealed" is by instruction only. Anyone with repo access can reconstruct the key:**
- `_key.json` is committed in plain text next to the items.
- `make_holdout_kit.py` (with seed 20261002) regenerates it.
- All 12 prompts appear verbatim in `data/practice_tasks.json` and the study plans. The 6 non-weakened answers are token-identical to the published reference outlines, so comparing an item against the published plan unblinds it. The kit README tells the grader not to open those files, but nothing technical prevents it.
- `score_holdout.py` (even as a dry run) prints per-asset scores for any filled sheet. That makes it usable as an oracle for which items are weakened. It should not be run, or its output seen, by the grader before grading.
- A surface-form cue in the candidate answers also distinguishes some weakened answers from reference ones without the key. Specifics are withheld here so the grader stays blind. The builder should normalize answer shape across all 12 items before grading starts.

**Scoring design:**
- Records are per asset: 10 assets with 1–2 items each, and CS has 1 item. One criterion can therefore flip an asset's `passed`.
- A non-discriminating grader who gives every criterion a 2 still produces passing records for some assets. The kit summary would show 0/6 weaknesses detected, but that summary is not part of any asset's pass rule.
- They should require kit-level discrimination before any per-asset record can pass, for example `weakened_detected` ≥ 5/6 and kit criterion agreement ≥ 0.8. The kit should also be relabeled as a rubric-discrimination check, because the answers are reference or weakened outlines, not learner responses.

**Would `score_holdout.py` output pass the new resolver? YES.**
- In a scratch copy I filled the sheet with fixture grades ("TEST-FIXTURE not real grades"; values unrelated to the key) and ran `--write`. That wrote 10 holdout records.
- All 10 resolved under the new gate, using `--repo-root` set to the scratch repo, with `source_type` `human_evaluation`, a correct `integrity_hash` and the asset's `source_reference`.
- The fixture outputs were deleted; no holdout evidence exists.

## Still needed from them

1. **build.py:** call the gate with `--repo-root <repo root>` (`ROOT.parents[1]`). Without it, their own regeneration with the merchant gate fails `synthesis_asset_record` ("does not resolve"); I reproduced this in a scratch rebuild.
2. **Tests:** drop the `asset.pop("evidence_root")` workaround in `tests/test_build.py` now that the schema accepts the field.
3. **Gates, then regression:** regenerate the gate files with the new gate, then rerun regression as `-04` so the gate digests match. Consider making the baseline v3 (`687b3c1`) instead of `8cc1ce1`, and keeping old evidence files rather than deleting them.
4. **ownership_class:** in `practice_tasks.json`, replace "mixed_per_item" with a policy class.
5. **Holdout kit fixes before Irean grades:** normalize answer shape across items, and add a kit-level discrimination requirement to `passed`. Also either move `_key.json` and the weakening table out of the repo the grader uses, or commit only its sha256 (the kit already records `key_sha256` at scoring time). Finally, tell the grader not to run `score_holdout.py`.
6. **Unchanged from v3** (needs the owner, a model key, or another source): Irean's actual holdout grading, a benchmark run, a second perspective, DreamCo commercial terms, and an `owner_approval` record. Sale also needs the dataset scorecard (`config/dataset_evaluation_scorecard.json`), which has never been run.

## Files

- `candidate.json`, `triage_score.json`: authored CS asset, scorer output 73.9.
- `license_gate.json`: run from `study_packs/career_pathways/` with `--asset-root . --repo-root ../..`, so all paths are relative.
- `verification/gate_all_1044_summary.json`: patterns across all 1,044 plans.
- `verification/license_gate_generated_sample_14.4802.json`: one generated-tier plan.
- `verification/license_gate_cs_without_repo_root.json`: shows the failure mode without `--repo-root`.
- `verification/leakage_report_v4.json`: 0 non-title O*NET 5-gram hits in the 27 authored plans.
- `verification/scripts/`: the scripts behind these checks.
