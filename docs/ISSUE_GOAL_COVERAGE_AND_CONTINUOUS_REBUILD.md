# Issue Goal Coverage and Continuous Rebuild System

This document maps the current open issue themes to repository evidence and automation. It exists so DreamCo bots do not guess whether a goal is complete; they must point to files, workflows, and reports.

## Scanned issue themes

- `#428 Massive update`: 45 dynamic divisions, config-as-code, bot registry, self-healing, Kubernetes, KEDA, Argo Rollouts, Helm, CI/CD validation, living AI divisions.
- `#427 Buddy`: Buddy model routing, top-model task selection, coding/fixing/PR workflows.
- `#426 Update`: AI coding-agent governance and repository maintenance options.
- `#425 Update`: lead generation, client discovery, sales, pricing, KPI, and continuous improvement systems.
- `#424 Update`: deployment options and GitHub-based dashboard delivery.
- Older open PRs: CI self-healing, bot test failures, GlobalAISourcesFlow compliance, lead bots, self-building automation, and repository activity tracking.

## Added coverage

- `config/divisions.json`: 45-division registry for dynamic home/dashboard buttons.
- `config/bot_registry.json` and `registry/bots.json`: central bot self-registration contract and starter records.
- `config/scaling.yaml`, `config/upgrade_rules.yaml`, `config/thresholds.yaml`, `config/task_queues.yaml`, `config/feature_flags.yaml`: configuration-as-code foundation.
- `kubernetes/`: deployment, service, HPA, KEDA scaler, network policy, and disruption budget.
- `argo/`: rollout, analysis template, and rollback policy.
- `helm/dreamco/`: chart metadata and values.
- `automation-tools/agents/issue-goal-coverage.js`: evidence scanner that compares issue goals to files/checks.
- `.github/workflows/dreamco-continuous-self-build.yml`: scheduled six-hour audit workflow.
- `.github/workflows/dreamco-debug-audit.yml`: now includes issue goal coverage.
- `npm run scan:issues`: local and CI command for coverage reporting.
- `npm run debug:all`: now includes issue coverage, dependency audit, metadata planning, missing-file scan, sandbox no-hallucination audit, and Buddy connectivity.

## What this does not honestly claim

- It does not prove production is deployed.
- It does not prove every bot is healthy.
- It does not prove secrets, Stripe, outreach, Kubernetes, Argo, or Helm are live in a real cluster.
- It does not close GitHub issues automatically.

Those actions require live credentials, infrastructure, workflow runs, and green reports.

## Commands

```bash
npm run scan:issues
npm run sandbox:no-hallucinations
npm run debug:all
```

## Reports

The audits write evidence to:

- `reports/issue-goal-coverage.json`
- `reports/issue-goal-coverage.md`
- `reports/sandbox-hallucination-audit.json`
- `reports/sandbox-hallucination-audit.md`
- `reports/bot-health-report.json`
- `reports/buddy-connectivity-report.json`

DreamCo bots should cite these reports instead of saying everything is fixed without proof.
