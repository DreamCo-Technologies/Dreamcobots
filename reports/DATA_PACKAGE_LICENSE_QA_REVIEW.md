# DreamCo Occupation Synthesis Pack (built with O*NET® 31.0 data): license and QA review, sample build, package #2 scope

Internal SKU id: `DP-ONET-OCC-SYN` (internal identifier only; a buyer-facing id will be decided before any listing).

- **Date:** Mon 2026-10-05, 4:43–5:00 PM CT; display-name update and PR preparation 10:33 PM CT onward (§8).
- **Author:** Grok-Data-Package-Merchant (Grok Bot executor), local review only.
- **Branch:** `feat/dp-onet-license-qa-review`, created off origin/main `f1ece6ffa` in a separate local worktree. That commit includes the PR #13192 merge `0b677b43`.
- **Review phase (4:43–5:00 PM CT):** nothing was committed, pushed or sent.
- **Update (10:33 PM CT):** Irean Jordan approved, via chat, the display name (option A) and opening a PR. This branch is committed and opened as a PR for review. It is not merged, and no one was messaged (§8).

**Truth boundary.** Nothing in this review marks any package `sellable`, `approved_for_sale` or `production_ready`, and no price is set.
- The new 0.0.2 sample is **approved_for_private_use** at the asset gate.
- The package's `license_gate_status` is `fail`.
- The sellable build refuses it.
- All third-party copyright and attribution notices were kept. Edits were additive only.

---

## 0. Summary

| Area | Result |
| --- | --- |
| License | O*NET® 31.0 database files are CC BY 4.0, so commercial redistribution of derived and synthesized data is allowed with conditions. The conditions are: credit "O*NET 31.0 Database" and USDOL/ETA, link the license, state the modification, use the non-endorsement text, use the trademark properly, and add no downstream restrictions. SOC/BLS and NCES material is U.S. Government work and in the public domain (17 U.S.C. §105). O*NET® Web Services data and the Career Exploration Tools carry different terms and are excluded. |
| Gaps | 18 gaps found (G1–G18). 17 fixed, including G8 (the name), which was resolved on 2026-10-05 by Irean's choice of option A. 1 recorded as a note only (G17). |
| Trademark | The old display names led with "O*NET" without ®, which was not compliant. **Resolved 2026-10-05:** Irean chose option A, and the display name is now "DreamCo Occupation Synthesis Pack (built with O*NET® 31.0 data)" everywhere a buyer could see it (§1.4, §8). The SKU id `DP-ONET-OCC-SYN` is kept as an internal id only; a buyer-facing id is decided before listing. |
| QA scorecard | 8 checks with thresholds, implemented in `tools/score_data_package_dataset.py`. The 0.0.2 sample scored **pass, qa_score 98.5/100** against the pinned O*NET® 31.0 zip. |
| Milestone | **populatedDatasetCount ≥ 1 reached on disk.** DP-ONET-OCC-SYN 0.0.2 has 44 occupations across 22 SOC major groups. `server/routes.ts` still says 0; changing it is a follow-up. |
| Gate | Asset gate gives `approved_for_private_use` with rights ceiling `approved_for_sale`. All 7 rights checks pass. The sale-scope checks fail: scorecard, validation evidence and owner approval. |
| Tests | `tests/test_license_provenance_gate.py` + `tests/test_score_data_package_dataset.py`: **128 passed, 4 skipped**. That is 99 passed + 4 skipped (same as baseline) plus 29 new. |
| Package #2 | Recommend **DP-ONET-SKILL-GRAPH** first. Second is the **CIP→SOC education-pathways bridge**. BLS OEWS wages and projections are conditional on getting a copy from another network. |
| Decision date | Sale-readiness decision targeted for **Thu 2026-11-12**. It slips to Nov 19 if Irean's inputs arrive after Nov 6. |

---

## 1. License review

### 1.1 Primary sources read

All sources below were read on **2026-10-05** (CT) unless marked otherwise. Raw copies of the onetcenter.org and CC pages were kept in a local scratch directory outside the repo. They are not committed.

