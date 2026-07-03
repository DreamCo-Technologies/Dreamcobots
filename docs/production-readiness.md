# Production Readiness Standard

## Active production scope

The following repository areas are treated as production-critical and are required to pass readiness gates:

- `/home/runner/work/Dreamcobots/Dreamcobots/index.js`
- `/home/runner/work/Dreamcobots/Dreamcobots/DreamCo/**`
- `/home/runner/work/Dreamcobots/Dreamcobots/backend/**`
- `/home/runner/work/Dreamcobots/Dreamcobots/core/**`
- `/home/runner/work/Dreamcobots/Dreamcobots/dreamco-control-tower/**`
- `/home/runner/work/Dreamcobots/Dreamcobots/__tests__/**`
- `/home/runner/work/Dreamcobots/Dreamcobots/tests/**`
- `/home/runner/work/Dreamcobots/Dreamcobots/config/**`

Directories outside this scope are treated as non-blocking for root production gates unless explicitly promoted to active scope.

## Required production gates

Each release candidate must satisfy all of the following:

1. **Node lint gate**: `npm run lint` passes with zero warnings.
2. **Node test gate**: `npm run test -- --passWithNoTests` passes.
3. **Node build gate**: `npm run build` passes.
4. **Python smoke gate**: `python -m pytest tests/test_company_lookup_bot.py tests/test_integration_feedback_bot.py -q` passes.
5. **Python suite gate**: `python -m pytest tests/ -q --tb=short --ignore=tests/e2e` passes.
6. **Dependency hygiene gate**: security vulnerabilities in active-scope dependencies are tracked and remediated before release.
7. **Deployment gate**: production artifacts are generated without runtime startup failures.

## Baseline status (current run)

- Node lint: **failing** before this change due to non-active directories being linted by root command.
- Node tests: **failing** before this change due to date-sensitive orchestrator test.
- Node build: **passing**.
- Python smoke tests: **passing**.
- Python suite: **failing** before this change due to:
  - `config/__init__.py` syntax corruption
  - missing `LeadGenBot` backend import target

## Follow-up backlog

- Add an explicit CI workflow that executes only active-scope production gates.
- Add dependency vulnerability thresholds for PR merge blocking.
- Add service-level startup probes and standardized runtime health checks for all active services.
