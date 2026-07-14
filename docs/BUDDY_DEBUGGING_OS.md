# Buddy Debugging OS

Buddy Debugging OS is the sellable debugging layer for DreamCo apps, bots, workflows, AI Creation Studio builds, revenue systems, and pull requests.

## Pipeline

1. Capture: collect failing checks, logs, changed files, affected bots, screenshots, and user impact.
2. Reproduce: run the smallest local command that proves the failure.
3. Isolate: classify source bug, config bug, dependency bug, data bug, integration bug, or flaky test risk.
4. Patch: make the smallest reviewed change and preserve rollback notes.
5. Verify: run targeted checks, then broader dashboard, storage, Stripe, bot, and cleanroom checks when affected.
6. Package: prepare a PR summary, client-safe explanation, rollback note, and next action.

## Pull request help

Every pull request should get Buddy help:

- scan goal, changed files, comments, checks, linked issues, and stale risk;
- explain what changed, why it matters, and what could break;
- retest targeted commands and record evidence;
- repair failing gates through supervised operation packets;
- package a merge-ready checklist, rollback note, and client summary.

## Actions and agents failures

The Actions page should show one debug queue for workflow failures, quality gate failures, bot connection issues, storage warnings, payment blockers, and agent runtime problems.

Every failure packet should include:

- source;
- title;
- target;
- evidence;
- route;
- next action;
- retest command or check;
- owner approval state.

The Agents or Bot Overview section should make failing bots easy to inspect by showing heartbeat, workflow status, pending pull requests, dashboard links, prospectus links, and the Buddy debug packet for each failing agent.

## Sellable offers

- Launch Audit: repo, checkout, bot tests, deploy blockers, and dashboard readiness.
- AI App Debug Desk: failures across apps, bots, workflows, APIs, webhooks, and UI.
- Revenue Rescue: Stripe links, offers, webhooks, payment alerts, and revenue evidence.
- Vibe Build QA: games, simulations, videos, courses, image edits, and dashboards.

## Rule

Buddy can prepare fixes, reports, branches, and pull request packets. Merges, deploys, customer outreach, credential changes, and money movement require owner approval.