| # | Source | URL | Read |
| --- | --- | --- | --- |
| S1 | O*NET® Database license (31.0) | https://www.onetcenter.org/license_db.html | 2026-10-05 |
| S2 | O*NET® 31.0 Database page (usage license, credit text) | https://www.onetcenter.org/database.html | 2026-10-05 |
| S3 | License agreements index | https://www.onetcenter.org/license_agreements.html | 2026-10-05 |
| S4 | O*NET® Resource Center content license | https://www.onetcenter.org/license.html | 2026-10-05 |
| S5 | Career Exploration Tools licenses | https://www.onetcenter.org/license_tools.html | 2026-10-05 |
| S6 | O*NET® Web Services data license | https://services.onetcenter.org/help/license_data | 2026-10-05 |
| S7 | Web Services / OnLine data sources | https://services.onetcenter.org/help/datasources | 2026-10-05 |
| S8 | O*NET® graphics / logo and acknowledgement rules | https://www.onetcenter.org/graphics.html | 2026-10-05 |
| S9 | O*NET® disclaimer | https://www.onetcenter.org/disclaimer.html | 2026-10-05 |
| S10 | Database releases (31.0 = Aug 2026, current) | https://www.onetcenter.org/db_releases.html | 2026-10-05 |
| S11 | O*NET® 31.0 release notes (appendix: updates) | https://www.onetcenter.org/dictionary/31.0/excel/appendix_updates.html | 2026-10-05 |
| S12 | O*NET® 31.0 data dictionary: Occupation Data, Job Zones, Knowledge, Essential Skills, Task Statements, Abilities, Work Styles, Job Titles, Software Skills | https://www.onetcenter.org/dictionary/31.0/excel/ (one page per file) | 2026-10-05 |
| S13 | O*NET® crosswalks (CC BY 4.0 footer) | https://www.onetcenter.org/crosswalks.html | 2026-10-05 |
| S14 | CC BY 4.0 legal code | https://creativecommons.org/licenses/by/4.0/legalcode.en | 2026-10-05 |
| S15 | 17 U.S.C. §105 | https://www.law.cornell.edu/uscode/text/17/105 | 2026-10-05 |
| S16 | BLS copyright information | https://www.bls.gov/opub/copyright-information.htm | **cited, not fetched** (bls.gov returns 403 from this box; text seen via search index 2026-10-05) |
| S17 | BLS linking and copyright | https://www.bls.gov/bls/linksite.htm | cited, not fetched |
| S18 | BLS SOC home | https://www.bls.gov/soc/ | cited, not fetched |
| S19 | NCES / IES public access statement | https://nces.ed.gov/about/public-access-research | 2026-10-05 |
| S20 | ED publications FAQ | https://www.ed.gov/about/contact-us/faqs/Publications | 2026-10-05 |
| S21 | NCES CIP 2020 resources (CIP–SOC crosswalk) | https://nces.ed.gov/ipeds/cipcode/resources.aspx?y=56 | 2026-10-05 (file: https://nces.ed.gov/ipeds/cipcode/Files/CIP2020_SOC2018_Crosswalk.xlsx, HTTP 200) |

### 1.2 Findings

**F1. O*NET® 31.0 database files are CC BY 4.0 (S1, S2).**
- The license page says O*NET® 31.0 is licensed under CC BY 4.0 "except as noted below".
- The "noted" exceptions only limit the scope to the downloadable files on the Database, Archive and Spanish pages. They add no extra restriction on those files.
- CC BY 4.0 allows commercial use, adaptation and redistribution (S14 s.2(a)(1)).
- **Consequence:** DreamCo may sell derived and synthesized data built from these files, provided the attribution conditions below are met.

**F2. Required attribution (S1, S2, S14 s.3(a)).** You must credit the "O*NET 31.0 Database" (with the version number) and USDOL/ETA, link the license, and indicate changes.
- Verbatim credit text, unmodified form: "This page includes information from the O*NET 31.0 Database by the U.S. Department of Labor, Employment and Training Administration (USDOL/ETA). Used under the CC BY 4.0 license. O*NET® is a trademark of USDOL/ETA."
- Verbatim credit text, modified form. Add: "[Company] has modified all or some of this information. USDOL/ETA has not approved, endorsed, or tested these modifications."
- The O*NET® Database license also recommends a downloadable file that lists all changes. This is the **modification notice**.
- CC BY 4.0 s.3(a)(1)(A)(i)–(v) also requires, where supplied:
  - identification of the creator;
  - the copyright notice;
  - a notice referring to the license;
  - a notice referring to the disclaimer;
  - a URI or hyperlink to the material.
- CC BY 4.0 s.3(a)(1)(B) requires indicating modifications. s.3(a)(1)(C) requires the license text, URI or hyperlink.
- S2 adds the credit line "sponsored by USDOL/ETA, developed by the National Center for O*NET Development".
- S8 says apps using O*NET® data "must acknowledge the National Center for O*NET Development as the source".

**F3. No-endorsement (S1 modified text; S14 s.2(a)(6)).** Never state or imply that USDOL/ETA or the National Center sponsors, endorses or tested DreamCo's product. The modified-form sentence "USDOL/ETA has not approved, endorsed, or tested these modifications" is required.

**F4. Trademark (S1 trademark section; S14 s.2(b)(2)).** CC BY 4.0 does **not** license trademark rights. The O*NET® trademark rules:
- display the ® symbol;
- use "O*NET" only as an adjective followed by a generic product name ("built with O*NET® data", not "includes O*NET");
- never use it in possessive or plural form.

See §1.4 for the naming verdict.

**F5. No downstream restrictions (S14 s.2(a)(5)(B), s.3(a)(4)).** DreamCo's sale terms and technical measures (DRM, click-through) must not restrict recipients' CC BY 4.0 rights in the O*NET®-derived values.
- DreamCo can license its own synthesis layer on its own terms.
- DreamCo cannot stop buyers from reusing the O*NET®-derived numbers under CC BY.
- This limits the commercial moat: value must come from the DreamCo layer and the curation.

**F6. Removal on request (S14 s.3(a)(3)).** If the licensor asks, the attribution must be removed to the extent reasonably practicable. This is operational only and recorded as G17.

**F7. Sui generis database rights (S14 s.4).** These are licensed under the same terms. No extra obligation.

**F8. Files with different terms. Exclude them (S3–S7).**
- The **Career Exploration Tools** (Interest Profiler and similar) are CC BY-ND 4.0 or under the O*NET® Tools Developer License, which forbids derivatives. Not used.
- **O*NET® Web Services** data must be shown without modification under a non-transferable license (S6). Not a source.
- The external data shown in O*NET® OnLine and My Next Move is **not covered** by the O*NET® license (S7). That includes BLS projections, OEWS wages, Career Clusters and CareerOneStop. S7 says "Database Services: No external data sources used."
- **Package #2 rule:** BLS data must come from BLS directly, never through O*NET® Web Services or My Next Move.

