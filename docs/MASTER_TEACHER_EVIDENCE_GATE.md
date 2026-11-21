# Master Teacher evidence gate

This bounded change introduces `tools/master_teacher_evidence_gate.py` and unit tests. It does **not** run model evaluations, schedule hourly execution, train weights, edit existing benchmark scores, or promote models.

## Invocation

```bash
python -m unittest tests.test_master_teacher_evidence_gate
python tools/master_teacher_evidence_gate.py path/to/authorized-evidence.json --output artifacts/master-teacher/gate.json
```

Only use evidence from authorized runners. Never put private holdout answers, personal data, API keys, or restricted datasets in the repository or generated artifacts.

Each record must identify suite/version, dataset and champion/candidate hashes, seed/config/environment, baseline and pass criteria, paired trials, latency/cost, tool use, safety, regressions, evidence, isolation/permissioned holdout provenance, contamination checks, independent verification and rollback plan. The gate blocks unknown contamination status. A previously exposed task is not unseen. Suspect holdouts must be quarantined outside the training/generator access boundary and independently replaced.

The gate is deliberately conservative: it returns **eligible_for_manual_review**, never auto-promotion. Existing repository benchmark orchestration and private holdout infrastructure should be integrated only after independent review. Do not interpret a green unit test as model mastery.

## Remaining integration work

- Identify the authorized registered suites and completed-task evidence sources.
- Run exact and near-duplicate scans against permissioned training corpora; review templates, lineage, timestamps and task-family leakage.
- Execute reproducible champion/candidate trials and prior-task regressions with uncertainty estimates.
- Convert failures into minimized, privacy-safe regression fixtures and deduplicated Bootcamp lessons without revealing holdout answers.
- Confirm the budget and obtain explicit owner authorization before any paid evaluation or weight training.
- Schedule the hourly workflow only after verifying runners, permissions, costs, and existing workflow collisions.
