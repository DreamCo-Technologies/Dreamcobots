# DreamCo GitHub CI Failure and Safe Repair Foundation

This repository uses GitHub Actions for keyless test execution, sanitized failure reporting, and human-reviewed repair pull requests.

## Pull request checks

The DreamCo PR Quality Gate runs make test-all on every pull request targeting main. The Makefile runs:
- JSON contract validation.
- Five-stage pipeline and policy-boundary tests.
- Repair-report redaction and repair-PR guard tests.
- Python compile checks for the stage and reverse-engineering packages.

The Repository Test Matrix remains a separate broader workflow. Keep its required check enabled alongside the DreamCo PR check when configuring branch protection.

## Failure reports

The PR and mainline workflows upload bounded JSON reports. Raw runner logs are not uploaded by these new workflows. The report generator redacts common credential formats, email addresses, phone numbers, and SSNs before storing a short excerpt.

Sanitization is defense in depth, not a guarantee that arbitrary logs are safe to publish. Treat report artifacts as internal diagnostic material and review them before sharing externally.

## Mainline recovery

Every push to main runs the mainline health check. A failure opens or updates an issue with the commit, workflow run, and sanitized excerpt. The workflow never pushes to main, creates an automatic revert, or invokes an AI model.

## Safe repair pull requests

The Promote Validated Repair Branch workflow is manually dispatched from the Actions tab. Supply an existing repair branch name. It compares that branch with origin/main and checks only Git metadata and diff text; it does not check out or execute code from the candidate branch.

The validator is fail-closed. It requires exact agreement between the changed-file inventory and each parsed diff section, and rejects unmatched paths, extra diff sections, non-normalized paths, binary changes, and file-mode changes. It permits only added or modified files under buddy/, server/, client/, shared/, or tools/, with a 20-file and 1,500-changed-line limit. It blocks workflow, contract, policy, security, migration, and secret paths; modifications or deletions of existing tests; sensitive security/policy/auth tests; deletions and renames; credential-like additions; and changes to the validator itself. New non-security Python test modules may be added.

Passing this structural check does not mean the code is correct. The resulting PR must pass all required checks and receive human review before merge.

## Required repository settings

The repository ruleset named "Code Quality Copilot review for default branch" was observed with enforcement disabled when this foundation was prepared. A repository administrator must enable or replace it.

For main, configure:
1. Require a pull request before merging.
2. Require the DreamCo required tests check.
3. Require the Repository Test Matrix check (governed-local-tests) if that workflow is intended to gate all repository changes.
4. Require branches to be up to date, or use a merge queue after verifying every required workflow supports the merge_group event.
5. Block force pushes and deletion of main.
6. Require review of the proposed changes.

Do not make the new required status check mandatory until it has completed successfully at least once. Do not enable merge queue until the required workflows are confirmed to run for merge-group events.

## Cost and credentials

No model provider, model endpoint, API key, paid runner, or external repair service is required. The workflows use GitHub-hosted runners and GitHub's built-in token with job-scoped permissions.
