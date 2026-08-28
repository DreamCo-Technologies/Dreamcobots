# Production Push / Verification Guide

## If GitHub Actions is green

Open the repository Actions page and inspect the latest runs for the current `main` SHA. A green workflow means that workflow passed; production certification still requires the complete certification workflow and any external/runtime smoke tests.

## Local Mac verification

From a clean clone of `main`:

```bash
git fetch origin
git checkout main
git pull --ff-only
python3 --version
node --version
npm ci
python3 tools/production_readiness_gate.py
```

Then run the repository's documented verification commands from `package.json` and the relevant workflow files. Do not substitute `npm install` for `npm ci` when reproducing CI unless the project explicitly requires it.

## If a workflow fails

1. Open the failed job.
2. Read the first failing step and the surrounding log, not only the final summary.
3. Confirm the failing SHA is the current `main` SHA.
4. Reproduce locally when practical.
5. Fix the smallest root cause that preserves security and contracts.
6. Add or update a regression test.
7. Commit and push the fix.
8. Wait for the new workflow run.
9. Verify the new run and artifact before closing the issue.

## If the GitHub connector cannot push

Use the commands below on the Mac after cloning the repository:

```bash
git remote -v
git status
git fetch origin
git checkout main
git pull --ff-only
# make or copy the approved changes
git add .
git commit -m "chore: production hardening"
git push origin main
```

If `git push` is rejected, do not force-push. Inspect branch protection and authentication, then push a feature branch and open a pull request.

## Required production evidence

- Current commit SHA
- Build/test results
- Security results
- Benchmark receipts where applicable
- Buddy/fleet E2E evidence
- Actions/control-plane evidence
- Deployment health/smoke evidence
- Rollback evidence
- Observability evidence
- Cost/resource evidence where applicable

A missing external credential or hardware-dependent environment must be reported as unverified rather than replaced with a simulated green result.
