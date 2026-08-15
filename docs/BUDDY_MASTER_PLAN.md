# Buddy Master Plan

This document is the single beginner-friendly index for the Buddy platform direction.

## North star
Build a dependable, teachable, extensible AI system that can coordinate specialist agents, help users build software and businesses, learn from evidence, and operate across approved devices and services while keeping users in control.

## Core systems

1. **Beginner-first experience** — plain language, safe defaults, Teach Me, guided recovery.
2. **Developer copilot** — repository understanding, intelligent suggestions, code review, tests, PR guidance and optional implementation.
3. **Agent routing** — select specialist agents by task, allow multiple agents per step, verify outputs before promotion.
4. **Actions control center** — every workflow has purpose, status, history, diagnostics, progress, benchmarks and safe actions.
5. **Benchmark/Bootcamp** — sandbox tasks, repeatable evaluations, quality/speed/correctness/safety metrics, regression suites and evidence-based mastery.
6. **Navigation** — voice-first, route choices, safe driving interaction, transportation planning and user-approved integrations.
7. **Device Center** — discover visible/authorized devices through supported OS, Bluetooth/BLE, USB, LAN and vendor APIs; discovery never grants control.
8. **Download Center** — real platform builds, release verification, installation guidance and approved app-store distribution where required.
9. **Business intelligence** — approved data connections, custom dashboards, opportunity research, lead generation and workflow automation.
10. **Learning system** — failures become diagnoses, fixes, regression tests and lessons.
11. **Observability** — health, latency, cost, reliability, errors and capability drift are tracked.
12. **Governance** — permissions, audit logs, approval policies, rollback and explicit separation between facts, estimates and simulations.

## Capability lifecycle

`Idea → Prototype → Sandbox → Tested → Reproducible → Reliable → Production → Monitored → Improved`

## Definition of done

A feature is not complete because code exists. It should have:

- understandable UX
- implementation
- tests
- error handling
- observability
- documentation
- permissions/security review when applicable
- recovery/rollback path when applicable
- benchmark evidence
- regression coverage
- clear limitations

## Mastery policy

Buddy should never label a capability "mastered" based on a single benchmark. Mastery requires repeated passing results against the repository's defined correctness, quality, speed, safety and reliability thresholds, plus regression stability.

## Beginner promise

A new user should be able to:

`Install Buddy → connect a project → understand its health → fix one problem → build one useful thing → learn why it worked`

without first becoming a GitHub expert.

## Long-term engineering principle

Prefer measurable, reversible, reliable progress over feature-count growth. A smaller system that can explain itself, recover from failures, protect user permissions and demonstrate improvement is a stronger foundation for future capability than a large collection of unverified features.

## Related standards

- `docs/BEGINNER_FIRST_REPOSITORY_STANDARD.md`
- `docs/BUDDY_BEGINNER_ONBOARDING.md`
- `docs/BUDDY_BEGINNER_UI_CHECKLIST.md`
- `docs/BUDDY_GITHUB_TRANSLATOR.md`
- `docs/BUDDY_PARENTING_AND_MASTERY_CHARTER.md`
- `docs/BUDDY_DEVICE_CENTER_UX.md`
- `docs/BUDDY_DEVICE_DISCOVERY_ROADMAP.md`
- `docs/BUDDY_UNIVERSAL_DEVICE_CONTROL.md`
- `docs/BUDDY_DOWNLOAD_CENTER_SPEC.md`
