# Data Package Week-1 Evidence Packet

**Plan item:** `reports/DATA_PACKAGE_PRODUCT_PLAN.md` section 8, item 8  
**Branch / worktree:** `feat/data-package-gate-skeleton` at `<merchant-repo>` (based on origin/main `5ba09f2ea`). Not committed, not pushed, no PR.  
**Prepared:** 2026-10-02, about 17:10 CT (America/Chicago)  
**Truth boundary:** This is evidence for gate and skeleton tooling only. **Zero packages are for sale.** No `production_ready` flag was changed. There are no listings, prices, Stripe price IDs, or sales channels. No assets were approved for sale.

## 1. For-sale claims: none

| Claim surface | Value |
| --- | --- |
| SKUs with `license_gate_status` pass or reference_only_bundle | **0** |
| Assets with gate outcome `approved_for_sale` | **0** |
| `sales_channel` other than `none` | **0** |
| `stripe_price_id` set | **0** |
| Owner approvals recorded | **0** |
| Scorecard runs (`config/dataset_evaluation_scorecard.json`) | **0** |
| `production_ready` flags flipped | **0** |

## 2. Files added (all untracked in the worktree)

| Path | Purpose |
| --- | --- |
| `tools/license_provenance_gate.py` | Shared gate. Takes an asset dir or candidate JSON and returns `approved_for_sale`, `approved_for_private_use`, `reference_only`, or `blocked`, with 10 per-check results. Exits 1 on blocked. Also provides `package_gate_status()`, which rolls asset outcomes up to the plan 5.2 package status. |
| `tools/build_sellable_data_package.py` | Validates a package dir: plan 5.2 manifest, `contents_digest`, and the release artifacts from `dataset_product_standard`. Recomputes the package gate status from the asset gate files. **Refuses (exit 1)** unless the package is sellable. `--structure-only`, `--write-digest`, `--out` (assembles only on pass). |
| `tools/minimal_json_schema.py` | Small draft 2020-12 subset validator. `jsonschema` is not in any `requirements*.txt`. The schemas were cross-checked with `jsonschema` 4.26 in a throwaway `/tmp` venv, with 0 errors. |
| `config/license_provenance_gate.json` | Gate rules: O*NET and crosswalk CC BY 4.0 attribution elements, outcome ranking, sale requirements, `package_status_mapping`, and synthesis-asset sale requirements. Existing policy configs are referenced, not copied. |
| `schemas/data_package_asset_provenance.schema.json` | `provenance.json`. It extends `evidence_provenance_schema` and adds ownership classes and per-source sha256 pins. |
| `schemas/data_package_synthesis_asset.schema.json` | `asset.json`, the plan 5.2 "Synthesis asset" record. |
| `schemas/data_package_license_gate.schema.json` | `license_gate.json` (gate output). |
| `schemas/data_package.manifest.schema.json` | The plan 5.2 "Sellable package manifest". |
| `tests/test_license_provenance_gate.py` | 22 pytest cases. |
| `data/dreamco_knowledge/packages/DP-ONET-OCC-SYN/0.0.1/` | SKU skeleton: `manifest.json`, `LICENSE`, `dataset_card.md`, `data_dictionary.md`, `provenance_manifest.json`, `license_manifest.json`, `quality_report.json` and `benchmark_report.json` (both `not_run`), and `sample/.gitkeep`. |
| `data/dreamco_knowledge/assets/_candidates/edu_cs_11.0701/` | CS sample: `as_is/`, `corrected/`, `templates/` (provenance.json, asset.json, candidate.json, license_gate.json), and `README.md`. |
| `reports/DATA_PACKAGE_WEEK1_EVIDENCE.md` | This file. |

The restored plan files `reports/DATA_PACKAGE_PRODUCT_PLAN.md` and `reports/data-package-product.json` are also untracked. The only edit to them is one clause in plan section 8's "Status on restore" line. It said item 1 was done, but item 1 also requires a commit-or-gitignore decision for the catalog, and that decision has not been made. The catalog file is untracked, `.gitignore` has no entry for it, and `data-package-product.json` `top_5_code_gaps` rank 3 lists the decision as open. The line now ends with "commit-vs-gitignore decision still open". The plan's sha256 went from 4eb6d067… to 8de3009c….

### Plan 5.2 reconciliation

