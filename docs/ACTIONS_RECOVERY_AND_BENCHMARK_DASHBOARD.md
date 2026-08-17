# Actions Recovery, PR Audit & Benchmark Dashboard

## Purpose
Provide one owner-facing control surface for finding problems, auditing pull requests, repairing approved issues, and measuring current benchmark health.

## Buttons

### 🔎 Find Problems & Bugs
Run a bounded repository health scan covering:
- recent failed Actions runs
- repeated failure fingerprints
- broken workflow references
- missing scripts/files
- dependency/build/type errors
- security findings
- stale or conflicting configuration
- benchmark regressions
- missing evidence
- broken Pages/download paths

Every finding must retain its source run, job, step, commit, severity, evidence and status.

### 🔍 Scan Pull Requests
Audit open PRs for:
- merge conflicts
- failing required checks
- stale branches
- missing tests
- missing documentation
- security/dependency findings
- changed files without appropriate coverage
- duplicate or overlapping PR scope
- unsupported configuration
- claims that are not backed by evidence

Classify each PR as `healthy`, `review`, `blocked`, `stale`, or `duplicate_candidate`. Never close or merge a PR solely because a scanner recommends it.

### 🛠 Fix Problems
Create a review branch and generate the smallest repair that addresses an evidence-backed finding. Run targeted tests, dependent regression tests, security checks and relevant benchmarks. Open a PR with the evidence. High-impact or destructive changes remain approval-gated.

### 🔁 Replay Failures
Re-run only failed jobs/runs that are still relevant. Do not repeatedly replay deterministic failures without a new code/configuration change. Classify infrastructure/flaky failures separately.

### 📊 Benchmark Health
Show current benchmark evidence as:
- green = passed on the current measured revision/environment
- red = failed on the current measured revision/environment
- yellow = incomplete, stale, or awaiting evidence
- gray = not executed / not applicable

Historical GitHub failures remain historical. The dashboard must never rewrite them to green. Instead it shows `historical failure → superseded by verified run` when a later run proves the issue resolved.

## Benchmark percentage calculation

`green_pct = green / (green + red) * 100`

`red_pct = red / (green + red) * 100`

Yellow/incomplete is reported separately and is never silently counted as green.

The denominator must identify the benchmark suite, fixture version, model/runtime version, repository commit and evidence timestamp. Percentages without that provenance are not release evidence.

## Recovery state machine

```text
DISCOVER → FINGERPRINT → CLASSIFY → REPRODUCE → PROPOSE FIX
                                      ↓
                                  APPROVAL
                                      ↓
                              PATCH → TEST → BENCHMARK
                                      ↓
                                  VERIFY
                                      ↓
                            PR / RELEASE EVIDENCE
```

## Truth contract

GitHub Actions history is immutable evidence. The system cannot and should not make old failed runs appear successful. The objective is a green **current verified state**, with historical failures linked to their verified repairs.

A green dashboard requires actual successful GitHub evidence. Planned, skipped, cancelled, stale, or missing runs are not green.

## Efficiency rules

- Prefer targeted checks before full-system certification.
- Reuse valid evidence until the measured revision/environment changes.
- Deduplicate identical root causes.
- Limit parallel work to the repository's configured runner budget.
- Stop repeated retries after a configurable threshold.
- Store artifacts and fingerprints so the same failure can be diagnosed without rerunning everything.