**F9. Third-party content inside the database (S11, S12).** The data dictionary pages read show **no separate license terms** for Abilities, Work Styles, Knowledge, Essential Skills, Task Statements, Job Zones or Occupation Data.
- **Software Skills / Technology Skills** use UNSPSC v260801 "provided by the United Nations Development Programme". The database license covers it as published. This is flagged because UNSPSC has its own terms; DP-ONET 0.0.2 does not use it.
- **Job Titles (lay titles)** come from professional associations, incumbents, Occupational Classification Analysis, SOC, government agencies, user input and employer job postings. They are published under the database license; not used in 0.0.2.
- The **30.3 notes** say Basic Interests and **Work Styles** ratings came from a hybrid AI-and-expert method, and hot technologies come from employer job postings. That is a provenance-quality note, not a license difference.
- **Abilities** follow the O*NET® Content Model, which historically adapted Fleishman's taxonomy. No separate terms are published. Low risk; confirm with onet@onetcenter.org before an Abilities-heavy SKU.

**F10. Crosswalk files are CC BY 4.0 (S13).** Footer text: "Crosswalk Files by U.S. Department of Labor, Employment and Training Administration is licensed under a Creative Commons Attribution 4.0 International License."
- The CIP crosswalk is based on NCES data.
- The OOH crosswalk is maintained by BLS.
- The pinned `Education_CIP_to_ONET_SOC.xlsx` is pinned, but 0.0.2 does not use it.

**F11. SOC/BLS and NCES are public domain (S15–S21).**
- §105: works of the U.S. Government are not subject to copyright.
- BLS says everything it publishes is public domain except previously copyrighted photos and illustrations. It asks for a citation, and the BLS emblem is a trademark. This was cited from the search index because bls.gov returns 403 from this machine.
- IES says "Unless stated otherwise, all information on IES website is in the public domain".
- An ED publications FAQ says publications "may be reproduced for non-commercial purposes". That is ambiguous wording. §105 governs NCES-authored data. Flagged for counsel only if NCES data becomes a main SKU input.
- SOC codes and titles are U.S. Government work, so O*NET-SOC codes add no restriction beyond the O*NET® CC BY credit.

**F12. Version (S10, S11).** 31.0 (August 2026) is the current production release. The pin matches.
- 31.0 updated 208 occupations.
- 31.0 replaced Skills with Essential Skills (2.A) and Transferable Skills (2.B).
- The re-downloaded zips match all three pins:
  - `db_31_0_csv.zip`: `55033fc6…87cd`
  - `db_31_0_excel.zip`: `c63ad00a…1b04`
  - crosswalk xlsx: `4802101a…a6e8`

### 1.3 Gaps against the package files, and fixes

Files reviewed: the package `LICENSE`, `dataset_card.md`, `license_manifest.json`, `provenance_manifest.json`, `manifest.json` (0.0.1), and `config/license_provenance_gate.json` with its code.

| Gap | Finding vs. package | Basis | Fix (worktree) |
| --- | --- | --- | --- |
| G1 | No source URI or download link for the O*NET® material | S14 s.3(a)(1)(A)(v) | LICENSE §1 adds https://www.onetcenter.org/database.html and the zip URLs. dataset card links added. |
| G2 | Dataset card had no license link | S1 "link to the license" | Card "Rights notes added 2026-10-05" adds links to the CC BY 4.0 license and license_db. |
| G3 | No list of changes (modification notice file) | S1 recommendation; S14 s.3(a)(1)(B) | New `MODIFICATIONS.md`: 0.0.1 says "none"; 0.0.2 lists every transformation. |
| G4 | No National Center for O*NET Development credit | S2, S8 | Added to LICENSE, ATTRIBUTION.md and provenance `attribution_text`. |
| G5 | No disclaimer notice | S14 s.3(a)(1)(A)(iv), s.5; S9 | LICENSE now references the CC BY 4.0 s.5 disclaimer and the O*NET® disclaimer. |
| G6 | No statement that recipients keep CC BY rights | S14 s.2(a)(5)(B) | LICENSE "Recipients' rights" clause. Rows carry `license.onet_license`. |
| G7 | No-endorsement only implied | S14 s.2(a)(6); S1 | Explicit "not an official O*NET or U.S. Department of Labor product, not sponsored, endorsed or tested" paragraph. |
| G8 | Name and SKU id used the O*NET mark ahead of the product noun, without ® | S1 trademark rules | **Resolved 2026-10-05.** Irean Jordan chose option A. Display name "DreamCo Occupation Synthesis Pack (built with O*NET® 31.0 data)" set in the manifests, dataset cards, LICENSE, ATTRIBUTION, MODIFICATIONS, data dictionaries, occupation cards, asset titles, `reports/data-package-product.json` and the plan. The SKU id is kept as an internal id. See §1.4 and §8. |
| G9 | No exclusion of Web Services data | S6 | LICENSE plus license_manifest `excluded_sources_not_used`. |
| G10 | No exclusion of Career Exploration Tools | S5 | Same as G9. |
| G11 | No third-party component inventory | S12 | license_manifest `third_party_component_inventory` covers UNSPSC, Job Titles and AI-hybrid ratings, with "used: no" in 0.0.2. |
| G12 | Crosswalk section lacked the CC link | S13 | LICENSE crosswalk section gains the CC BY 4.0 URL. Gate rule now requires it. |
| G13 | Exact notice strings and version-specific credit not recorded | S1 | license_manifest `required_notices` holds the verbatim strings, version 31.0. |
| G14 | Gate treated the trademark notice and license link as optional in declared attribution | S1 | Gate config 0.1.1 adds `required_in_declared_attribution` (`license_link`, `trademark_notice`; crosswalk `license_link`). `check_attribution` now fails without them. |
| G15 | No per-row provenance or attribution | Plan §5.2; S14 s.3(a) | 0.0.2 rows carry `source_refs` (file, member sha256, keys, fields) and a `license` split. |
| G16 | SOC/BLS public-domain status and citation absent | S15–S18 | LICENSE §4 and a license_manifest SOC component, citing BLS. |
| G17 | No process for "remove attribution on request" | S14 s.3(a)(3) | Note in license_manifest. An operational owner is needed (Irean). |
| G18 | DreamCo copyright claim not split from O*NET®-derived values | S14 s.2(a)(5)(B) | 0.0.2 rows list `onet_derived_fields` and `dreamco_fields`. The card and LICENSE say DreamCo claims only its own layer. |

