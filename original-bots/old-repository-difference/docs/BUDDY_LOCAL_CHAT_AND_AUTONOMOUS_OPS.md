# Buddy Local Chat and Semi-Autonomous Operations

Buddy can be run as a local command center for testing DreamCo bots, workflows, customer discovery plans, tool discovery, skill discovery, and social content drafts.

## Local UI

```bash
cd dreamco-control-tower/frontend
npm install
npm run dev
```

Open the Vite URL and launch `Buddy Command Center` from the Actions page.

## Local audit commands

From the repository root:

```bash
npm run autonomous:readiness
npm run scan:issues
npm run sandbox:no-hallucinations
npm run debug:all
```

## Operating modes

- `observe`: read reports, summarize state, no writes.
- `diagnose`: inspect failures, propose fixes, no writes.
- `draft`: create plans, outreach drafts, social drafts, and tool ideas.
- `build`: create code/config/docs after approval.
- `test`: run sandbox-safe checks and write reports.
- `command`: dispatch approved workflows.
- `autopilot`: limited to read-only research, report generation, and queued drafts.
- `locked`: no external actions.

## Customer discovery loop

Buddy should route customer discovery through `config/autonomous_business_engine.json`:

1. Define the problem.
2. Identify the customer.
3. Research public sources.
4. Create an MVP offer.
5. Validate with a real customer after approval.
6. Draft pricing.
7. Build repeatable sales process.
8. Measure KPIs.
9. Review daily.
10. Improve the system.

## Social media connector rule

Use `config/social_connectors.template.json` as the template. Social actions default to draft-only. Posting, commenting, messaging, and ad spend require approval and platform secrets that must not be committed to Git.

## Tool and skill discovery rule

Use `config/tool_skill_discovery.json`. ToolFinder and SkillFinder may research public sources such as GitHub, Wikipedia, official docs, and package registries. They must store source URLs, confidence, usable knowledge, and next experiments. They must not claim learned facts without sources.

## Set-it-and-check-it rule

DreamCo should aim for scheduled audits and queued drafts, not uncontrolled forever-running bots. The safe loop is:

```text
research -> draft -> test -> report -> request approval -> execute approved action -> measure -> learn -> repeat
```

This keeps the system close to set-it-and-forget-it while still protecting money, customers, accounts, and deployments.
