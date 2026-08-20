# Buddy Learning Memory

Each learning attempt should record:

- capability
- strategy used
- result
- score before
- score after
- lesson learned
- evidence ID
- timestamp

The ledger is intended to support targeted remediation, regression detection, strategy comparison and auditable promotion. It should be persisted by the repository's existing storage layer rather than treated as a temporary prompt history.

A failed attempt is valuable only when it produces actionable evidence. Repeated identical failures should be clustered so the planner can choose a different strategy.
