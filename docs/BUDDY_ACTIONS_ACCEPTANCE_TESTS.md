# Buddy Actions Acceptance Tests

## Purpose

Prevent the Actions page from becoming a collection of buttons that only look functional. Each control must be continuously checked against its declared contract.

## Universal acceptance test

For every action control:

1. control is discoverable;
2. plain-language purpose is visible;
3. execution class is visible (READ-ONLY / LOCAL / REMOTE);
4. prerequisites are checked before execution;
5. action receives a unique action/run ID;
6. execution result is captured;
7. failure is routed to the correct queue;
8. evidence is linked;
9. result status is derived from evidence;
10. retry behavior is bounded;
11. consequential changes have an approval/rollback path;
12. UI does not claim success when execution was skipped or unavailable.

## Specific tests

### Doctor
- missing dependency is detected;
- malformed config is reported;
- healthy repository produces a pass report;
- no source mutation occurs during diagnostics.

### Tests
- passing suite produces verified pass;
- failing suite produces failure evidence;
- first/root failure is preserved;
- failure links to canonical Issue/Action incident.

### Lint/Type
- configured checks are actually invoked;
- non-zero exit becomes failure;
- no-error run becomes verified pass.

### Security
- scanner availability is verified;
- findings are captured;
- critical finding blocks certification;
- secrets never appear in output.

### Benchmark
- benchmark version is recorded;
- baseline is recorded;
- score, latency and cost are captured;
- threshold comparison is deterministic;
- failed benchmark creates a capability gap rather than fake green.

### Repair Plan
- requires evidence;
- produces bounded steps;
- includes tests;
- includes rollback for consequential changes;
- never directly claims the repair succeeded.

### Pages Verify
- source data parses;
- required fields exist;
- UI loads;
- key controls render;
- displayed status matches source evidence.

### Device Bundle
- build succeeds;
- artifact exists;
- checksum/metadata is produced;
- install/launch smoke test succeeds where runner supports it.

### Refresh GitHub Runs
- GitHub response is current enough for the selected window;
- workflow identity is mapped correctly;
- unknown workflows remain visible rather than discarded;
- stale data is labeled.

### Remote workflow dispatch
- workflow is approved;
- permissions are sufficient;
- dispatch creates a traceable run;
- result is polled or linked;
- failures enter Actions queue.

## Truthfulness tests

The following must fail CI if violated:

- button says "completed" without an execution record;
- green status exists without evidence;
- unavailable runner is presented as successful;
- failed required check is hidden by a stale cache;
- destructive operation lacks an approval/rollback gate;
- secret value appears in evidence;
- retry count is unbounded.

## Regression policy

Every bug found in an Actions control becomes one of:

- a regression test;
- a contract clarification;
- a monitoring rule;
- a runbook improvement.

This prevents the Actions page itself from becoming a source of false confidence.
