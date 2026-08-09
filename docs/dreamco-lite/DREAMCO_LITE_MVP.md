# DreamCo Lite — Locked MVP

## Decision

DreamCo Lite is the required first shipping target before any repo-wide Lite System, recursive builder network, full multi-agent platform, or Buddy mega-orchestrator expansion.

The MVP is intentionally small:

- **2 bots**
- **1 UI**
- **5-day build cycle**
- **1 proven workflow:** leads → outreach messages → usable output

The goal is not to prove that DreamCo can contain hundreds of bots. The goal is to prove that one small DreamCo product can create useful, actionable results for a real user.

## Core Bots

### Money Bot v1

Purpose: produce immediate user value.

Inputs:

- target niche
- target location

Outputs:

- relevant leads
- business/contact information when available
- personalized outreach messages
- copy-ready or export-ready results

Initial workflow:

1. User enters niche and location.
2. User selects **Find Leads**.
3. Money Bot returns a small lead set.
4. User selects **Generate Messages**.
5. Money Bot generates outreach for the selected leads.
6. User can select **Run Automation** to perform the proven sequence in one action.

### Debug Bot v1

Purpose: support the MVP during early development and testing.

Inputs:

- error message
- log output
- failed task context

Outputs:

- plain-English explanation
- likely root cause
- suggested next fix

Debug Bot v1 is intentionally simple. It is not a self-repairing autonomous platform, a repo-wide repair service, or a recursive builder.

## Single-Page UI

The Lite UI contains only what is necessary to prove the workflow.

Required controls:

- niche input
- location input
- **Find Leads** button
- **Generate Messages** button
- **Run Automation** button
- output panel for leads, generated messages, and errors

Not part of the locked MVP:

- drag-and-drop workflow builder
- recursive bot creation
- autonomous builder fleets
- multi-agent debate systems
- Kubernetes or distributed orchestration
- global repo scanning
- automatic Lite Systems attached to every bot
- advanced client dashboards
- predictive auto-scaling
- full Buddy orchestration

## Five-Day Build Cycle

### Day 1 — UI skeleton

Acceptance target:

- single page loads
- niche and location can be entered
- all three action buttons render
- output panel can display mock results

### Day 2 — Lead engine

Acceptance target:

- **Find Leads** returns a usable lead list from one source
- if an external lead source blocks progress, the UI/backend contract may be validated with mock data first rather than delaying the entire MVP

### Day 3 — Message engine

Acceptance target:

- **Generate Messages** converts returned leads into usable outreach copy
- messages use the lead/business/niche context and are not generic placeholders

### Day 4 — Debug Bot

Acceptance target:

- failed MVP operations can send error/log context to Debug Bot
- Debug Bot returns a readable explanation and a suggested corrective action

### Day 5 — Connect, test, deploy

Acceptance target:

- **Run Automation** executes the validated leads → messages sequence
- outputs are visible in the UI
- the deployed MVP can be tested by a real person outside the development path

## MVP Exit Criteria

DreamCo Lite is considered validated only when a real user can:

1. enter a niche and location;
2. obtain real or operationally usable leads;
3. generate outreach worth sending;
4. act on the output without needing to understand DreamCo internals.

Shipping comes before polishing. A working, limited MVP is preferred over a sophisticated unfinished platform.

## Scope Lock Rule

Until the MVP exit criteria are met, do not expand the build because a feature is interesting. New work must directly improve the leads → messages → action workflow or remove a blocker preventing that workflow from working.
