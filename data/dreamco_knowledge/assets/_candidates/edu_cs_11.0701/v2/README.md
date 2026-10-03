# v2 reviewer copy: edu-cs-11.0701 after the Edu-Career-Pathways fixes (PR #12441, claimed commit 8cc1ce1)

Reviewed 2026-10-02, about 17:20 CT. The files were read in place under `<workspace>/edu-career-pathways` and not copied or modified.
Their pytest run used `-p no:cacheprovider` with `PYTHONDONTWRITEBYTECODE=1`, so nothing was written there.
Commit 8cc1ce1 cannot be verified on the box: the edu folder is not a git checkout. The file sha256 values are in `candidate.json#reviewed_files_sha256`.

- `candidate.json`: reviewer candidate with merchant-assigned scores and justifications. Its provenance and asset paths point at their files.
- `triage_score.json`: `tools/score_data_package_candidate.py` gives **66.0, quality_review**. Builder self-estimate was 66.75; v1 was 56.25.
- `license_gate.json`: gate run on their asset dir. Result is **approved_for_private_use**, with the rights ceiling at approved_for_sale and 0 warnings. Failed checks (all sale-scope): scorecard_threshold, synthesis_asset_record (no validation evidence ids), owner_approval.

## validation_evidence_ids: what the sale check accepts today, and the convention to use

Schema (`schemas/data_package_synthesis_asset.schema.json`): an object with exactly the keys `sandbox`, `benchmark`, `holdout`, and `regression`. All four keys are required, and no other keys are allowed. Each value is an array of unique, non-empty strings.

Gate (`synthesis_asset_record`, sale scope) passes only if:
- `human_layer`, `machine_layer`, and `dreamco_analysis` are non-null;
- `commercial_redistribution_allowed` is true;
- there are at least 1 evidence ids in total across the four lists;
- `asset.json` is consistent with `provenance.json`.

The gate does not yet resolve ids to files, so any string would pass. Use the convention below; resolution should be enforced before any sale.

ID format: `<kind>:<asset_id>:<YYYYMMDD>-<NN>`. It resolves to the file `data/dreamco_knowledge/evidence/<kind>/<asset_id>/<YYYYMMDD>-<NN>.json`. That file is an evidence record with:
- the `config/evidence_provenance_schema.json` required fields:
  - `evidence_id`: equals the id;
  - `capability_id`;
  - `source_type`: dreamco_experiment, human_evaluation, or benchmark;
  - `source_reference`: the asset integrity_hash it evaluated;
  - `retrieved_at`;
  - `content_version`;
  - `license_or_usage_basis`;
  - `transformation`: original_evaluation;
  - `evaluator_version`: grader, model, and rubric version;
  - `integrity_hash`: sha256 of the results/transcripts file;
- plus `split`, `n_items`, `metric`, `score`, `threshold`, `passed`, and, for benchmark runs only, `baseline_score`.

```json
"validation_evidence_ids": {
  "sandbox":    ["sandbox:edu-cs-11.0701:20261009-01"],
  "benchmark":  ["benchmark:edu-cs-11.0701:20261012-01"],
  "holdout":    ["holdout:edu-cs-11.0701:20261012-02"],
  "regression": ["regression:edu-cs-11.0701:20261015-01"]
}
```

What counts for a study-plan pack:
- **sandbox**: an executed run of the 6 practice prompts by a sandboxed bot or model. The run produces responses, applies the 3-criterion rubrics, and saves hashed transcripts. It shows the tasks are completable and gradable without leaking O*NET text.
- **benchmark**: a fixed career-guidance question set, for example "which entry roles fit CIP 11.0701, what preparation do they need". Score a baseline answer without the plan and an answer with the plan in context, using the same grader and rubric. Report baseline_score, score, and the delta.
- **holdout**: rubric-graded items that were not used while tuning build.py. Examples: held-out practice tasks or held-out majors, ideally including human graders with inter-rater agreement (a `human_evaluation` record).
- **regression**: a rebuild of the same version that diffs links, targets, and scores against the prior release. No unexplained changes, and no score drop.
- **Not acceptable**: `evidence/pytest.txt`. Build-integrity tests, schema checks, and hash checks are integrity evidence, not validation, and the builder already declines to count them.