- **Sellable package manifest:** `sku_id`, `version`, `package_type`, `contents_digest`, `included_asset_ids[]`, `excluded_reference_only_sources[]`, `license_gate_status`, `scorecard_score`, `commercial_tier`, `known_limitations`, and `sales_channel` are required. `stripe_price_id` is optional; the skeleton sets it to null.
- **Allowed `license_gate_status` values:** `pending | pass | fail | reference_only_bundle`.
  - `pending` is a pre-gate value only: no included assets, or an included asset not yet gated.
  - `pass`: every included asset is `approved_for_sale` and no sources are excluded.
  - `reference_only_bundle`: every included asset is `approved_for_sale`, and at least one reference-only source is cited but not shipped.
  - `fail`: any included asset is `approved_for_private_use`, `reference_only`, or `blocked`.
  - The mapping is documented in the schema `$defs` and in `config/license_provenance_gate.json#package_status_mapping`.
- **Synthesis asset:** `asset.json` sits beside `provenance.json` (plan 5.1 layout). Every 5.2 field is a required key. `human_layer`, `machine_layer`, and `dreamco_analysis` may be null, so an incomplete asset is recorded honestly instead of left out.
  - The plan text's `validation` is implemented as `validation_evidence_ids`, with `sandbox`, `benchmark`, `holdout`, and `regression` lists. That is the key name in the plan JSON.
  - `perspectives_used` must use values from `buddy/learning/multi_perspective_policy.json`.
  - The gate checks `asset.json` against `provenance.json` (ids, ownership class, integrity hash, source versions, rights claims). A contradiction caps the outcome at `reference_only`. A missing or incomplete record only blocks sale.
- `buddy/learning/sellable_package_schema.json` (plan 5.3) was **not** created. It would duplicate `schemas/data_package.manifest.schema.json`, which is the schema CI should use.

## 3. Test results

`python3 -m pytest tests/test_license_provenance_gate.py -q`: **22 passed, 0 failed** (Python 3, pytest 9.1.1).

Coverage:
- A good O*NET asset gets `approved_for_private_use` without owner approval.
- Sale needs all of: a scorecard ≥ 75, owner approval from Irean Jordan with scope sale, and a complete `asset.json`.
- Missing ownership_class fails.
- A bogus ownership class fails, and `unknown_do_not_publish` gives `reference_only`.
- redistribution_allowed false gives `reference_only`.
- commercial_use_allowed false caps at private use.
- A hard-fail flag gives `blocked` with exit 1.
- No sources gives `blocked`.
- An unpinned source fails.
- A missing USDOL/ETA non-endorsement notice fails.
- An asset sha256 mismatch fails.
- An `asset.json` that contradicts provenance gives `reference_only`.
- The package status mapping is tested.
- The as-is CS sample's known gaps are tested.
- The templates validate.
- The schema value lists match the policy configs and the plan JSON `storage_schema_summary`.
- The skeleton manifest validates.
- The builder accepts the skeleton's structure but refuses a sellable build. It rejects sale signals without a gate, and catches `contents_digest` drift.

`python3 tools/build_sellable_data_package.py data/dreamco_knowledge/packages/DP-ONET-OCC-SYN/0.0.1` gives **refused (exit 1)** for 7 reasons: status pending, no included assets, no scorecard, quality report not_run, benchmark report not_run, release_level discovered, and an empty sample.

## 4. Gate results on the CS sample (`edu-cs-11.0701`)

Source asset (read-only): `<workspace>/edu-career-pathways/study_plans/11.0701_computer_science.md`, sha256 `f38df6b3…bc27`. It is one of 27 study plans, with 296 major→occupation links across the set.

**Triage scorer** (`tools/score_data_package_candidate.py`): **56.25, `quality_review`**, with no hard failures.

| Dimension | Score |
| --- | --- |
| rights_clarity | 70 |
| training_relevance | 55 |
| data_quality | 45 |
| provenance | 55 |
| freshness | 90 |
| coverage/diversity | 35 |
| format/usability | 60 |
| benchmark_value | 15 |
| commercial_package_potential | 35 |
| maintenance/updateability | 75 |

One-line reasons for each score are in `as_is/candidate.json`.

**Gate as-is** (`as_is/license_gate.json`): **`reference_only`**.
- Failed rights checks:
  - `provenance_schema_conformance`: no `provenance.json`.
  - `ownership_class_valid`: missing on the asset and both sources.
  - `commercial_and_redistribution_rights`: no source declares these rights, and unknown counts as not allowed.
- Failed sale checks: `scorecard_threshold`, `synthesis_asset_record` (no `asset.json`), `owner_approval`.
- Passed: `sources_pinned` and `no_blocked_flags_or_categories`.
- Warnings: the footer lacks the trademark notice and a "DreamCo has modified" statement, and doesn't state the crosswalk's CC BY 4.0 license.

