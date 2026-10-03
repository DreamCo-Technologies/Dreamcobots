# v3 reviewer copy: edu-cs-11.0701 at PR #12441 head 687b3c1 (Edu-Career-Pathways)

Reviewed on 2026-10-02, about 18:08 to 18:25 CT.

PR head `687b3c1a2a4b23a5ae8fae13925bebf7eabaf197` was fetched to branch `pr-12441-v3` and checked out in a separate worktree, `<workspace>/edu-pr12441-v3` (HEAD verified). Nothing in the PR or worktree was modified. All reruns (build, regression, tests) ran in scratch copies under `<workspace>/edu-v3-scratch/`. Paths below are relative to `study_packs/career_pathways/` unless they start with `tools/`, `config/` or `schemas/`, which are relative to the merchant worktree.

## Result

| | v2 (8cc1ce1) | v3 (687b3c1) |
|---|---|---|
| Merchant triage, authored CS asset (`tools/score_data_package_candidate.py`) | 66.0, quality_review | **72.4, approved_for_private_use** (scorer status at 70 or above; still under 75) |
| Gate, authored CS (`tools/license_provenance_gate.py`) | approved_for_private_use | **approved_for_private_use**. Rights ceiling approved_for_sale, all 7 rights checks pass. Failed: scorecard_threshold, owner_approval. synthesis_asset_record is now a warn (1 perspective) instead of a fail. |
| Generated tier (1,017 plans), scored separately | n/a | **59.25, quality_review**. Gate: approved_for_private_use for all 1,017. Rights ceiling approved_for_sale. Failed: scorecard_threshold, synthesis_asset_record (no evidence ids), owner_approval. |

Sale is still blocked for 4 reasons:
- The triage score is under 75.
- The separate dataset scorecard (`config/dataset_evaluation_scorecard.json`, at least 75 plus release gates) has never been run.
- There is no owner approval.
- The gate does not yet resolve evidence ids.

| Dimension (weight) | v2 | v3 | Reason (full text in `candidate.json`) |
|---|---|---|---|
| rights_clarity (20) | 85 | 88 | Job Zone text is no longer quoted, so the plan contains no third-party prose. Gate rights all pass. Still: DreamCo-layer commercial terms are unset, and plan.json has no attribution block. |
| training_relevance (15) | 60 | 70 | Items are self-contained authored scenarios with rubric and reference outline. 5-gram Jaccard is 0.0006 (v2: 0.2285). Only 6 per plan; no graded responses. |
| data_quality (15) | 55 | 66 | Software Developers is in, Database Architects is out, CAD is gone, outline topics are distinct, and the citations are correct. There is no human review, the means are unweighted, and Design and Administration and Management are silently skipped. |
| provenance (10) | 85 | 90 | The commit is verifiable, source hashes match fresh downloads, the rebuild is byte-identical, and regression records are hash-linked. created_at is date-only, and the recorded gate-file hash is stale. |
| freshness (10) | 90 | 90 | Unchanged (O*NET 31.0). |
| coverage/diversity (10) | 35 | 35 | Authored tier is still 27 majors with one perspective. The generated tier is scored separately. BLS is absent. |
| format/usability (5) | 70 | 75 | Self-contained tasks, tier labels, coverage.csv. No data dictionary. |
| benchmark_value (5) | 25 | 40 | Reference outlines exist. No holdout, pilot or baseline. |
| commercial_package_potential (5) | 40 | 55 | There is now a real non-templated DreamCo layer. It is unvalidated, AI-authored, has no owner approval, and has no BLS data. |
| maintenance/updateability (5) | 80 | 88 | Reproducible release diff (rerun matches), byte-reproducible build, 2103/2103 tests pass. Still pinned to 31.0. |

## Claim verification (independent checks; scripts in `verification/scripts/`)

1. **162 hand-written scenarios: VERIFIED (not templated).** See `verification/diversity_report.json`.
   - Structure: 162/162 items have 3 criteria and a reference outline. 159 distinct formats, 473 distinct rubric criterion names (each used at most twice), 154/162 distinct 6-token openings once the label prefix is removed.
   - Overlap: mean pairwise 5-gram Jaccard 0.0006 (max 0.024; 0 pairs above 0.2). Only 0.9% of 5-gram occurrences appear in 5 or more items, and those are all the "DreamCo-original practice prompt" label.
   - For contrast, v2 had 1 opening, 10 criterion names, Jaccard 0.2285, and 80% boilerplate.
   - CS spot-check: all 6 citations exist under the stated SOC in O*NET 31.0, and each scenario does the cited task (14638 test plan; 5313 security training; 21670 modify software; 14639 test modifications; 5318 coordinate implementation with vendors; 21662 feasibility within time and cost). The technical content is sound.
   - 8 random non-CS items also align with their tasks.
   - The 162 items are AI-authored ("hand-written" means per-item authored by the agent, not by a human).
