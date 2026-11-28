# Research, benchmark, code/training recovery, and learning points

The daily Hugging Face research brief is connected to a candidate pipeline:

`Hugging Face category/task → cited research item → benchmark candidate → fixture/adapter review → isolated benchmark run → failure diagnosis or verified mastery`

## From research to benchmark

Each research item can become a `dreamco.research_benchmark_candidate.v1` record with the citation, date, current Hugging Face category/task, evidence type (real robot, simulation, benchmark-only, preprint, official documentation, speculation, or mixed), demonstrated capability, limitations, proposed DreamCo test, and license/data-rights review state.

```sh
python3 tools/buddy_research_benchmark_bridge.py candidate finding.json
```

This creates a proposal only. It does not add a score, claim mastery, download or train on the source, or award points. New Hugging Face task categories fall back to a generic task-specific benchmark domain and can be mapped later.

## From measured failure to recovery work

Only a verified benchmark failure becomes a diagnostic job:

```sh
python3 tools/buddy_research_benchmark_bridge.py failure benchmark-failure.json
```

Code, repository, source-tracking, and provenance gaps create a reverse-engineering plan: pin the commit and run, trace behavior through code/logs/artifacts, reproduce with a synthetic fixture, patch DreamCo-owned code, and add regression plus holdout checks. Training, checkpoint, adapter-quality, and distillation gaps create a training-diagnosis plan: inspect data rights, teacher terms, hardware, configuration and hashes, then design a small controlled experiment. A plan does not start training or execute third-party code. Distillation is limited to a user-owned student and data/teacher outputs whose terms permit the use; separate approval, budget, compute and training-data authorization remain required.

The same-category failures are clustered by capability and failure mode. The output preserves evidence references and requires held-out, regression and safety checks before any promotion. Research findings alone are not failures and cannot trigger training.

## Learning points

The token interpretation implemented here is **non-transferable learning points**, separate from the repository's financial token-transfer feature. Reading research, creating a candidate, failed runs, unverified claims, and external-model-only success earn zero points. A mastery event requires owner approval and at least three distinct verified runs on the same immutable benchmark version; every run must pass its task-score floor, hidden holdout, regression, safety and native-success checks. Duplicate awards share one idempotency key.

The policy config controls the point amount and gates. The Python ledger helper writes user-scoped JSON records with exclusive creation and file permissions under a caller-supplied private data directory. It does not write into a Git-tracked path by default, connect to a wallet, transfer crypto, or assign cash value. An app-level account/authentication adapter and trusted benchmark-result ingestion are still needed before exposing the balance to users.

## Validation boundary

The bridge validates structure and policy gates; it cannot prove a caller-supplied benchmark result is authentic. A production account service must pass verified receipts from its trusted benchmark runner, enforce user identity, and expose no client route that can directly submit arbitrary “verified” flags. No model weights, third-party source code, or live provider are modified by these bridges.
