# Workflow schedule demotions

Applied on branch `ops/workflow-schedule-demotions` against `main` at `fc4493bf`.

No workflow files were deleted. Demoted jobs still run on `workflow_dispatch`, and any path `push` or `pull_request` trigger they already had is unchanged.

## Kept on the colliding minute

- `keep-green.yml` stays on `17 */6 * * *`
- `actions-failure-sweep.yml` stays on `11 * * * *`
- `problem-registry.yml` stays on `17 * * * *`
- `production-readiness.yml` stays on `17 6 * * *`
- `dreamco-core-health.yml` stays on `17 5 * * *`
- `system-scan-hourly.yml` stays on `23 * * * *`

## Demoted to manual

- `buddy-65-masterbot-training.yml` (65-wide matrix, highest cost)
- `repo-capability-audit.yml`
- `masterbot-routing-audit.yml`
- `buddy-preventive-engineering.yml` (pull request and push to main still run it)
- `benchmark-evidence-loop.yml` (path push still runs it)
- `buddy-24h-sandbox-soak.yml`
- `actions-command-center.yml` (`workflow_run` still refreshes it)
- `buddy-1000-source-learning.yml`
- `continuous-learning-runner.yml`
- `intelligent-issue-cleaner.yml`
- `benchmark-tracker.yml` (push and pull request still run it)
- `note-model-hourly.yml`

## Rescheduled, not removed

- `benchmark-lessons-daily.yml`: `17 6 * * *` moved to `41 7 * * *`
- `benchmark-65-orchestrator.yml`: `*/30 * * * *` moved to `47 */6 * * *`

Restore a schedule only after a manual run shows the job still produces evidence the canonical workflow does not already cover.
