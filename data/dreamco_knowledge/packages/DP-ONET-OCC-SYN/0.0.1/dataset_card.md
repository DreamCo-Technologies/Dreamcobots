# Dataset card: DreamCo Occupation Synthesis Pack (built with O*NET® 31.0 data), version 0.0.1 (skeleton)

Internal SKU id: `DP-ONET-OCC-SYN` (internal identifier only; a buyer-facing id will be decided before any listing).

**Status:** skeleton. No data assets, not evaluated, not for sale. `license_gate_status: pending` (pre-gate; plan enum pass | fail | reference_only_bundle).

## Purpose (intended)
A DreamCo-authored synthesis layer over O*NET® occupational data: major-to-occupation study plans,
knowledge/skill groupings, and evaluation prompts for career-guidance bots.

## Composition
- Assets: none yet (`manifest.json#included_asset_ids` is empty; `excluded_reference_only_sources` is empty).
- Planned inputs: O*NET® 31.0 Database (USDOL/ETA, CC BY 4.0) and the CIP 2020 to O*NET-SOC 2019
  crosswalk (USDOL/ETA, CC BY 4.0). These are proposed pins; see "Version pin" below.

## Ownership and rights
- O*NET® and crosswalk content: third-party, `ownership_class: open_license_with_conditions`.
  Commercial use and redistribution are allowed with attribution under CC BY 4.0.
- DreamCo synthesis: `synthetic_generated_by_dreamco` / `dreamco_owned` only for material DreamCo writes.
- Every asset must carry `provenance.json` and pass `tools/license_provenance_gate.py`.

## Version pin
This package version pins O*NET® 31.0. The download URLs and sha256 for `db_31_0_excel.zip`, `db_31_0_csv.zip` and the
CIP to O*NET-SOC crosswalk are in `provenance_manifest.json`, and each asset's `provenance.json` pins its per-file inputs.
The fleet catalog tool (`tools/build_universal_work_ai_catalog.py`) still defaults to 30.3 for its other users.
DP-ONET builds override that default with `--onet-zip-url https://www.onetcenter.org/dl_files/database/db_31_0_excel.zip`.
The tool reads only Occupation Data and Task Statements, so 31.0 works with it unchanged.

O*NET® 31.0 replaces the single Skills file with two files:
- Essential Skills (`essential_skills.csv` / `Essential Skills.xlsx`, elements 2.A.*)
- Transferable Skills (`transferable_skills.csv` / `Transferable Skills.xlsx`, elements 2.B.*)

Any skill-based asset must name which of the two it uses.

## Quality and evaluation
- `quality_report.json`: not_run
- `benchmark_report.json`: not_run
- Dataset scorecard (`config/dataset_evaluation_scorecard.json`): not run

## Known limitations
See `manifest.json#known_limitations`.

## Attribution
This package includes information from the O*NET 31.0 Database by the U.S. Department of Labor,
Employment and Training Administration (USDOL/ETA). Used under the CC BY 4.0 license. O*NET® is a
trademark of USDOL/ETA. DreamCo has modified all or some of this information. USDOL/ETA has not
approved, endorsed, or tested these modifications.

License: https://creativecommons.org/licenses/by/4.0/ . Source: https://www.onetcenter.org/database.html .
The O*NET® Database is sponsored by USDOL/ETA and developed by the National Center for O*NET Development.
Full text to copy into derivatives: `ATTRIBUTION.md`. Change list: `MODIFICATIONS.md`.

## Rights notes added 2026-10-05 (license review)
Source pages and read dates are in `reports/DATA_PACKAGE_LICENSE_QA_REVIEW.md`.
- Recipients keep every CC BY 4.0 right in O*NET®-derived values. DreamCo terms cover only the DreamCo synthesis layer,
  and no sale terms or technical measures may restrict the O*NET®-derived portions (CC BY 4.0 s.2(a)(5)(B)).
- No endorsement: this is a DreamCo product, not an official O*NET® or U.S. Department of Labor product (CC BY 4.0 s.2(a)(6);
  O*NET® non-endorsement sentence above).
- Trademark: CC BY 4.0 does not license trademarks (s.2(b)(2)). Use "O*NET" only as an adjective plus a generic noun
  ("built with O*NET® data"), with ®, never possessive or plural. Display name, approved by Irean Jordan on 2026-10-05
  (option A in `reports/DATA_PACKAGE_LICENSE_QA_REVIEW.md` section 1.4): "DreamCo Occupation Synthesis Pack (built with O*NET® 31.0 data)".
- Only the downloadable O*NET® 31.0 Database files are used. O*NET® Web Services data (unmodified presentation only,
  non-transferable) and the Career Exploration Tools (CC BY-ND 4.0 / Tools Developer License) are not sources.
- O*NET-SOC 2019 codes are based on the 2018 SOC (BLS, public domain; BLS asks to be cited).