**Gate on the corrected example** (`corrected/`, output also in `templates/license_gate.json`): **`approved_for_private_use`**.
- All rights checks pass.
- The committed outputs (`as_is/`, `corrected/`, `templates/`) were regenerated on 2026-10-03 with `--evaluated-at 2026-10-03T00:00:00-05:00`, from the repo root, with relative paths. The outcomes are unchanged.
- The regeneration ran without `--asset-root` because the source study plan lives only in the Edu-Career-Pathways checkout, which was not read for this run. As a result:
  - `asset_file_integrity` is `warn` (study plan not found under the asset dir; hash not verified).
  - Attribution is checked against the declared `attribution_text` only.
- The original 2026-10-02 run, with `--asset-root` on the Edu checkout, matched the asset file's sha256 and showed 3 attribution warnings for the file's footer.
- It is capped by sale-scope checks only:
  - `scorecard_threshold`: not run.
  - `synthesis_asset_record`: `machine_layer` null, `dreamco_analysis` null, no validation evidence ids.
  - `owner_approval`: none.

## 5. O*NET ingest

- `config/generated/universal-work-ai-catalog.json` is **not on origin/main**.
- `python3 tools/build_universal_work_ai_catalog.py` ran in the worktree: **ok**, about 15 s, 1,016 occupations, 18,796 tasks, 26,683,062 bytes.
  - The content matches the earlier `<workspace>/onet-ingest` copy; only the source URL differs.
  - The source zip `db_30_3_excel.zip` has sha256 `78703906…f6aa`, which matches the earlier provenance record.
- **Pinned version:** O*NET **30.3** (`DEFAULT_URL`, May 2026). The current production release is **31.0** (August 2026, per onetcenter.org/database.html and db_releases.html).
- **31.0 compatibility:** a scratch run in `/tmp` of the unmodified tool against `db_31_0_excel.zip` (sha256 `c63ad00a…1b04`) worked: 1,016 occupations, 18,838 tasks.
- **Recommendation:** pin the O*NET version per package version and record it in every `provenance.json`. Standardize DP-ONET on **31.0**, because it is current and the Edu-Career-Pathways assets already use it. Keep the 30.3 fleet catalog as a labelled snapshot until it is rebuilt.
  - Caveat: 31.0 replaced Skills with Essential Skills and Transferable Skills, so readers of the old Skills file need checking.
- **Done 2026-10-03 (CT):** DP-ONET-OCC-SYN 0.0.1 now pins O*NET 31.0. `provenance_manifest.json` records the URLs, sizes and sha256 for:
  - `db_31_0_excel.zip`: `c63ad00a…1b04`, re-downloaded and identical to the earlier download.
  - `db_31_0_csv.zip`: `55033fc6…87cd`.
  - The crosswalk xlsx: `4802101a…a6e8`.

  The per-file CSV pins in the asset `provenance.json` match the zip contents. The tool default stays 30.3, and DP-ONET passes `--onet-zip-url` (see plan §8).
- **Catalog not committed.** It is 26 MB, and it is not staged. `.gitignore` lists specific `config/generated/*` files only and has no pattern for generated catalogs, so nothing was added. Commit vs gitignore is still an owner decision (plan section 8 item 1).

## 6. Remaining gaps

1. **`buddy/learning/multi_view_synthesizer.py` has not been started** (plan section 8 item 3). No `_mvp_demo` sandbox asset exists.
2. **The O*NET catalog is not committed**, and no commit/gitignore policy has been chosen. The 30.3 vs 31.0 mismatch is still open in the tool.
3. DP-ONET-OCC-SYN 0.0.1 has no assets, samples, scorecard, quality run, or benchmark run, so its status stays `pending`.
4. The CS sample has no machine layer, DreamCo analysis, or validation evidence. Its footer is missing the trademark notice, a "DreamCo has modified" statement, and the crosswalk license statement; fixing these is Edu-Career-Pathways' call, in `build.py`.
5. The gate is not yet wired into `tools/score_data_package_candidate.py` (plan 5.3). It runs as a separate CLI.
6. Package README with blocked categories, the book analogy, and the copyright-stripping hard no (plan section 8 item 6) has not been written.
7. Rights determinations here (CC BY 4.0 allows commercial use, redistribution, and AI training) are the agent's reading of the published licenses. They still need the owner's rights review before any sale.
