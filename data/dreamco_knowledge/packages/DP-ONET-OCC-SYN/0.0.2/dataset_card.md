# Dataset card: DreamCo Occupation Synthesis Pack (built with O*NET® 31.0 data), version 0.0.2 (populated sample)

Internal SKU id: `DP-ONET-OCC-SYN` (internal identifier only; a buyer-facing id will be decided before any listing).

**Status:** first populated sample, 44 occupations. **Not for sale, not production ready, no price.**
Package `license_gate_status: fail` because the one included asset's gate outcome is `approved_for_private_use`
(plan mapping: anything below `approved_for_sale` rolls up to `fail`). All rights checks pass; the cap comes from sale-scope
checks: no dataset evaluation scorecard, no validation evidence, no owner approval.

## Purpose
DreamCo's own synthesis layer over a small, derived subset of O*NET® 31.0 data: per-occupation capability lenses, data-confidence
bands, practice-task seeds, rubric dimensions and agree / caveat / improve / still-need-test analysis, for training and evaluating
career-guidance and occupational-task bots. Built with O*NET® data; not an O*NET® product.

## Composition
- `sample/occupations.jsonl`: 44 rows (machine layer), schema `schemas/dp_onet_occ_syn.row.schema.json`, fields in `data_dictionary.md`.
- `sample/occupation_cards.md`: the same 44 occupations as readable cards (human layer), with the attribution footer.
- `assets/dp-onet-occ-syn-sample-0.0.2/`: `provenance.json`, `asset.json` (plan 5.2 synthesis asset), `candidate.json`, `license_gate.json`.
- Coverage: 22 SOC major groups x 2 occupations (group 55 has no O*NET® ratings). Job Zone 2 ("1-2"): 19, Zone 3: 8, Zone 4: 7, Zone 5: 10.
- Selection is deterministic (sha256 seed, see `MODIFICATIONS.md`). It is a sample, not a representative weighting of U.S. employment.

## Ownership and rights (field level)
- `license.onet_derived_fields` (code, title, job zone, top-5 knowledge / essential skills / work activities with IM values, task counts):
  O*NET® 31.0 Database content, USDOL/ETA, CC BY 4.0. Recipients keep every CC BY 4.0 right in these values; no DreamCo term or technical
  measure may restrict them (CC BY 4.0 s.2(a)(5)(B)).
- `license.dreamco_fields` (preparation band, lenses, lens lift, dominant and knowledge lens, data confidence, DreamCo synthesis):
  DreamCo-derived. Commercial terms are not set (see `LICENSE`). The DreamCo text embeds O*NET® titles and element names, so the
  O*NET® attribution applies to it too.
- Only the downloadable O*NET® 31.0 Database files are used: no O*NET® Web Services data, no Career Exploration Tools content, no crosswalk
  content, no occupation descriptions or task statement text.

## Version pin
O*NET® 31.0 (August 2026, the current production release per https://www.onetcenter.org/db_releases.html, read 2026-10-05).
`db_31_0_csv.zip` sha256 `55033fc6…87cd`; per-file pins for the six CSV members used are in the asset `provenance.json` and are repeated
per row in `source_refs[].file_sha256`. Essential Skills come from `essential_skills.csv` (2.A.*); Transferable Skills are not used.

## Quality and evaluation
- Dataset QA scorecard (`tools/score_data_package_dataset.py`, `config/data_package_dataset_qa_scorecard.json`): see `quality_report.json`.
  QA is integrity evidence (schema, referential integrity to O*NET-SOC codes, values match source, dedup, ranges, version match,
  per-row provenance, synthesis checks). It is **not** the `config/dataset_evaluation_scorecard.json` score, which has not been run.
- `benchmark_report.json`: not_run. No claim that this sample improves any model.
- The practice seeds and rubrics are template-generated and ungraded.

## Known limitations
See `manifest.json#known_limitations`. In short: single publisher (one perspective: official O*NET® data), 44 occupations,
template text, some ratings as old as 2015-07 (flagged per row), DreamCo lens groupings are DreamCo's judgment and not validated,
U.S. taxonomy only.

## Name and trademark
Display name: "DreamCo Occupation Synthesis Pack (built with O*NET® 31.0 data)". Irean Jordan chose this name (option A in `reports/DATA_PACKAGE_LICENSE_QA_REVIEW.md`
section 1.4) on 2026-10-05; it uses "O*NET" only as an adjective followed by a generic noun, with the ® symbol, after the
DreamCo product noun. The SKU id `DP-ONET-OCC-SYN` is an internal identifier only; a buyer-facing id will be decided before
any listing.

## Attribution
This dataset includes information from the O*NET 31.0 Database by the U.S. Department of Labor, Employment and Training
Administration (USDOL/ETA). Used under the CC BY 4.0 license (https://creativecommons.org/licenses/by/4.0/). O*NET® is a trademark of
USDOL/ETA. DreamCo has modified all or some of this information. USDOL/ETA has not approved, endorsed, or tested these modifications.
The O*NET® Database is sponsored by USDOL/ETA and developed by the National Center for O*NET Development
(source: https://www.onetcenter.org/database.html). Changes: `MODIFICATIONS.md`. Full text: `ATTRIBUTION.md`.
O*NET-SOC 2019 codes are based on the 2018 Standard Occupational Classification (U.S. Bureau of Labor Statistics, public domain).
