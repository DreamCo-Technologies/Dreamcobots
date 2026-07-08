# Dashboard and Command Center Tracking Map

DreamCo should have two polished control surfaces:

- **Command Center:** operator cockpit for actions, agents, commands, model routing, MCP tools, GitHub, deployments, and approvals.
- **Dashboard:** business cockpit for revenue, customers, leads, sales, KPIs, learning progress, bot performance, and daily review.

## Put it in Command Center

| Area | Track | Source files / systems |
| --- | --- | --- |
| Actions | tasks, blockers, owners, approvals, evidence | GitHub Issues, Actions, `reports/*.md` |
| Agents | bot modes, permissions, abilities, memory policy | `bot.control.json`, `config/buddy-mcp-tool-registry.json` |
| MCP Tools | GitHub, web research, Stripe, External Builder, local commands | `config/buddy-mcp-tool-registry.json` |
| Model Router | provider toggles, task routes, cost/quality mode | `config/buddy-model-router.json` |
| Commands | scan, build, test, repair, revenue report | `package.json`, GitHub Actions |
| Missing Files | broken imports, missing metadata, dependency gaps | `reports/bot-health-report.md`, `reports/dependency-audit-report.md` |
| Buddy Tests | registry validation, routing validation, safe command checks | `automation-tools/agents/buddy-connectivity-test.js` |
| GitHub Ops | PRs, branches, workflows, issue lanes | GitHub connector and Actions |
| Production | deployment readiness, secrets checklist, incidents | `docs/*`, workflows, reports |

## Put it in Dashboard

| Area | Track | Source files / systems |
| --- | --- | --- |
| Revenue | Stripe events, bot revenue, failed payments, payouts | `data/stripe/*.json`, `reports/stripe-revenue-report.md` |
| Sales | leads, pipeline, outreach, follow-ups, close rate | `docs/SALES_REP_BOT_TEAM.md`, future CRM JSON |
| Customers | segment, problem, solution, validation status | future `data/customers/*.json` |
| Offers | product, price, payment link, owner bot | `data/stripe/offers.template.json` |
| KPIs | daily sales, conversion, MRR, churn, response time | Stripe reports, sales reports |
| Learning | bot weekly goals, source extraction, evidence | `docs/BOT_TRACKING_LEARNING_SYSTEM.md` |
| Workflows | problem to customer to MVP to pricing to sales | `docs/SALES_REP_BOT_TEAM.md` |
| Web Research | public source findings and client discovery logs | future `reports/client-discovery-report.md` |
| Bot Results | which bots made money, saved time, or completed goals | bot summaries and revenue ledger |

## Both chat sections should show

- Current user request.
- Active bot/agent.
- Mode toggle: Observe, Diagnose, Draft, Build, Test, Command, Autopilot, Locked.
- Tool toggles: GitHub, web research, Stripe, model router, local command, External Builder if verified.
- Context panel: selected repo files, reports, customer/offer, current workflow stage.
- Output panel: answer, files changed, tests run, revenue impact, next action.
- Safety panel: approval required, risk level, command permission, privacy note.

## Daily operator flow

1. Open Command Center.
2. Review failed scans, missing files, broken builds, pending PRs.
3. Run Buddy connectivity test.
4. Open Dashboard.
5. Review Stripe revenue, failed payments, leads, sales actions, customer validation.
6. Pick the top action for each sales rep bot.
7. Approve only the actions that are ready.
8. End day with KPI review and learning update.

## Design standard

Both surfaces should feel like serious operator tools: dense, clean, fast, readable, no decorative clutter. Use cards only for repeated items, clear toggles for modes/tools, tables for tracking, and status pills for risk/health. The first screen should be the working dashboard, not a marketing hero.