**Side effect of G14.** Re-running the gate on the committed Edu CS `as_is` candidate now gives `attribution_present: fail` (was `warn`). Its outcome is unchanged (`reference_only`).
- The committed `as_is`, `corrected` and `templates` `license_gate.json` files are historical 0.1.0 outputs dated 2026-10-03. They were left untouched.
- The Edu CS footer gaps belong to Grok-Edu-Career-Pathways.

### 1.4 Trademark and name verdict (resolved 2026-10-05: option A)

**SKU id `DP-ONET-OCC-SYN`**
- It is acceptable as an internal identifier.
- If it appears to buyers (storefront, archive filenames, URLs), it puts the mark inside a product identifier with no ® and not in adjective form. That is a **moderate risk**.
- Options: `DP-OCC-SYN`, `DP-WORK-OCC-SYN`, `DP-DCO-OCC-SYN`.

**Display names**
- The manifest title "DreamCo O*NET Occupation Synthesis" and the plan name "O*NET Occupation Synthesis Pack" are **not compliant as written**.
- They have no ®, and leading the product name with the mark suggests an O*NET®-branded or endorsed product (F3, F4).

**Options**
- **A (recommended):** "DreamCo Occupation Synthesis Pack (built with O*NET® 31.0 data)".
- B: "DreamCo Career & Occupation Insights, formulated from O*NET® data".
- C (weakest): keep the current name, add ® and a prominent disclaimer.

**Decision (Mon 2026-10-05, relayed in chat at 10:33 PM CT):** Irean Jordan chose **option A**. The display name is exactly "DreamCo Occupation Synthesis Pack (built with O*NET® 31.0 data)".
- It is applied in every buyer-facing place: both package manifests, dataset cards, LICENSE, ATTRIBUTION, MODIFICATIONS and data-dictionary titles, the 0.0.2 occupation cards and asset titles (generator `DISPLAY_NAME`), `reports/data-package-product.json`, the plan and this report.
- In buyer-facing prose, "O*NET" now carries ® and is used as an adjective. These were deliberately left unchanged:
  - the verbatim USDOL/ETA credit sentence ("...information from the O*NET 31.0 Database by...", the credit O*NET prescribes);
  - the organization name "National Center for O*NET Development";
  - the taxonomy name "O*NET-SOC";
  - quoted words in the usage rules;
  - identifiers (file and column names, field values such as `source_version: "O*NET 31.0"`);
  - historical change-log entries.
- **The SKU id `DP-ONET-OCC-SYN` stays as an internal identifier only.** It must not appear as a buyer-facing product id (storefront, archive filenames, URLs) until a buyer-facing id is decided before listing. Candidates: `DP-OCC-SYN`, `DP-WORK-OCC-SYN`, `DP-DCO-OCC-SYN`.
- Optional: email onet@onetcenter.org or ask counsel before launch.

---

## 2. Dataset QA scorecard

The plan's gap was that no dataset-level QA existed.
- `config/dataset_evaluation_scorecard.json` is the commercial-tier scorecard (75/85/92), and it has not been run.
- The new scorecard is **integrity evidence only**. It is not `scorecard_score`, not validation evidence and not a sale approval. Its `truth_boundary` says so.

**Files**
- Config: `config/data_package_dataset_qa_scorecard.json` (v0.1.0, profile `dp_onet_occ_syn`).
- Tool: `tools/score_data_package_dataset.py`. It reuses `tools/minimal_json_schema.py`.
- Row schema: `schemas/dp_onet_occ_syn.row.schema.json`.

**Usage:** `python3 tools/score_data_package_dataset.py <pkg> [--onet-zip db_31_0_csv.zip | --onet-csv-dir DIR] [--out F] [--evaluated-at TS]`
- The reference zip must match the `provenance_manifest.json` pin, or it is rejected.
- Exit codes: 0 = pass or warn, 1 = fail, 2 = error.

