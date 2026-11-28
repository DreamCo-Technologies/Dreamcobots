# DreamCo GitHub CI Failure and Safe Repair Foundation

This repository uses GitHub Actions for keyless test execution, metadata-only failure reporting, and human-reviewed repair pull requests.

## Pull request checks

The DreamCo PR Quality Gate runs `make test-all` on every pull request targeting `main`. The Makefile runs:
- JSON contract validation.
- Five-stage pipeline and policy-boundary tests.
- Failure-report and safe-repair validator regression tests.
- Python compile checks for the stage and reverse-engineering packages.

The DreamCo Five-Stage Reverse Engineering Gate, Repository Test Matrix, Core Health, Code Trust Gate, and CodeQL are separate repository workflows. Require the applicable checks in the `main` ruleset after confirming each one has completed successfully.

## Failure reports

The PR and mainline workflows upload metadata-only JSON reports containing status, exit code, commit, and run ID. Raw runner logs and failure excerpts are deliberately omitted from artifacts and public issues because arbitrary logs cannot be reliably sanitized. A small sanitizer remains covered by regression tests but is not used to publish log text. Diagnostic details remain in the GitHub Actions run.

## Mainline recovery

Every push to `main` runs the mainline health check. A failure opens or updates an issue with the commit and workflow-run link, without copying log output. The workflow never pushes to `main`, creates an automatic revert, or invokes an AI model.

## Safe repair pull requests

The Promote Validated Repair Branch workflow is manually dispatched from the Actions tab. Supply an existing repair branch name. It compares that branch with `origin/main` using trusted workflow code; it does not check out or execute candidate code.

The validator is fail-closed. It requires exact agreement between the changed-file inventory and each parsed diff section, and rejects unmatched paths, extra diff sections, duplicate entries, non-normalized paths, binary changes, renames, and file-mode changes. It permits only added or modified files under `buddy/`, `server/`, `client/`, `shared/`, or `tools/`, with a 20-file and 1,500-changed-line limit. It blocks workflow, contract, policy, security, migration, and secret paths; modifications or deletions of existing tests; sensitive security/policy/auth tests; credential-like additions; and changes to the validator itself. New non-security Python test modules may be added.

Passing this structural check does not mean the code is correct. The resulting PR must pass all required checks and receive human review before merge.

## Required repository settings

The repository ruleset named "Code Quality Copilot review for default branch" was observed with enforcement disabled when this foundation was prepared. A repository administrator must enable or replace it; this change does not alter repository settings.

For `main`, configure:
1. Require a pull request before merging and at least one approval.
2. Require the DreamCo required tests check.
3. Require the DreamCo Five-Stage Reverse Engineering Gate.
4. Require the Repository Test Matrix check (`governed-local-tests`).
5. Require Code Trust Gate and CodeQL if those checks are part of the repository's release policy.
6. Require branches to be up to date, or use a merge queue only after verifying every required workflow supports the `merge_group` event.
7. Block force pushes and deletion of `main`.

Do not make a new required status check mandatory until it has completed successfully at least once. Do not enable merge queue until the required workflows are confirmed to run for merge-group events.

## Cost and credentials

No model provider, model endpoint, API key, paid runner, or external repair service is required. The workflows use GitHub-hosted runners and GitHub's built-in token with job-scoped permissions.

## Stage 06 keyless repair planning

Stage 06 (`stages/06_repo_repair/__main__.py`) consumes a `pytest-json-report` file or a trusted mainline failure observation. It records only bounded test IDs and summary counts; it does not copy traceback text or raw logs into its result.

- Pull-request runs are **dry-run only**. The PR Quality Gate publishes a repair plan alongside the sanitized CI report; it never edits the contributor's branch.
- Only five known generated-index test families can map to fixed, repository-owned builder commands. Unknown, ambiguous, security, permissions, billing, dependency, source-code, and policy failures return `NO_ALLOWLISTED_AUTOMATIC_REPAIR` for human triage.
- The path allowlist is hard-coded to generated artifacts under `artifacts/`, `command-center/data/`, `config/bots/`, `config/generated/`, `reports/`, and `website/data/`. A caller cannot expand it to source, tests, workflows, contracts, or secrets.
- `--apply` is blocked in pull-request and non-main GitHub contexts. It requires a clean trusted `main` checkout and runs fixed commands in a detached temporary Git worktree. The resulting patch is an unmerged review artifact; it does not commit, push, open, approve, or merge a PR.
- Attempt history is capped at three per failure fingerprint. No model is called and no API key is needed.

Run the report and planner locally without applying changes:

```bash
make test-report
python stages/06_repo_repair/__main__.py --report reports/pytest-report.json
```

Local execution requires an explicit `--apply --allow-local-apply` on a clean `main` checkout. The post-merge `Buddy CI Safe Generated-Artifact Repair` workflow records the Stage 06 plan and continues to use the existing deterministic generated-artifact repair lane. Its repair branch still requires a human to open/review the PR because repository policy blocks automatic PR creation by `GITHUB_TOKEN`.

The canonical dependency file for this pipeline is `requirements-reverse-engineer.txt`; this repository does not use a root `requirements.txt`.
