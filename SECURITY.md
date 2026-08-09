# DreamCo Security Policy

DreamCo treats security, privacy, permissions, provenance, and recoverability as release requirements.

## Report a vulnerability

Do not post exploitable details, credentials, private user data, or active secrets in a public issue.

Use GitHub's private vulnerability reporting / Security features when available for this repository. If a private reporting channel is not available, open a minimal public issue that says a security problem exists without including exploit details, secrets, or private data.

## What to include

Provide the affected file/component, the observed behavior, reproduction steps that are safe to share, likely impact, and any suggested mitigation. Remove tokens, credentials, personal data, and customer data from screenshots and logs.

## DreamCo security gates

Changes should preserve least-privilege GitHub Actions permissions, approval gates for consequential actions, secret redaction, user/tenant separation, dependency review, CodeQL/code scanning, sandbox-first external integrations, and evidence-backed repair/regression tests.

## Actions failures

Failed workflows are captured by DreamCo's Actions failure watcher and all-workflow sweep. Use **Buddy Debugger** to trace the first root cause rather than weakening checks.

## Supported branch

Security fixes target the default `main` branch unless a maintained release branch is explicitly documented.
