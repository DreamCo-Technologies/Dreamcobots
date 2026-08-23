# Buddy User Testing Catalog

Purpose: give human testers one authoritative catalog of what has repository/sandbox evidence and what still requires real-user, live-provider, or production validation.

## Truth rules

- **PASS-SANDBOX** = repository-controlled sandbox evidence exists; not a production claim.
- **PASS-REPO** = repository contract/static evidence exists.
- **READY-USER** = a human can test the capability using the documented flow.
- **NEEDS-LIVE** = requires a real provider, credential, device, external service, or deployment.
- **BLOCKED** = prerequisite is missing.
- **MASTERED** = only after the mastery evidence lifecycle requirements are satisfied; sandbox success alone is insufficient.

## Current verified baseline

| Area | Current evidence | User test status | What to test next |
|---|---|---|---|
| Bot fleet | 1,051/1,051 sandbox certified; 8,408/8,408 declared capability contracts | READY-USER | Select representative bots and execute real workflows |
| 45 divisions | Repository coverage exists | READY-USER | Test one primary workflow per division |
| Buddy Actions | Architecture/contracts built | READY-USER | Goal → plan → tool → execution → evidence → learning |
| Debugging | Preventive/recovery/incident contracts built | READY-USER | Introduce controlled failures and verify diagnosis/recovery |
| Benchmarks | 40 benchmark surfaces tracked; live benchmark evidence still required | READY-USER | Run baseline and collect evidence per capability |
| Bootcamp | Training/sandbox architecture built | READY-USER | Choose capability → baseline → lesson → sandbox → retest |
| Skills | Skill registry and gap planning contracts built | READY-USER | Test skill acquisition and capability-gap recommendations |
| Memory | Projects/documents/instructions/memory contracts in architecture | READY-USER | Test persistence, retrieval, provenance and user controls |
| Debate team | Structured debate decision contract built | READY-USER | Give hard architecture decisions and inspect dissent/evidence |
| Models | Routing/benchmark infrastructure exists | NEEDS-LIVE | Compare configured models on the same tasks |
| MCP/tools | Tool contract architecture exists | NEEDS-LIVE | Connect authorized MCPs and test real calls |
| Dashboards | Health contract exists | NEEDS-LIVE | Browser/API/auth/data smoke tests against deployed dashboards |
| GitHub automation | CI/preventive gates exist | READY-USER | Make controlled PRs and observe gates/repair flows |
| External integrations | Adapters/contracts may exist by subsystem | NEEDS-LIVE | Authenticate and run provider-specific smoke tests |
| Production deployment | Evidence required by release policy | NEEDS-LIVE | Deploy canary, verify health, rollback test |
| Creative AI | Contracts/benchmark architecture exist | NEEDS-LIVE | Run real rendering/generation providers |
| Security | Defensive sandbox architecture exists | NEEDS-LIVE | Authorized security scenarios only |
| Financial/revenue actions | Governance architecture exists | NEEDS-LIVE | Test with non-production/sandbox accounts first |

## Human testing sequence

### Phase 1 — Safe repository/sandbox testing

1. Pick a capability from the catalog.
2. Record baseline.
3. Run the sandbox test.
4. Record expected vs actual result.
5. Capture evidence.
6. Record failures.
7. Run recovery if applicable.
8. Retest.

### Phase 2 — Real user testing

1. Use a real user goal.
2. Let Buddy create a plan.
3. Inspect model, tools, memory and risk.
4. Approve only the intended action.
5. Observe execution.
6. Verify the result independently.
7. Record usability, correctness, latency and failure points.
8. Create regression coverage for important failures.

### Phase 3 — Live-provider testing

Only after sandbox validation:

1. Configure the required authorized credential/provider.
2. Run the provider smoke test.
3. Capture request/result evidence without exposing secrets.
4. Verify failure handling and rate limits.
5. Verify rollback/containment where relevant.
6. Mark the capability `live_provider_verified` only when evidence exists.

### Phase 4 — Production/canary testing

1. Confirm release gates.
2. Deploy a limited canary.
3. Verify browser/API/data/auth health.
4. Monitor errors and latency.
5. Verify user outcome.
6. Roll back once in a controlled test where appropriate.
7. Promote only with evidence.

## Tester result template

```text
Capability:
Tester:
Environment: sandbox | local | staging | live-provider | production
Goal:
Starting state:
Expected result:
Actual result:
Passed: yes/no
Evidence:
Latency/quality notes:
Failure:
Recovery result:
User experience score:
Safety concerns:
Suggested improvement:
Regression test needed: yes/no
``` 

## Mastery gate

A tester may report **passed this test**, but Buddy should not label the capability **mastered** until the evidence lifecycle, repeat acceptance, and applicable holdout/transfer/regression requirements are satisfied.

## Highest-priority testing queue

1. Buddy Actions end-to-end user journey
2. Debug/recovery controlled-failure journey
3. Bot fleet representative workflows
4. One workflow per division
5. Memory persistence/retrieval
6. Debate team decision quality
7. Skill training + benchmark loop
8. MCP/tool execution
9. Dashboard live health
10. Model comparison
11. External integrations
12. Canary deployment + rollback
13. Revenue/financial sandbox workflows
14. Creative generation providers
15. Authorized security scenarios
