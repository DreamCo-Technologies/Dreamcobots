# Actions Recovery Controls

The Actions page should expose these controls:

- **Find Problems & Bugs** — scan current workflow evidence, build/configuration failures, security findings, benchmark regressions, broken links and missing evidence.
- **Scan Pull Requests** — inspect open PRs for conflicts, failed checks, stale branches, missing tests/docs, security findings, duplicate scope and unsupported configuration.
- **Fix Problems** — create a review branch with the smallest evidence-backed repair. Run targeted verification and open a PR. Do not silently merge.
- **Replay Failures** — retry only relevant failed jobs/runs. Avoid repeated retries of deterministic failures.
- **Benchmark Health** — show green/red/yellow/gray with provenance.
- **Recovery History** — show historical failure, root cause, repair PR, verification run and current status.

## Green-state rule
Old GitHub failures are immutable history. A green current state means a newer verified run on the relevant revision/environment passed. Historical failures are labeled superseded when appropriate; they are never rewritten.

## Repair lifecycle

`SCAN → FINGERPRINT → CLASSIFY → REPRODUCE → PROPOSE → APPROVE → PATCH → TEST → BENCHMARK → VERIFY → REPORT`

## PR lifecycle

`SCAN PRs → identify blocked/stale/duplicate candidates → explain evidence → propose action → user approval → repair/rebase/update → required checks → merge decision`

The scanner must never close, merge, delete, or rewrite a PR solely from an automated recommendation.
