# Production Readiness Gate

This gate is evidence-based. A green-looking dashboard, registry entry, or successful static generation is not sufficient to declare production readiness.

## Required evidence

### Build
- TypeScript strict check passes.
- Production build succeeds.
- Dependencies install reproducibly from the lockfile.
- No known build-blocking configuration mismatch.

### Tests
- Unit tests pass.
- Integration tests pass.
- Actions-page tests pass.
- Dynamic fleet tests pass.
- Regression suite passes.
- Critical user journeys have executable checks.

### Runtime
- Health endpoint is available.
- Startup and shutdown behavior are tested.
- Errors are observable with request correlation.
- Timeouts, retries, rate limits, and backpressure are explicit.

### Security
- Secrets are never committed or rendered to client logs.
- Authentication/authorization is enforced for privileged actions.
- External side effects require policy/approval where required.
- Input validation exists at trust boundaries.
- Production data is excluded from synthetic/failure-injection tests.

### Data
- Database migrations are reviewed and reversible where practical.
- Backups/recovery procedures are documented.
- Data retention and deletion behavior are defined.

### Fleet
- No arbitrary bot/module/superbot ceiling exists.
- Discovery and registration are repeatable.
- Health states are evidence-backed.
- Failed resources can be quarantined without corrupting the registry.
- Capacity and utilization are observable.

### Actions / Buddy
- All ten Actions resolve through the same control plane.
- Routes identify the actual Superbot/module used.
- Results include evidence, status, confidence/uncertainty where relevant, and request correlation.
- Self-healing cannot bypass authorization or verification.

## Promotion rule

Production promotion requires all applicable gates to pass. Missing evidence is `BLOCKED`, not `PASS`.

## Important distinction

The repository can be **test-ready** before it is production-ready. External credentials, live provider adapters, domain configuration, billing configuration, DNS, managed databases, and cloud permissions may require deployment-environment verification that cannot be proven solely from source code.