2. **Per-major course topics; no CAD for CS: VERIFIED.** All 297 topic strings across the 27 majors are distinct. "CAD" and "technical drawing" appear only in the Mechanical and Civil Engineering outlines, where they fit, and not in the CS md or plan.json. Minor: the CS outline maps 6 of its top-8 knowledge areas and omits Design and Administration and Management without saying so.
3. **Software Developers is a target; Database Architects removed: VERIFIED.** Targets are 15-1252.00, 15-1253.00 and 15-1212.00, all Job Zone 4 in 31.0 `job_zones.csv`. The override reason is recorded in `authored/target_overrides.json`, plan.json and asset.json. Database Architects stays as a linked occupation only.
4. **Original-wording next steps; 0 O*NET leakage: VERIFIED.**
   - Method: 5-word shingles, tokens `[a-z0-9]+`, compared against O*NET 31.0 (`task_statements`, `occupation_data` Description, `job_zone_reference`; sha256-verified fresh downloads) and O*NET 30.3 (Task Statements, Occupation Data, Job Zone Reference from `db_30_3_excel.zip` sha256 78703906…). Shingles that fall entirely inside an occupation title were excluded, as was the provenance footer.
   - Result for the 27 authored md files, plan.json files and authored/*.json: **0 non-title hits** (2 raw hits, both title-only).
   - Control: the same checker finds 41 hits in the v2 CS plan, matching the regression's baseline_5gram_hits = 41.
   - Generated tier: 0 non-title O*NET shingles outside the attributed quote lines. The 2 hits found are a CIP title and an occupation title that overlaps Job Zone examples.
   - See `verification/leakage_report.json`.
5. **Regression evidence: VERIFIED, with 2 caveats.** See `verification/regression_and_evidence_check.json`.
   - Coverage: 54 ids (27 authored × -01/-02). All resolve and conform to the schema (required fields, enums, evidence_id, source_reference = asset integrity_hash = plan md sha256, integrity_hash = sha256 of the results file, plus split/n_items/metric/score/threshold/passed; passed 1.0 ≥ 1.0).
   - Empty lists: sandbox, benchmark and holdout are empty everywhere, and generated plans have no ids.
   - Genuine comparison: it is a real item-level comparison against git 8cc1ce1. For CS: 68 items, 60 preserved, 6 changed with reason, 2 improved.
   - My rerun of regression.py matches the committed -02 items exactly, and a rebuild with build.py is byte-identical apart from the gate timestamp.
   - Caveat (a): ids resolve under `study_packs/career_pathways/data/dreamco_knowledge/evidence/…`, not at the repo-root `data/dreamco_knowledge/evidence/…` of the convention.
   - Caveat (b): each results file's `current.files[...license_gate.json]` hash refers to a pre-regeneration gate file that is not in the commit (only evaluated_at differs).
   - The reasons for changes are self-authored, and the regression measures release stability, not quality.
6. **1,044 majors (27 authored + 1,017 generated, tier-labeled): VERIFIED. Attribution is present and correct in content, but machine labels are wrong.**
   - Quotes: all 6,102 generated items quote their O*NET 31.0 task verbatim (0 mismatches) with the correct SOC/Task ID pair.
   - md files: each quote line carries "(quoted verbatim, USDOL/ETA, CC BY 4.0)", and all 1,044 md footers carry every required notice (CC BY 4.0 + URL, ® trademark, "DreamCo has modified…", no endorsement, Crosswalk Files).
   - JSON: each JSON item has an `onet_task_statement_note` attribution. No third-party notice was stripped.
   - Gaps:
     - `data/practice_tasks.json` has no license URL and no modification notice.
     - Its file-level `label` ("DreamCo-original practice prompt"), `authorship` ("authored by Grok… (AI)") and `ownership_class` (synthetic_generated_by_dreamco) describe all 6,264 items, including the 6,102 that embed O*NET text.
     - The generated items' own `ownership_class` is synthetic_generated_by_dreamco.
     - `plan.json` (both tiers) has no attribution or license block.
     - CC BY permits all of this, but the machine layer should say "mixed: quoted O*NET text + DreamCo template" and carry the notices when it is distributed on its own.
   - Gate: it passes them (the rights checks read provenance.json; it does not inspect per-item quotes or JSON labels).
   - Recommendation:
     - Score and sell the generated tier separately; at most give it away as a free index or upsell. Under the DreamCo-own-perspective policy it is reformatted free O*NET plus one template.
     - Do not let it raise the authored asset's coverage. Bundling would raise coverage but pull data_quality, training_relevance and commercial toward the generated tier's 40/30/15, because 97% of items would be templated.
     - Content issues seen: unreviewed rule targets can be implausible (Power Plant Engineering → Robotics, Photonics, Wind Energy Engineers), and some cited tasks do not suit a first-year graduate ("Supervise technologists, technicians, or other engineers").
7. **BLS OOH: NOT reachable.** On 2026-10-02 at 18:17 CT, with UA `DreamCo-Research/1.0 (ireanjordan24@github)`, both www.bls.gov/ooh/ and an OOH occupation page returned HTTP/2 403 (AkamaiGHost "Access Denied" bot page). The default curl UA also got 403, while the onetcenter.org control returned 200. This matches the builder's report. See `verification/bls_reachability.txt`.

Tests:
- `tests/test_license_provenance_gate.py`: 22/22 pass.
- PR suite in the bare worktree: 1050 failed, because `raw/` data is gitignored and not committed.
- PR suite in a scratch copy with verified raw files: 1059 passed + 1044 skipped (no jsonschema), and **2103/2103 passed** with `<workspace>/venv-ecp` (jsonschema).

## Moves to cross 75 (projections; totals computed by the scorer on `projections/*.candidate.json`)

The dimension deltas are reviewer assumptions about a move that has been completed and verified. The totals are scorer output. Current score: 72.4.

| # | Move | Needs | Assumed Δ | Projected (gain) |
|---|---|---|---|---|
| 1 | Owner (Irean) acts as human holdout grader: blind-grade responses to the 6 CS items plus 1-2 held-out items against the rubrics, and review each reference outline for correctness. Record as `holdout:edu-cs-11.0701:<date>-01` (human_evaluation). | Human only, no model key | dq +6, bench +15, train +4, comm +5 | 74.9 (+2.5) |
| 2 | Benchmark: baseline vs plan-in-context on a fixed career-guidance question set, graded by an independent grader. | Model key, or Irean grading both arms blind | bench +15, train +4, comm +5 | 74.0 (+1.6) |
| 3 | Second official perspective (BLS via an owner-supplied manual download, or another pinned public source). Clears the gate warning. | Human download (BLS blocks this box) | cov +10, comm +5 | 73.65 (+1.25) |
| 4 | Machine-layer rights fix: license, notice and modification block in plan.json and practice_tasks.json; correct the mixed-content label and ownership; set commercial terms for the DreamCo layer. | Nothing | rights +4 | 73.2 (+0.8) |
| 5 | Role-filtered or weighted knowledge means, or show both; state which top elements the outline skips. | Nothing | dq +3 | 72.85 (+0.45) |
| 6 | Data dictionary; full created_at timestamp; point results at the committed gate file; make evidence resolve from the repo root. | Nothing | fmt +5, prov +2 | 72.85 (+0.45) |
| 7 | Sandbox run: a sandboxed model completes the 6 prompts, with hashed transcripts graded by a different grader. | Model key | bench +5 | 72.65 (+0.25) |

Bundles:
- **A (no model key: 1+4+5+6): 76.6.**
- B (A + 2 + 7): 78.45.
- C (B + 3): 79.7.

Bundle A crosses 75 only if Irean's holdout grading actually happens and the reviewed items hold up. No combination of no-human, no-key moves alone reaches 75 (4+5+6 = +1.7 → 74.1). Sale additionally needs the dataset scorecard and its release gates (benchmark_report_complete, train/validation/test separation, privacy_safety_review) plus an explicit owner_approval record.

## Files

- `candidate.json`, `triage_score.json`, `license_gate.json` (gate run from `study_packs/career_pathways/` with `--asset-root .`, so paths are relative): authored CS asset.
- `scorecard.json`: v2→v3 dimensions, weights, scorer outputs and gate summary.
- `generated_tier/`: separate candidate and score, plus a gate run on one sample plan (14.4802).
- `verification/`: diversity, leakage, regression/evidence, gate summary for all 1,044 plans, BLS check, and scripts. The scripts use absolute scratch paths: `<workspace>/edu-v3-scratch/onet31`, `<workspace>/edu-v3-scratch/onet303`.
- `projections/`: projected candidates and their scorer outputs (not scores of any existing asset).

Commands:

```
env -u GITHUB_TOKEN -u GH_TOKEN git -C <merchant-repo> fetch origin pull/12441/head:pr-12441-v3
env -u GITHUB_TOKEN -u GH_TOKEN git -C <merchant-repo> worktree add <workspace>/edu-pr12441-v3 pr-12441-v3   # HEAD 687b3c1a2
cd <workspace>/edu-pr12441-v3/study_packs/career_pathways
python3 <merchant-repo>/tools/license_provenance_gate.py study_plans/11.0701_computer_science --asset-root . --out <v3>/license_gate.json
python3 tools/score_data_package_candidate.py <v3>/candidate.json            # run from <merchant-repo>
python3 tools/score_data_package_candidate.py <v3>/generated_tier/candidate.json
python3 -m pytest -q -p no:cacheprovider tests/test_license_provenance_gate.py                       # in <merchant-repo>: 22 passed
```
