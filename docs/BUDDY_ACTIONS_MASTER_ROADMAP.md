# Buddy Actions Master Roadmap

## Mission

Turn the Actions page into Buddy's operating system: every important DreamCo goal becomes an explicit action with a clear purpose, prerequisites, execution path, proof, failure path, owner and next step.

## Operating rule

**Observe before changing. Prove before claiming. Repair before expanding.**

A button may be READ-ONLY, LOCAL, or REMOTE. Its UI must clearly state which one applies.

## Master action lanes

### A. Foundation / Green
Goal: trustworthy repository and runtime.

Path: Doctor -> dependencies -> lint/type -> tests -> build -> runtime smoke -> generated artifacts -> certification.

Proof: required checks pass and current runtime evidence agrees with static evidence.

Failure: create/link canonical incident; fingerprint; reproduce; repair; regression-test; escalate if blocked.

### B. Issues
Goal: every issue gets worked, not forgotten.

Path: intake -> deduplicate -> severity -> owner -> reproduce -> repair -> test -> Council if needed -> verify -> close/reopen on regression.

### C. Actions
Goal: every failed workflow becomes actionable engineering work.

Path: detect -> fingerprint -> group -> classify transient/deterministic -> safe retry -> reproduce -> repair -> rerun targeted checks -> verify.

### D. Agents
Goal: every failed Buddy run becomes evidence and learning.

Path: run ID -> failure classification -> retry policy -> sandbox -> repair/evaluation -> benchmark -> Council -> verified outcome -> learning record.

### E. Buddy Intelligence
Goal: make Buddy demonstrably smarter over time.

Path: benchmark baseline -> task evaluation -> compare model/tool route -> improve -> regression suite -> promote only when quality/reliability/cost improve.

### F. Personal AI Product
Goal: users can build personalized assistants with explicit data/rights controls.

Path: create -> consent -> import permitted sources -> index/memory -> train/evaluate -> personalize -> benchmark -> publish/use -> export/delete/reset.

### G. GitHub Parity
Goal: progressively cover GitHub's important developer lifecycle without losing beginner simplicity.

Path: capability inventory -> gap -> priority -> implementation -> sandbox -> compatibility test -> usability test -> security -> performance -> certify.

Lanes: source control, collaboration, Issues, planning, AI coding, CI/CD, environments, packages, publishing, security, APIs, community, education, mobile, enterprise, observability, migration, reliability, cost.

### H. Beginner Experience
Goal: a non-developer can accomplish real work.

Path: plain-language goal -> guided plan -> one-click safe action -> explain result -> recover on failure -> teach only what is needed -> measure completion.

### I. Security / Trust
Goal: protect code, data, identities and user memory.

Path: scan -> classify -> least-privilege review -> patch -> rescan -> Council -> release gate -> monitor.

### J. Deployment / Operations
Goal: reliable releases and fast recovery.

Path: build -> artifact -> security -> smoke -> canary -> health -> release -> monitor -> rollback if necessary -> post-incident learning.

### K. Revenue / Business
Goal: turn validated capabilities into sustainable products.

Path: hypothesis -> market validation -> unit economics -> prototype -> user test -> conversion -> retention -> support burden -> scale.

### L. Observability
Goal: Buddy can explain what is happening.

Path: telemetry -> incident correlation -> dashboard -> alert -> diagnosis -> evidence -> action -> verification.

## Action card standard

Every Actions-page control should expose:

- **Goal:** what outcome this creates.
- **Why:** why the user should care.
- **Prerequisites:** what must already be true.
- **Execution:** exactly what happens after click.
- **Permissions:** what it can access/change.
- **Evidence:** where results come from.
- **Success:** measurable pass condition.
- **Failure:** what happens next.
- **Rollback:** how to undo a consequential change.
- **Owner:** which service/agent/team owns it.
- **Related queue:** Issue / Action / Agent.
- **Next action:** what Buddy recommends afterward.

## Green/yellow/red truth model

**GREEN — Verified:** current evidence meets the required gate.

**YELLOW — Working/blocked:** active work or a non-critical blocker exists.

**RED — Failed:** a required gate is currently failing.

**GRAY — Unknown:** evidence is missing or stale; never invent a green result.

## Parent rules

1. Protect user work.
2. Fix critical foundations before new features.
3. Never close work without evidence.
4. Never let a bot certify its own consequential production change.
5. Prefer the smallest reversible repair.
6. Add regression protection after repairs when practical.
7. Bound retries and escalate repeated failures.
8. Consolidate capabilities into shared services instead of creating bot sprawl.
9. Keep Issues, Actions and Agents distinct for humans.
10. Teach beginners without hiding expert controls.
11. Optimize quality, reliability and cost together.
12. Treat privacy, consent and deletion as product features.

## End-state

The Actions page should answer, at any moment:

- What is Buddy responsible for?
- What is healthy?
- What is failing?
- What is being repaired?
- What is waiting for me?
- What did the Council approve/reject?
- What evidence proves the result?
- What should happen next?

No goal is considered complete merely because an Action exists. It is complete only when the defined outcome is verified.
