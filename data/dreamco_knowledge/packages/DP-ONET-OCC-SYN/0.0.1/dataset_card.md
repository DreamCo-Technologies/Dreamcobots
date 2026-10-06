# Dataset card: DP-ONET-OCC-SYN 0.0.1 (skeleton)

**Status:** skeleton. No data assets, not evaluated, not for sale. `license_gate_status: pending` (pre-gate; plan enum pass | fail | reference_only_bundle).

## Purpose (intended)
A DreamCo-authored synthesis layer over O*NET occupational data: major-to-occupation study plans,
knowledge/skill groupings, and evaluation prompts for career-guidance bots.

## Composition
- Assets: none yet (`manifest.json#included_asset_ids` is empty; `excluded_reference_only_sources` is empty).
- Planned inputs: O*NET 31.0 Database (USDOL/ETA, CC BY 4.0) and the CIP 2020 to O*NET-SOC 2019
  crosswalk (USDOL/ETA, CC BY 4.0). These are proposed pins; see "Version pin" below.

## Ownership and rights
- O*NET and crosswalk content: third-party, `ownership_class: open_license_with_conditions`.
  Commercial use and redistribution are allowed with attribution under CC BY 4.0.
- DreamCo synthesis: `synthetic_generated_by_dreamco` / `dreamco_owned` only for material DreamCo writes.
- Every asset must carry `provenance.json` and pass `tools/license_provenance_gate.py`.

## Version pin
This package version pins O*NET 31.0. The download URLs and sha256 for `db_31_0_excel.zip`, `db_31_0_csv.zip` and the
CIP to O*NET-SOC crosswalk are in `provenance_manifest.json`, and each asset's `provenance.json` pins its per-file inputs.
The fleet catalog tool (`tools/build_universal_work_ai_catalog.py`) still defaults to 30.3 for its other users.
DP-ONET builds override that default with `--onet-zip-url https://www.onetcenter.org/dl_files/database/db_31_0_excel.zip`.
The tool reads only Occupation Data and Task Statements, so 31.0 works with it unchanged.

O*NET 31.0 replaces the single Skills file with two files:
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
