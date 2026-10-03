# Candidate: edu-cs-11.0701 (Edu-Career-Pathways CS study plan)

Source asset (read-only, not copied): `<workspace>/edu-career-pathways/study_plans/11.0701_computer_science.md`
(sha256 f38df6b3863ae9212bc512921bb0ebbdb1c75e96db282452fdb2bc6674b0bc27).

- `as_is/`: candidate built only from what the asset ships today (no provenance.json, no ownership_class).
  `triage_score.json` = tools/score_data_package_candidate.py (56.25, quality_review);
  `license_gate.json` = gate result (reference_only).
- `corrected/`: same asset with provenance.json, asset.json (plan 5.2 synthesis asset), and ownership classes.
  Gate: approved_for_private_use. Rights checks all pass. It is capped because there is no scorecard,
  the synthesis record is incomplete (machine_layer, dreamco_analysis, and validation evidence are empty),
  and there is no owner approval.
- `templates/`: copy `provenance.json`, `asset.json`, and `candidate.json` next to each study plan. Update asset_id,
  asset_files[].sha256 / human_layer.sha256, integrity_hash (same value in both files), and descriptions, then run:
  `python3 tools/license_provenance_gate.py <dir> --asset-root <edu repo root> --out <dir>/license_gate.json`

Fix in build.py PROVENANCE footer to clear the attribution warnings: add "O*NET® is a trademark of USDOL/ETA.",
"DreamCo has modified all or some of this information.", and state that the crosswalk (Crosswalk Files by
USDOL/ETA) is licensed under CC BY 4.0. Optionally link https://creativecommons.org/licenses/by/4.0/.
