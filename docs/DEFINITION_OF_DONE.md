# Definition of Done

A capability is production-complete only when:

- [ ] Canonical contract is versioned.
- [ ] One owner and one canonical implementation exist.
- [ ] Required adapters/connectors are isolated.
- [ ] Policy gates are enforced.
- [ ] Contract and unit tests pass.
- [ ] Integration tests pass where applicable.
- [ ] Sandbox side effects are verified.
- [ ] User-facing E2E passes where applicable.
- [ ] Telemetry and audit are present.
- [ ] Errors/retries/idempotency are handled.
- [ ] Security review is complete for high-impact actions.
- [ ] Commercial attribution exists when money is involved.
- [ ] Documentation and runbook exist.
- [ ] Rollback/recovery is tested or explicitly bounded.
- [ ] Legacy implementations are either proven necessary or migrated/aliased.

Green tests alone do not make a capability production-ready; operational ownership and evidence are required.
