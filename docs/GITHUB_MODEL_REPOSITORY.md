# DreamCo Model GitHub Repository Standard

DreamCo's original `DreamCo-Technologies/Dreamcobots` repository is the reference implementation. Forks/templates should preserve the simple control paths while allowing domain-specific customization.

## Already represented in repository files

- **GitHub Actions:** Control Center, Buddy Test Lab, repository tests, Pages deploy, security scans, open-source evolution, self-working/offline parity, failure watcher and failure sweep.
- **GitHub Pages:** `Deploy Buddy Website` builds/verifies and deploys the public `website/` directory.
- **Dependabot:** `.github/dependabot.yml` tracks npm and GitHub Actions dependencies.
- **Code scanning:** `.github/workflows/codeql.yml` runs CodeQL on JavaScript/TypeScript and Python.
- **Dependency review:** `.github/workflows/dependency-review.yml` reviews dependency changes in pull requests.
- **Agents:** `.github/agents/` contains Buddy Debugger and Easy Updater.
- **Copilot instructions:** `.github/copilot-instructions.md` plus root `AGENTS.md` teach coding agents how to build/test/repair DreamCo.
- **Issues:** structured bug and idea forms.
- **Pull requests:** a standard evidence/verification checklist.
- **Security policy:** `SECURITY.md`.
- **Contribution guide:** `CONTRIBUTING.md`.
- **Offline equivalent:** `tools/buddy_local_repository.py` provides local build/test/repair/artifact/release/work-queue functions without GitHub.

## GitHub Settings to enable or verify

These settings live in GitHub, not ordinary repository files, so they must be enabled through repository/organization settings or a GitHub API/app with suitable administrative permissions.

### 1. Protect `main`

Use a branch ruleset or branch protection rule. Recommended policy:

- require a pull request for normal collaborative changes;
- require important status checks before merge;
- block force pushes and branch deletion;
- require conversation resolution;
- consider signed commits and linear history when they fit the team;
- require CodeQL/code-scanning results once the workflow has a stable successful baseline;
- use merge queue if change volume becomes high enough to justify it.

Do **not** make a brand-new failing check required before it has successfully run and its stable job name is known.

### 2. Security and supply chain

Verify/enable:

- dependency graph;
- Dependabot alerts/security updates;
- secret scanning;
- push protection;
- CodeQL/code scanning;
- Copilot Autofix or other code-scanning assistance when available/appropriate;
- private vulnerability reporting/security advisories;
- dependency review for pull requests.

Never store provider credentials, private keys, passwords, access tokens, bank information, or production secrets in repository files.

### 3. GitHub Pages

Keep GitHub Pages as a low-friction public Buddy surface. If a custom domain is used, verify the domain in GitHub and configure HTTPS/DNS carefully. The repository workflow should remain the deployment source of truth.

### 4. Releases and tags

Use GitHub Releases for verified distributable versions of Buddy. Release only from a known commit/tag after required checks pass. Attach generated manifests/checksums and clear release notes. Local/offline Buddy can produce equivalent release bundles under `.buddy-local/releases/` before optional GitHub publication.

### 5. Environments and deployments

Use GitHub Environments for production-like deployments that need environment-specific secrets, approvals, URLs, or deployment protection. Keep sandbox/test deployments separate from production.

### 6. Issues, Projects and Discussions

- **Issues:** executable backlog and bug/repair ownership.
- **Projects:** portfolio/roadmap/status tracking when a board view helps.
- **Discussions:** design proposals, community questions, RFCs and ideas that are not yet executable tasks.

Builder bots should work from clearly testable issues rather than treating every discussion as implementation approval.

### 7. Copilot/Agents

Repository custom instructions and custom agents should stay aligned with canonical DreamCo commands. Agent changes are code changes: test them. Organization-level agents may later be placed in the organization's `.github` or `.github-private` repository so the same DreamCo agents can be shared across many repositories.

### 8. Packages/Codespaces/development environments

Use GitHub Packages when DreamCo publishes reusable packages/images. Use Codespaces or equivalent development environments when a reproducible cloud workspace helps, but keep the local/offline path working too.

## Failure policy

Any failed, timed-out, stale or action-required workflow should be visible. Core workflows are captured immediately by `Actions Failure Watch`, while `Actions Failure Sweep` scans recent runs across all workflows. Each failure should produce evidence and a repair issue/path rather than silently disappearing.

## Local-first parity rule

GitHub adds hosted collaboration, security intelligence, cloud runners and distribution. DreamCo should not make those services mandatory for core operation. Buddy locally owns:

- repository inventory;
- test/build execution;
- sandbox generation;
- bot/fleet curricula;
- issue/work queue equivalents;
- repair diagnostics;
- generator factory;
- artifacts;
- release bundles;
- local Pages-equivalent serving;
- optional sync queue.

This is functional parity where practical, not a claim that a laptop recreates GitHub's global hosting, account network, security intelligence, cloud compute or collaboration UI.

## Golden path for a nontechnical owner

1. GitHub online: **Actions → DreamCo Control Center → check-everything**.
2. If red: **Agents → Buddy Debugger → “Fix this failed run.”**
3. Offline/local: `python3 tools/buddy_local_repository.py check`.
4. Local repair: `python3 tools/buddy_local_repository.py repair`.
5. Bot work: `python3 tools/buddy_local_repository.py fleet`.
6. Resource work: `python3 tools/buddy_local_repository.py resources`.
7. Full-potential sandbox: `python3 tools/buddy_local_repository.py sandbox`.
8. Generator registry: `python3 tools/buddy_local_repository.py generate`.
9. Local site: `python3 tools/buddy_local_repository.py serve`.
10. Release bundle: `python3 tools/buddy_local_repository.py package VERSION_NAME`.

The goal is that the user's intent stays simple even when the repository is sophisticated.
