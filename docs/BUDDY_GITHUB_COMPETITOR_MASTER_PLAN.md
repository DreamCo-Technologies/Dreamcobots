# Buddy vs GitHub — Master Competition Plan

## North star

Buddy should eventually be able to replace GitHub as the human-facing open-source development platform while remaining interoperable with GitHub during the transition.

The target is not to copy GitHub's UI. The target is to match the full developer lifecycle with a dramatically simpler experience and stronger evidence-driven reliability.

## Benchmark categories

| Category | GitHub capability to match | Buddy target | Exit evidence |
|---|---|---|---|
| Source control | repositories, branches, commits, history | Plain-language version control plus advanced Git compatibility | round-trip repo tests |
| Collaboration | pull requests, reviews, discussions | Buddy proposals, council reviews, human approval | multi-user workflow suite |
| Planning | issues, projects, roadmap | outcome-driven plans and automatic work breakdown | planning benchmark |
| AI coding | Copilot, agent mode, code review | Personal Coding AI + Council + multi-model routing | coding benchmark suite |
| CI/CD | Actions, runners, workflow visualization | Reliability Pipeline + council gates + self-healing | 30-day CI reliability evidence |
| Environments | Codespaces | one-click Builder Workspace | cold-start + reproducibility tests |
| Packages | GitHub Packages | DreamCo Package Registry | publish/install/security tests |
| Web hosting | Pages | Buddy Publish | deploy/rollback/health tests |
| Security | code scanning, secret scanning, Dependabot, security policies | security council + supply-chain scanning + repair gates | security certification suite |
| Ecosystem | Marketplace, APIs, webhooks | DreamCo Open Source Marketplace + APIs + events | marketplace/API contract suite |
| Community | discussions, profiles, social/community | beginner-first open-source community | moderation + collaboration suite |
| Education | docs, education resources | Buddy teaches while building | beginner completion benchmark |
| Mobile | GitHub Mobile | Buddy mobile-first development control | mobile task completion suite |
| Enterprise | teams, permissions, audit, policies | council-governed organizations | enterprise control suite |
| Observability | insights, workflow status | one health center with root-cause explanations | incident benchmark |
| Portability | Git CLI/API | Git-compatible import/export initially | 100% fixture round-trip target |

## GitHub parity inventory

GitHub currently combines code experiences, planning, code-to-cloud DevOps, collaboration, security/compliance, client apps, enterprise administration, communities, ecosystem/API capabilities, learning, and insights. The public GitHub roadmap organizes these as major feature areas. Buddy's parity program must cover every area rather than focusing only on AI coding.

## Reliability advantage

Buddy's differentiator is the Council Reliability Layer.

Every consequential automated change should be eligible for independent checks such as:

- architecture review
- security review
- test review
- performance review
- compliance review
- product/value review
- rollback review

No single bot should be the sole authority for production promotion.

## Council decision model

```text
User intent
   -> planner
   -> implementation
   -> isolated test
   -> council review
       -> security
       -> architecture
       -> tests
       -> performance
       -> compliance
       -> value
   -> human approval when required
   -> publish
   -> monitor
   -> rollback or repair if needed
```

The council must produce evidence, not merely votes.

## Reliability benchmarks

### R1 — Build reliability

- reproducible builds
- deterministic validation where possible
- no silent test bypasses
- rollback after failed release

### R2 — Change reliability

- every generated change has a diff
- affected tests identified
- council evidence attached
- human approval policy enforced

### R3 — Repair reliability

- detect failure
- identify root cause
- propose smallest safe fix
- run regression tests
- require escalation when confidence is insufficient

### R4 — Security reliability

- secrets never committed
- dependency risk surfaced
- unsafe generated code blocked
- permission boundaries tested

### R5 — Beginner reliability

- a beginner can recover from common errors without reading logs
- advanced logs remain available
- no important action is hidden

## Performance targets

Targets are product goals, not claims of current performance.

- first useful action: under 60 seconds for a prepared environment
- beginner onboarding completion: under 10 minutes for the first Personal AI
- common code-change feedback: under 2 minutes where infrastructure permits
- health check: under 1 second for local service health target
- rollback initiation: under 60 seconds after an approved rollback
- no silent loss of user work

Actual measurements must be stored in benchmark artifacts.

## Compatibility strategy

Do not abandon GitHub before DreamCo has equivalent export/import coverage.

### Stage A

GitHub is infrastructure.

### Stage B

Buddy is the primary interface and GitHub is a backend connector.

### Stage C

DreamCo supports native repositories while retaining Git compatibility.

### Stage D

Users can migrate projects entirely to DreamCo without losing history, issues, releases, packages, CI definitions, or collaboration records.

### Stage E

Buddy becomes a general open-source interface that can connect to GitHub, GitLab, Bitbucket, self-hosted Git, and DreamCo repositories.

## Certification gates

Buddy is not declared "GitHub replacement ready" until all of these pass:

1. source-control parity
2. collaboration parity
3. planning parity
4. AI coding parity
5. CI/CD parity
6. environment parity
7. package parity
8. publishing parity
9. security parity
10. ecosystem/API parity
11. community parity
12. education/beginner parity
13. mobile parity
14. enterprise governance parity
15. observability parity
16. import/export parity
17. reliability certification
18. cost-efficiency certification

## Current DreamCo reality

This repository already contains substantial infrastructure for the direction, including Buddy success/governance systems, benchmark tracking, model progress tooling, local repository integration, self-repair tooling, and dedicated Buddy pages. The generated success program currently reports 1,051 routed profiles, 45 divisions, 500 model benchmark targets, and 360 daily logical benchmark slots; however it also reports 0 production-ready divisions and 0 verified live resource hosts, so these counts are planning/inventory signals rather than proof of production readiness.

A recent Run Everything report recorded 40/44 top-level checks passed, while the production verification section still reported failed checks and marked the run not production-ready. The failure included a stale generated Buddy success program and a production runtime smoke failure. Treat this as the current blocking evidence until a newer clean certification run proves otherwise.

## Definition of "done"

The goal is not "we have a page that looks like GitHub."

Done means a real user can:

- create/import a project;
- edit code;
- use an AI coding agent;
- manage history;
- collaborate;
- plan work;
- run tests;
- deploy;
- monitor;
- secure the project;
- publish packages;
- document the project;
- invite contributors;
- resolve failures;
- roll back safely;
- export everything;
- and understand what happened without being an expert.

## Immediate priority

Before adding dozens of new features, make the certification loop trustworthy:

1. eliminate stale generated artifacts;
2. repair production runtime smoke;
3. make Run Everything clean;
4. certify current council gates;
5. build a single Buddy Platform Readiness dashboard;
6. then implement parity category-by-category.

This prevents DreamCo from confusing feature inventory with working capability.
