# Repository health repair runbook

## Why this exists

The November 18, 2026 repository audit found three deterministic drift failures in the fleet/prospectus gate and seven npm audit findings (three high, four moderate). The fleet runtime's separate offline sandbox evidence showed 1,101 profiles and 8,460 declared capability checks passing; the failing prospectus tests were generated-data freshness/accounting failures, not evidence of live external integrations.

## Safe repair command

From a clean checkout on a dedicated branch:

```bash
bash tools/reconcile_repository_health.sh
```

The script:

1. Installs the exact lockfile dependencies.
2. Applies only non-breaking `npm audit fix` updates and requires the high-severity audit gate to pass. It never uses `--force`.
3. Runs the repository's existing full fleet-truth regeneration script.
4. Runs the targeted fleet, Actions prospectus, file prospectus, Pages feature, and navigation regression tests.
5. Verifies the public site and production bundle.

The command deliberately stops at the first failed gate. It does not suppress failures, create runtime evidence, merge a PR, deploy Pages, or write to `main`.

## Review and release

After it passes, inspect the complete diff, especially `package-lock.json` and generated JSON under `config/generated/` and `website/data/`. Commit the result to a separate branch and open a PR. Merge only after all repository-required checks pass. The existing Pages deployment workflow should then publish the merged site.

## Remaining certification boundary

A successful static build or offline sandbox test is not proof that authenticated external providers, payment flows, production secrets, or live model adapters are operational. Those require their own configured credentials, provider sandboxes, owner approvals, and independent runtime evidence.
