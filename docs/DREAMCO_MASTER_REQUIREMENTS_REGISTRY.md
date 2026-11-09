# DreamCo Master Requirements Registry

**Version:** 1.0  
**Created:** 2026-11-08  
**Primary repository:** `DreamCo-Technologies/Dreamcobots`  
**Tracking branch:** `codex/per-conversation-tracking-20261108`

## Purpose

This registry is the source of truth for mapping each project conversation to its own requirements, implementation locations, GitHub issues, pull requests, test runs, evidence, and blockers.

## Conversation inventory

| ID | Conversation | Independent checklist |
|---|---|---|
| CHAT-01 | Daily DreamCo Repository Debug | [Open checklist](conversation-checklists/CHAT-01-daily-dreamco-repository-debug.md) |
| CHAT-02 | Repository Engineering Review 1 | [Open checklist](conversation-checklists/CHAT-02-repository-engineering-review-1.md) |
| CHAT-03 | Repository Engineering Review 2 | [Open checklist](conversation-checklists/CHAT-03-repository-engineering-review-2.md) |
| CHAT-04 | Repository Engineering Review 3 | [Open checklist](conversation-checklists/CHAT-04-repository-engineering-review-3.md) |
| CHAT-05 | Repository Engineering Review 4 | [Open checklist](conversation-checklists/CHAT-05-repository-engineering-review-4.md) |
| CHAT-06 | Repository Engineering Review 5 | [Open checklist](conversation-checklists/CHAT-06-repository-engineering-review-5.md) |
| CHAT-07 | Repository Engineering Review 6 | [Open checklist](conversation-checklists/CHAT-07-repository-engineering-review-6.md) |
| CHAT-08 | DreamCo Lite | [Open checklist](conversation-checklists/CHAT-08-dreamco-lite.md) |
| CHAT-09 | Buddy OS Agent Architecture | [Open checklist](conversation-checklists/CHAT-09-buddy-os-agent-architecture.md) |
| CHAT-10 | DreamCo Bot Revamp | [Open checklist](conversation-checklists/CHAT-10-dreamco-bot-revamp.md) |
| CHAT-11 | DreamCo Pitch and Monetization | [Open checklist](conversation-checklists/CHAT-11-dreamco-pitch-and-monetization.md) |
| CHAT-12 | GitHub and Copilot Setup | [Open checklist](conversation-checklists/CHAT-12-github-and-copilot-setup.md) |
| CHAT-13 | MomMap App Concept | [Open checklist](conversation-checklists/CHAT-13-mommap-app-concept.md) |
| CHAT-14 | Buddy Master Teacher and Benchmarks | [Open checklist](conversation-checklists/CHAT-14-buddy-master-teacher-and-benchmarks.md) |

## Canonical requirement IDs

- **D01** — Consolidate every project conversation
- **D02** — Create master requirements registry
- **D03** — Audit all repositories and branches
- **D04** — Reconcile all open pull requests
- **D05** — Find duplicate bots and implementations
- **D06** — Resolve outstanding CI failures
- **D07** — Complete Buddy OS
- **D08** — Enable builder bot development workflows
- **D09** — Validate all 45 divisions
- **D10** — Implement 50 command centers
- **D11** — Complete Buddy learning and benchmark system
- **D12** — Connect monetization infrastructure
- **D13** — Update and validate GitHub Pages
- **D14** — Complete final integration testing

## Required traceability record

For every CHAT-ID × requirement-ID pair, record:

| Field | Meaning |
|---|---|
| Conversation source | Original chat URL, title, date, and message reference |
| Requirement | Canonical D01–D14 requirement |
| Scope | Exact request and acceptance criteria from that chat |
| Repository | Repository owner/name |
| Implementation | File paths, components, services, or workflows |
| Issue | GitHub issue URL and number |
| Pull request | PR URL, branch, base, and status |
| Tests | Exact commands/workflows and run URLs |
| Evidence | Logs, artifacts, screenshots, or test reports |
| Status | Not started / in progress / blocked / ready for review / verified |
| Blocker | Dependency, conflict, permission, or owner action |
| Shared work | Other CHAT-ID records supported by the same implementation |

## Completion rules

- A shared implementation may satisfy more than one conversation only when it demonstrably covers each conversation's acceptance criteria.
- Never infer completion from a PR title, branch name, generated file, or prior approval alone.
- A merged PR is not automatically a passing test; preserve test evidence separately.
- Keep PRs with conflicts or security implications out of automatic merge paths.
- Do not weaken tests to obtain green CI.
- Preserve branch protections, authorization, audit logging, telemetry, and rollback evidence.
- Cloudflare remains disconnected from the active build path until separately reauthorized.
- Record unknowns as **unverified**, not complete.

## Initial repository audit snapshot

The authenticated GitHub connection returned five repositories under the DreamCo-Technologies organization:

- `DreamCo-Technologies/Dreamcobots` (primary; default branch `main`)
- `DreamCo-Technologies/Ai-bots`
- `DreamCo-Technologies/Dreamco`
- `DreamCo-Technologies/demo-repository`
- `DreamCo-Technologies/DreamCo-Command-Center`

A branch-health report found in the primary repository reports 476 branches, 64 open PRs, 28 conflicts, and many blocked branches. These are a dated report snapshot, not a fresh full PR/branch audit. Re-run the audit and record its run time before making changes.

## Work queue

1. Reconcile all 14 conversations against their original source messages.
2. Inventory all five repositories, default branches, branches, and open PRs.
3. Map existing issues and PRs to CHAT-ID × D01–D14.
4. Identify exact duplicate requests and duplicate implementations.
5. Create only missing issues/PRs after duplicate checks.
6. Inspect failing CI jobs and repair root causes without weakening gates.
7. Validate Buddy OS, builder workflows, 45 divisions, and 50 command centers.
8. Validate learning/benchmark and monetization paths.
9. Validate GitHub Pages alongside repository changes.
10. Run final integration, security, and regression tests.

## Current status

All 196 conversation-requirement pairs are **unverified / not yet reconciled**. This registry and the per-conversation checklists are tracking artifacts; they do not assert that the underlying product work is complete.


## Tracking artifacts created in this change

- Tracking issue: [#17172](https://github.com/DreamCo-Technologies/Dreamcobots/issues/17172)
- Documentation pull request: [#17173](https://github.com/DreamCo-Technologies/Dreamcobots/pull/17173) (draft; not merged)
- Tracking branch: `codex/per-conversation-tracking-20261108`
- Checklist file verification: fetched successfully from the tracking branch after creation.
- Registry file verification: fetched successfully from the tracking branch after creation.


## Per-conversation file verification

All 14 independent checklist files were fetched successfully from the tracking branch after creation. Each contains its own 14 unchecked requirements and traceability fields.
