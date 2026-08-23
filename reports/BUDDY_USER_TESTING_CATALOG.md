# Buddy User Testing Catalog

Generated as the handoff from repository/sandbox verification to real human testing.

## Truth rules

- **SANDBOX_PASS** = repository-controlled test passed; does not prove real-world usability.
- **REPO_VERIFIED** = repository contracts/checks passed.
- **USER_TEST_REQUIRED** = a real person should exercise the flow.
- **LIVE_PROVIDER_REQUIRED** = an authenticated external service/provider must be tested.
- **PRODUCTION_REQUIRED** = deployment/production behavior must be verified.
- **BLOCKED** = required dependency, credential, environment, or evidence is missing.

A pass in one environment is never promoted to another environment automatically.

## Already sandbox/repository verified

| Area | Current evidence | Status | Human testing? |
|---|---|---|---|
| Bot fleet profiles | 1,051/1,051 certified | SANDBOX_PASS | Yes |
| Bot capability contracts | 8,408/8,408 certified | SANDBOX_PASS | Yes |
| Bot divisions | 45 covered | REPO_VERIFIED | Yes |
| Buddy governance contracts | automated tests | REPO_VERIFIED | Yes |
| Preventive engineering contracts | automated tests/workflow | REPO_VERIFIED | Yes |
| Mastery ledger | automated contract tests | REPO_VERIFIED | Yes |
| Mastery gap planner | contract tests | REPO_VERIFIED | Yes |
| Agent mode contract | contract tests | REPO_VERIFIED | Yes |
| Dashboard health contract | contract tests | REPO_VERIFIED | Yes |
| Benchmark contract | contract tests | REPO_VERIFIED | Yes |
| Recovery contract | contract tests | REPO_VERIFIED | Yes |
| Audit event contract | schema/tests | REPO_VERIFIED | Yes |
| Skill registry contract | contract tests | REPO_VERIFIED | Yes |
| Debate output contract | schema/tests | REPO_VERIFIED | Yes |
| AGI-like Actions model | schema + behavior cases | REPO_VERIFIED | **Priority** |

## User testing campaign

### P0 — Start here

1. **Buddy Actions** — give Buddy a real goal; inspect plan, model, tools, memory, risk, progress, evidence, recovery and next-best-action.
2. **Bot control** — select a bot, run a safe sandbox action, inspect output and evidence.
3. **Dashboard selection** — open dashboards, test navigation, verify health/status and report broken routes.
4. **Debugging** — intentionally introduce a safe test failure and verify detection, diagnosis, repair, verification and learning.
5. **Buddy Bootcamp** — select a skill, baseline it, train, run sandbox tests, review score and retry.
6. **Benchmark center** — run a benchmark and confirm the result is evidence-backed and recorded in the mastery ledger.
7. **Memory/context** — create a project/instruction/document context and verify Buddy uses it without leaking unrelated context.
8. **Debate team** — submit a non-destructive architecture decision and inspect positions, dissent, decision, risks and evidence requirements.

### P1 — Integrations and real-world workflows

9. MCP/tool connection flows.
10. GitHub repository actions.
11. CI workflow monitoring.
12. External API adapters.
13. Authenticated provider sandbox flows.
14. Deployment and rollback flows.
15. Observability and incident workflows.
16. Revenue/product workflows where configured.

### P2 — Scale and resilience

17. Multi-bot orchestration.
18. Multi-step autonomous Actions.
19. Cross-dashboard workflows.
20. Capability transfer between bots/models.
21. Regression after repository changes.
22. Recovery after dependency failure.
23. Concurrent tasks and queue behavior.
24. Long-running task continuation.

## Human acceptance template

For every test record:

- Tester:
- Date:
- Environment:
- Capability:
- Goal:
- Starting state:
- Steps:
- Expected result:
- Actual result:
- Pass/Fail:
- Evidence link/artifact:
- UX issues:
- Reliability issues:
- Safety issues:
- Confusing behavior:
- Suggested improvement:
- Reproducible?:
- Follow-up issue:

## User-test status vocabulary

- NOT_STARTED
- IN_PROGRESS
- PASS
- PASS_WITH_ISSUES
- FAIL
- BLOCKED
- NEEDS_REGRESSION
- NEEDS_LIVE_PROVIDER_TEST
- NEEDS_PRODUCTION_TEST

## What users should NOT test with real destructive data

Use sandbox/test accounts for destructive, financial, credential, security, production, or irreversible operations unless the workflow explicitly requires a controlled production test and has approval/rollback evidence.

## Completion rule

A capability becomes **USER_VERIFIED** only after the required human acceptance test passes and evidence is recorded. A capability becomes **LIVE_VERIFIED** only after its external provider flow passes with evidence. A capability becomes **PRODUCTION_VERIFIED** only after deployment health and production evidence pass.