| Check | Weight | Hard | Metrics, with pass / warn thresholds (below warn = fail) |
| --- | --- | --- | --- |
| completeness | 0.10 | soft | required_field_fill_rate ≥ 0.99 / ≥ 0.95 |
| schema_validity | 0.15 | hard | rows_valid = 1.0; rows_parse = 1.0 |
| referential_integrity (to O*NET-SOC codes) | 0.15 | hard | codes_resolve, titles_match, elements_resolve = 1.0; values_match_source ≥ 1.0 / ≥ 0.99 |
| deduplication | 0.10 | hard | unique_record_ids, unique_keys = 1.0; unique_synthesis_payloads ≥ 1.0 / ≥ 0.98 |
| value_ranges | 0.10 | hard | values_in_range = 1.0 (importance 1–5, job zone 1–5, lenses 0–1); internal_consistency ≥ 1.0 / ≥ 0.98 (sorted, band matches zone, major group, arg-max lens, ids, version) |
| freshness_version_match | 0.10 | hard | row_version_matches_pin, file_hashes_match_pin = 1.0; pin_is_latest_known_release ≥ 1.0 / ≥ 0 (latest known 31.0, checked 2026-10-05) |
| provenance_coverage (per row) | 0.15 | hard | rows_fully_covered = 1.0 (every O*NET® field has a pinned ref, every DreamCo field has a synthesis ref, license split present); refs_pinned = 1.0 |
| synthesis_perspective | 0.15 | hard | dreamco_layer_coverage ≥ 0.95 / 0.90; multi_evidence_rows ≥ 0.8 / 0.5; no_verbatim_onet_text = 1.0 (no 10-word run shared with that occupation's O*NET® description or task statements); distinct_seed_ratio ≥ 0.9 / 0.75; dreamco_field_share ≥ 0.3 / 0.2 |

**Overall result**
- `fail` if any hard check fails or is `not_run`. Without reference data, referential integrity and verbatim checks are `not_run`, so the result is `fail`.
- Otherwise `pass` if every check passes, else `warn`.
- `qa_score` = Σ weight × check score (0–100).

**Results on version 0.0.2** (`qa_scorecard.json`; first run 2026-10-05 4:56 PM CT, re-run after the rename with identical results, see §8; reference db_31_0_csv.zip, sha256 matched)

| Check | Status | Score | Key metrics |
| --- | --- | --- | --- |
| completeness | pass | 100 | fill 1.0 |
| schema_validity | pass | 100 | 44/44 valid |
| referential_integrity | pass | 100 | codes, titles, elements and values all 1.0 |
| deduplication | pass | 100 | 1.0 / 1.0 / 1.0 |
| value_ranges | pass | 100 | 1.0 / 1.0 |
| freshness_version_match | pass | 100 | 1.0 / 1.0 / 1.0 |
| provenance_coverage | pass | 100 | 1.0 / 1.0 |
| synthesis_perspective | pass | 90 | layer 1.0, multi-evidence 1.0, verbatim-clean 1.0, distinct seeds 1.0, DreamCo field share 0.5 |
| **Overall** | **pass** | **98.5** | |

Without `--onet-zip`, the same package gives **fail, 70.0** (`referential_integrity` and `synthesis_perspective` are not_run). That is the intended behavior.

**Honest caveats**
- `multi_evidence_rows` counts O*NET® rating sources (incumbent, occupational expert, analyst). These are **one publisher**, so `asset.json` lists only `perspectives_used: ["official_documentation"]`.
- Templates generated the practice seeds and rubrics. No person graded them.

---

## 3. Sample build (milestone: populatedDatasetCount ≥ 1)

**Download and verification**
- `db_31_0_csv.zip` (plus the excel zip and crosswalk) was downloaded to a local scratch directory outside the repo. Downloads are not committed.
- sha256 matched the `provenance_manifest.json` pins.
- The generator checks the pin again before parsing.

**Generator:** `tools/build_dp_onet_occ_syn_sample.py` (version `build_dp_onet_occ_syn_sample 0.1.1`; 0.1.0 before the rename. 0.1.1 changes only titles and the wording of card and analysis text.)
- It picks 2 data-level occupations per SOC major group, ranked by sha256 with seed `dp-onet-occ-syn-0.0.2`.
- Result: **44 rows across 22 major groups.**
- Reproducible: a re-run with the same `--generated-at` gave byte-identical files.

**Per-row O*NET®-derived fields**, a small subset with no descriptions and no task text:
- code and title, job zone;
- top-5 knowledge, essential skills and work activities by Importance (ratings flagged Recommend Suppress excluded; 1 excluded in total);
- core and supplemental task counts.

**Per-row DreamCo synthesis**
- preparation band;
- capability-lens scores and lift over the all-occupation mean;
- dominant lens and knowledge lens (a cross-check between two separately rated domains);
- data-confidence band (dates, N, suppressed count, rating sources);
- practice seed, rubric, and agree / caveat / improve / still-need-test analysis.

**Provenance and licensing per row**
- `source_refs` give the file, member sha256, keys and fields.
- `license` splits `onet_derived_fields` from `dreamco_fields`.
- Attribution ships in `ATTRIBUTION.md`, the `occupation_cards.md` footer, LICENSE, the dataset card and provenance `attribution_text`.

**Stats**
- Job zones: 2:19, 3:8, 4:7, 5:10.
- Dominant lens: physical 19, digital 12, people 8, information 5.
- Knowledge lens agrees with the dominant lens in 17/44 rows.
- Confidence: high 26, medium 14, low 4.
- Ratings range from 2015-07 to 2026-08.

**Package `data/dreamco_knowledge/packages/DP-ONET-OCC-SYN/0.0.2/`**
- Status: `release_level: discovered`, `license_gate_status: fail`, `scorecard_score: null`, `commercial_tier: null`, `sales_channel: none`, `stripe_price_id: null`.
- `quality_report.json` status is `partial`; `benchmark_report.json` is `not_run`.
- Asset integrity: `sha256:06e0b0f6…4df1`, after the 2026-10-05 rename regeneration. It was `sha256:5dc7d31d…c2f9` before.
- `build_sellable_data_package.py --write-digest` gives `structurally_valid`.
- A sellable build is **refused** (exit 1) for 6 reasons: gate status, asset outcome, no scorecard, quality partial, benchmark not_run, release level.

0.0.1 stays an empty skeleton because an existing test asserts that. It only gained the license fixes.

### 3.1 Gate outcome

`python3 tools/license_provenance_gate.py <0.0.2 asset> --asset-root <0.0.2> --repo-root .` (gate 0.1.1; first run 2026-10-05 4:55 PM CT, re-run after the rename with the same outcome, see §8):

- **outcome `approved_for_private_use`**, rights_ceiling `approved_for_sale`.
- Pass: provenance_schema_conformance, sources_pinned, ownership_class_valid, commercial_and_redistribution_rights, attribution_present, no_blocked_flags_or_categories, asset_file_integrity.
- Fail:
  - `scorecard_threshold`: no dataset evaluation score.
  - `synthesis_asset_record`: no sandbox, benchmark, holdout or regression evidence ids.
  - `owner_approval`: no explicit record.

These stay failing on purpose until Irean provides approval and the evidence exists.

---

## 4. Tests

```
python3 -m pytest tests/test_license_provenance_gate.py tests/test_score_data_package_dataset.py -q
128 passed, 4 skipped
```

- The gate file alone gives 99 passed, 4 skipped, unchanged from the baseline before any edits.
- The new file has 29 tests:
  - generator pin refusal, stratified selection, suppressed-rating exclusion, and attribution in rows and cards;
  - QA pass on fixtures (zip and CSV dir);
  - not_run without a reference, and an unpinned zip rejected;
  - bad code or value, duplicate, out-of-range, band inconsistency, missing provenance ref, tampered hash, wrong version, verbatim overlap, unparseable line;
  - CLI exit codes and config consistency;
  - 0.0.2 manifest validates, sale refused, gate stays private-use, attribution kept, honest reports, 0.0.1 attribution;
  - gate 0.1.1 fails without the license link or without the trademark notice.
- `tests/test_buddy_platform_expansion.py` (touches data-package purposes): 18 passed.

---

## 5. Package #2 scope

Plan candidates (§3, `reports/data-package-product.json` skus): DP-ONET-SKILL-GRAPH, DP-MULTI-VIEW-LESSON, DP-BENCH-HOLDOUT, DP-BOOTCAMP-GAIN, DP-HF-STUDY and DP-DOMAIN-SYN, plus the Edu CS study-plan line.

The top 3 below build directly on DP-ONET.

**1. DP-ONET-SKILL-GRAPH (Skills & Work-Activities Graph Pack). Recommend: GO as package #2.**
- **Source:**
  - O*NET® 31.0 files from the same pinned zip: `tasks_to_dwas.csv` (24,087 rows), `gwas_to_iwas_to_dwas.csv` (2,087), `related_occupations.csv` (18,460), `transferable_skills.csv` (45,500), essential skills, knowledge, work activities, and the `*_to_work_activities` linkage files.
  - License: **CC BY 4.0** (S1, F1). The same attribution and trademark rules apply.
  - Avoid Technology/Software Skills (UNSPSC, F9) and lay titles in v1.
- **Buyer use case:** capability routing, skills-based matching, curriculum and transfer-path design, and agent tool routing ("which occupations share this DWA cluster").
- **Effort:** low to medium, 1.5–2 weeks. The pipeline, pins, QA tool and gate already exist. Needs a graph schema, DreamCo transfer-task synthesis, and QA profile extensions (edge integrity, orphan nodes).
- **Risks:**
  - Raw O*NET® linkages are free, so value must come from DreamCo normalization, weighting and transfer tasks.
  - The same trademark naming issue as package #1.
  - AI-hybrid Work Styles ratings (F9) should be labeled if used.
- **Recommendation:** start after the DP-ONET full build (week of Oct 19). Gate it for private use by Oct 30.

**2. CIP→SOC education-pathways bridge (a new SKU, or an `LP-*` line with a DP-ONET backbone). Recommend: GO, behind #1.**
- **Source:**
  - NCES CIP 2020 ↔ SOC 2018 crosswalk (S21): `CIP2020_SOC2018_Crosswalk.xlsx`, downloaded to scratch 2026-10-05, sha256 `ba3d59a191b9d977a5c457a66b9348c4f2f7963aafacf72c0b80113b46bf0ab8`. Sheets: CIP-SOC 6,097 data rows, SOC-CIP, plus unmatched CIP 194 and unmatched SOC 180. **Public domain** (§105, IES statement; ED FAQ wording flagged in F11).
  - O*NET® `Education_CIP_to_ONET_SOC.xlsx` (8,505 rows incl. headers), already pinned, **CC BY 4.0** (S13).
  - Credit NCES and USDOL/ETA.
- **Buyer use case:** program-to-career advising, edtech and workforce boards, and DreamCo's Edu study plans.
- **Effort:** medium, 2–3 weeks. Needs SOC 2018 ↔ O*NET-SOC 2019 code mapping, conflict analysis between the two crosswalks (a real multi-perspective synthesis: two publishers), and QA profile reuse.
- **Edu CS study-plan tier:** include it **only once its provenance is clean**. Today that tier is not ready:
  - the corrected example is private use only;
  - `machine_layer` and `dreamco_analysis` are null;
  - holdout evidence needs remote verification;
  - `required_signer_fingerprints` is unset.

  It also needs Irean's holdout grading and signing-key fingerprint. Grok-Edu-Career-Pathways owns it.
- **Risks:**
  - The two crosswalks disagree, so a matching methodology is needed.
  - The ED reproduction FAQ ambiguity.
  - The Edu CS dependency must not leak into the public-domain tier.
- **Recommendation:** scope it in the week of Oct 26. Go or no-go with Irean on Oct 30.

**3. BLS OEWS wages + Employment Projections enrichment. Recommend: CONDITIONAL. Do not start until the data access is solved.**
- **Source:** BLS OEWS and Employment Projections tables. **Public domain** (S16; cite BLS; do not use the BLS emblem). Not verified live: bls.gov returns 403 from this box, and per instructions it was not scraped.
- **Must not** be taken from O*NET® OnLine, My Next Move or Web Services (F8).
- **Buyer use case:** wage and outlook-aware career and occupation cards. This is the most commercially attractive add-on.
- **Effort:** medium, 2 weeks once the files are obtained. Needs SOC 2018 aggregation mapping to O*NET-SOC and a release-year freshness check.
- **Risks:**
  - Access, from this machine.
  - OEWS estimates are for broader SOC detail, so mapping must be documented.
  - Freshness (annual May reference period).
- **Recommendation:** Irean or another network downloads the official files with sha256 pins. Then add BLS as a second perspective to DP-ONET 0.1.x rather than as a separate SKU.

Not recommended now:
- DP-MULTI-VIEW-LESSON: needs the multi-view synthesizer (plan §8 item 3, not started).
- DP-BENCH-HOLDOUT: depends on the holdout signing infrastructure.
- DP-HF-STUDY and DP-BOOTCAMP-GAIN: separate tracks.

---

## 6. Timeline to sale-readiness decision (all CT)

| Dates | Work | Exit criteria |
| --- | --- | --- |
| Mon Oct 5 – Fri Oct 9 | This review. Irean reads it and decides on the name, commit/PR and catalog commit-vs-gitignore. | Review accepted; commit/PR approval (Irean) |
| Mon Oct 12 – Fri Oct 16 | Full build of all 909 data-level occupations (of 1,016 O*NET-SOC codes) with the same generator; QA scorecard pass; human spot-check of 30 rows; `multi_view_synthesizer.py` stub (plan §8 item 3). | QA pass on the full set; spot-check log |
| Mon Oct 19 – Fri Oct 23 | Validation evidence: grade practice seeds on a holdout split; benchmark run; first `config/dataset_evaluation_scorecard.json` run (target ≥ 75); start package #2 (SKILL-GRAPH). | Evidence ids resolve; scorecard score recorded |
| Mon Oct 26 – Fri Oct 30 | Privacy and contamination test families; refresh/reproducibility rerun; package #2 private-use gate; CIP bridge scoping. **Fri Oct 30:** package #2 go/no-go. | quality_report families all run |
| Mon Nov 2 – Fri Nov 6 | Release candidate DP-ONET 0.1.0: renamed per decision, attribution audit, `server/routes.ts` count proposal. **Fri Nov 6: deadline for Irean's pricing input and approval record.** | RC structurally valid; all gate checks pass except owner approval |
| Mon Nov 9 – Fri Nov 13 | **Thu Nov 12: sale-readiness decision.** Gate re-run with Irean's `owner_approval` record (if given). Sellable build attempted only then. | Decision recorded; it slips to **Thu Nov 19** if inputs arrive after Nov 6 |

**Blocked on Irean**
1. An explicit sale approval record, `owner_approval` with scope `sale`. Without it the gate is capped at `approved_for_private_use`.
2. Pricing and tier (none set here).
3. ~~The name and trademark decision (§1.4).~~ Done 2026-10-05: option A. Still open: the buyer-facing SKU id, decided before listing.
4. ~~Approval to commit this branch and open a PR.~~ Given 2026-10-05; PR opened (§8). Merge is still Irean's call.
5. Commit vs gitignore for `config/generated/universal-work-ai-catalog.json` (still open from the plan).
6. For the separate Edu CS SKU: his holdout grading and his signing-key fingerprint for `required_signer_fingerprints`.
7. Optional: O*NET® developer registration, counsel review of the ED FAQ and trademark question, and the owner for CC BY s.3(a)(3) removal requests.
8. A BLS data download from a network that can reach bls.gov (package #2 option 3).

---

## 7. Changed files (review phase; see §8 for the update)

**Modified**
- `config/license_provenance_gate.json` (0.1.0 → 0.1.1: `required_in_declared_attribution`)
- `tools/license_provenance_gate.py` (GATE_VERSION 0.1.1; declared-attribution check)
- `data/dreamco_knowledge/packages/DP-ONET-OCC-SYN/0.0.1/LICENSE`
- `data/dreamco_knowledge/packages/DP-ONET-OCC-SYN/0.0.1/dataset_card.md`
- `data/dreamco_knowledge/packages/DP-ONET-OCC-SYN/0.0.1/license_manifest.json`
- `data/dreamco_knowledge/packages/DP-ONET-OCC-SYN/0.0.1/manifest.json` (change_log and digest)
- `data/dreamco_knowledge/packages/DP-ONET-OCC-SYN/0.0.1/provenance_manifest.json`
- `reports/data-package-product.json` (SKU status note, `populated_dataset_count_on_disk: 1`, gap-4 status, related report)

**New**
- `data/dreamco_knowledge/packages/DP-ONET-OCC-SYN/0.0.1/ATTRIBUTION.md`, `MODIFICATIONS.md`
- `data/dreamco_knowledge/packages/DP-ONET-OCC-SYN/0.0.2/`:
  - LICENSE, ATTRIBUTION.md, MODIFICATIONS.md, dataset_card.md, data_dictionary.md
  - manifest.json, provenance_manifest.json, license_manifest.json
  - quality_report.json, qa_scorecard.json, benchmark_report.json
  - `sample/occupations.jsonl`, `sample/occupation_cards.md`
  - `assets/dp-onet-occ-syn-sample-0.0.2/{provenance,asset,candidate,license_gate}.json`
- `config/data_package_dataset_qa_scorecard.json`
- `schemas/dp_onet_occ_syn.row.schema.json`
- `tools/score_data_package_dataset.py`
- `tools/build_dp_onet_occ_syn_sample.py`
- `tests/test_score_data_package_dataset.py`
- `reports/DATA_PACKAGE_LICENSE_QA_REVIEW.md` (this file)

**Not changed**
- `server/routes.ts` (`populatedDatasetCount: 0`). Updating it is a follow-up for owner review.
- The Edu CS candidate gate outputs (historical 0.1.0).
- Other local checkouts of the repo.

---

## 8. Update, Mon 2026-10-05 10:33 PM CT: display name and PR

**Owner decisions**, relayed in chat on 2026-10-05:
- Irean Jordan approved opening a PR for this branch.
- He chose option A as the display name: **"DreamCo Occupation Synthesis Pack (built with O*NET® 31.0 data)"**.

**What changed**

1. **Display name** is set in:
   - both package manifests (`title`; the version qualifier moved to `summary`);
   - the dataset cards, LICENSE, ATTRIBUTION.md, MODIFICATIONS.md and data dictionary titles for 0.0.1 and 0.0.2;
   - the 0.0.2 occupation-card heading and asset titles (`DISPLAY_NAME` in `tools/build_dp_onet_occ_syn_sample.py`);
   - the `reports/data-package-product.json` SKU `name`, plus `name_decision` and `sku_id_scope`;
   - the plan's SKU table and a dated note in plan §3;
   - this report.
2. **O*NET® in buyer-facing prose** now carries ® and is used as an adjective. That includes the DreamCo-authored sentences that follow the credit, the card lines ("O*NET®-derived"), the per-row analysis text, the license strings and the data-dictionary origin column. Possessive and noun uses were reworded, e.g. "O*NET's license" became "The O*NET® Database license". The exemptions are listed in §1.4.
3. **The SKU id `DP-ONET-OCC-SYN` is unchanged and internal only.** Every renamed title is followed by a line saying so. A buyer-facing id is decided before any listing.
4. **G8 is resolved** (§1.3, §1.4).
5. **Sample regenerated** with generator 0.1.1 on the same pinned `db_31_0_csv.zip` (sha256 verified), generated_at 2026-10-05 10:35 PM CT.
   - Only titles and wording changed; all values match the source (referential integrity 1.0).
   - Re-running with the same `--generated-at` gave byte-identical `occupations.jsonl`, `occupation_cards.md`, `provenance.json`, `asset.json` and `candidate.json` (**deterministic**).
   - New asset integrity: `sha256:06e0b0f6505f884babd41080e8816568ef73be5fe35028806d0a8feb06804df1`.
   - New `occupations.jsonl` sha256: `fb9d09e4…bf00`.
   - `provenance_manifest.json` asset pins, `license_manifest.json` gate results and `quality_report.json` were refreshed. Both `contents_digest` values were rewritten with `--write-digest`.
6. **Outcomes are unchanged** (re-run 10:35 PM CT):
   - Dataset QA scorecard: **pass, 98.5**, no failed or warned checks.
   - Asset gate 0.1.1: **approved_for_private_use**, rights ceiling approved_for_sale. Failed checks are still `scorecard_threshold`, `synthesis_asset_record` and `owner_approval`.
   - Package `license_gate_status`: `fail`. `scorecard_score`: null. `stripe_price_id`: null. `sales_channel`: none. `release_level`: discovered.
   - Sellable build **refused** (6 reasons). Both versions are `structurally_valid`.
   - **Not for sale. No price.**
7. **Tests:** `tests/test_license_provenance_gate.py` + `tests/test_score_data_package_dataset.py` give **128 passed, 4 skipped**.
8. **Base:** `git fetch origin` showed origin/main still at `f1ece6ffa`, so no rebase was needed.

**Staged-set checks before commit** (each was checked):
- no local machine paths;
- no file over 1 MB;
- no generated O*NET® catalog (`config/generated/universal-work-ai-catalog.json`);
- no O*NET® or NCES downloads, zips, xlsx files or raw page copies;
- nothing from the Edu-Career-Pathways trees;
- no recheck or attack scripts;
- no holdout passphrase or key-location details.

**Still pending (Irean)**
- Explicit sale approval and pricing, by **Fri 2026-11-06**.
- The buyer-facing SKU id.
- PR review and merge.
- For the Edu CS SKU: his holdout grading and signing-key fingerprint.
- Sale-readiness decision: **Thu 2026-11-12**.
