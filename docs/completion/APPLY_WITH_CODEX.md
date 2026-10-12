# DreamCo consolidated implementation

This branch reconciles the registry audit, interrupted Pages/runtime audit, evidence-integrity fixes, and human-reviewed evaluation framework. Original workspaces are preserved. It adds a source-backed division compiler, strategy selection policy, generated strategy/catalog pages, offline nightly verification, and scoped subscription status.

## Truth boundaries

- The supplied source contains 62 divisions and 1,000 named proposals: 600 original upgrades, 200 Shopping operations, 200 Creator operations. The 1,600 target is not fabricated.
- Generated sandbox wrappers are not specialist implementations or live integrations.
- The 78 strategy records comprise 72 existing research techniques plus six configuration/evaluation interventions. Policy selection is implemented; GPU training adapters and live experiments are not universally implemented.
- No new live benchmark delta, training spend, AGI/frontier mastery, or production readiness is asserted.
- Billing is currently single-owner. Subscription status requires the existing owner token and queries only the stored customer. Multi-user billing requires authenticated tenant-to-customer mapping.
- Hosted providers, private datasets, paid runs, deployment, and model promotion require configured adapters, rights and repository approval gates.

## Install and verify

Use Node supported by package.json and Python 3.12. In a clean checkout:

```sh
npm ci
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-tools.txt
.venv/bin/python -m pip install pytest==8.3.5 pytest-subtests==0.14.2
python3 tools/compile_division_catalog.py
python3 tools/build_training_strategy_pages.py
python3 tools/general_intelligence.py
python3 tools/benchmark_suite_contracts.py
.venv/bin/python -m pytest -q tests/test_strategy_policy.py tests/test_source_division_catalog.py tests/test_cycle_evidence_integrity.py tests/test_general_intelligence.py tests/test_verify_frontier_evidence.py
node --import tsx --test tests/subscription-status.test.ts tests/model-source-connection-policy.test.ts
npm run check
npm run test:governed
npx tsx tools/run_universal_verification.ts --full
```

The bundle includes a patch against main commit `1d5ef60e95d611427a69a641301b9c3ea29cabf1`. Check the current repository before applying; existing PRs may contain the same changes. Use `git apply --check` followed by three-way reconciliation on a new branch. Never apply an overlapping feature twice.

## Application order

1. Reconcile proposal registry audit and dependency fixes already published in PR #13889.
2. Reconcile shared runtime/Pages repairs and evidence integrity.
3. Reconcile human review PR #13901; retain stricter hashes, repeat IDs and fail-closed claims.
4. Apply strategy policy, source catalog, subscription isolation, tests and workflow.
5. Regenerate canonical indexes after staging new files. Run focused checks, then full verification and offline browser checks.
6. Commit and push the new branch; open a PR. Do not merge or deploy without required reviews.

## Compact continuation prompt

Inspect live DreamCo-Technologies/Dreamcobots main and open PRs once. Reuse this consolidated branch and evidence report. Reconcile existing owners; do not duplicate working systems. Preserve no-delete/no-force-push and fail-closed production_ready/frontier/mastery. Complete remaining specialist adapters only where source requirements, rights, credentials and test fixtures are available. Run focused tests and canonical full verification; fix root causes without weakening gates. Commit, push and open/update a PR, returning exact pass/fail evidence and blockers. Do not count catalog entries or sandbox wrappers as production bots.
