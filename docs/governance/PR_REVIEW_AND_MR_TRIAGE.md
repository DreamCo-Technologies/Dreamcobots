# DreamCo PR Review and MR Issue Triage

## Security model

The workflow uses pull_request_target so it can update a deduplicated remediation issue and one PR comment. It checks out only the pull request base commit and never checks out or executes code from the untrusted PR head. It obtains the patch through GitHub's PR diff endpoint and passes that text to the auditor.

The auditor is intentionally patch-level. It scans added lines for credential patterns and unsupported absolute claims, flags quarantined staging paths, checks checkpoint evidence updates, and rejects moving competitor revision labels. It does not execute changed Python, shell, JavaScript, or workflow code. Isolated CI jobs must perform syntax, tests, type checks, workflow linting, dependency checks, and CodeQL.

## Decisions

- Any blocker or conflict-marker issue produces CHANGES_REQUESTED and a failing required check.
- A clean patch is REVIEW_REQUIRED, never an automatic approval.
- The workflow updates one marker-managed PR comment.
- Remediation issues are deduplicated by stable finding fingerprint.
- The bot does not commit fixes, approve, merge, or close PRs.
- Humans remain responsible for rights determinations, clean-room originality, and final merge decisions.

## Limitations

A patch scanner cannot prove that an entire repository is secret-free, that a model is genuinely trained, or that a dataset is uncontaminated. Existing trust gates, checkpoint evidence validation, benchmark holdout protections, CodeQL, and branch protection remain required. A hash proves byte identity, not ownership or legal permission.
