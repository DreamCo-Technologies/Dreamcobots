# DreamCo Production Readiness Master System

This subsystem creates a daily, evidence-based master list of missing work required to make the repository production-ready and keep it that way.

## Daily master list

The report inventories tracked Markdown/MDX requirements, approved chat exports, all PRs, issues and workflow evidence available to the GitHub token, plus repository resources discoverable from tracked files. It creates actionable findings for missing implementation links, tests, runtime routes, benchmark evidence, workflows, security/dependency controls, observability, backups, restore, rollback, and deployment preflight.

Each finding includes a stable ID, source/provenance, severity, owner/workstream where known, dependency references, evidence age, recommended next action, and verification state. It distinguishes missing, disconnected, broken, unverified, blocked, regressed, and verified.

## Current implementation boundary

The current runner performs a complete paginated read-only GitHub Pull Requests API inventory when the workflow token is available. It records normalized PR metadata and marks the inventory BLOCKED when authentication, API access, response validation, or pagination is incomplete. It does not yet claim complete issue, branch, commit, deployment, or external-provider inventories. Those resource classes remain explicit follow-up work until each has a source adapter and evidence-backed contract test.

The current route inventory is path-based discovery. It does not yet generate an executable end-to-end test for every discovered service, API route, integration, database, monitor, backup, security control, and benchmark. Each such route remains DISCOVERED_NOT_RUNTIME_VERIFIED until an authorized test actually exercises it and stores timestamped evidence.

## Routing and workflow tests

A resource route is a directed edge from a capability/resource to its owning service, workflow, API entrypoint, test, runtime evidence, and operational fallback. A route is not healthy merely because a YAML file mentions a name. Required route tests must exercise:
- registry/schema validity and referential integrity;
- workflow trigger, permissions, concurrency, timeout, artifact and failure behavior;
- API/service route contracts and authentication/authorization boundaries;
- dependency and integration contract tests;
- resource-specific unit, integration, end-to-end and failure-path tests;
- observability, alert, backup/restore and rollback evidence;
- benchmark baseline, candidate, holdout and regression checks where applicable.

The inventory generator can identify missing evidence links. It must not fabricate test results or claim that a runtime endpoint was exercised when no safe runner or credentials exist.

## Always-on cadence

The workflow is scheduled every five minutes plus a daily run. GitHub schedules are best-effort, not real-time guarantees. **Current implementation performs a full repository scan on each scheduled invocation; it does not yet process an incremental queue or implement a separate hourly full-scan tier.** The daily master list is uploaded as an artifact. The policy's 65-minute / 13-batch / five-lane rotation is a target design, not proof of a live training schedule: the existing MasterBot workflow remains separately scheduled and must be connected to the canonical registry and evidence queue before this target can be called operational. The dashboard must show last successful run and staleness rather than promise exact timing.

## 65 MasterBots and Actions Control Center

Every MasterBot consumes the same requirement/evidence/dependency queue. Each lane should select the highest-priority unresolved gap in its domain, record baseline evidence, run authorized sandbox work, execute a benchmark and holdout test, record regression status, and requeue unresolved gaps. The current lane runner emits a checkpoint only; it does not prove that training or benchmark execution occurred. Keep checkpoint, execution, and mastery as separate states.

The Actions Control Center should display daily missing counts, severity, PR conflict/dependency queue, per-MasterBot backlog, verified vs estimated completion, last successful run, evidence freshness, and next action. All displayed readiness values must derive from the generated ledger.

## Merge and production gates

No PR is merge-ready unless its base comparison is fresh, three-way merge is clean, required CI/security/dependency checks pass, reviews and branch protections are satisfied, and applicable runtime, integration, benchmark, deployment-preflight and production-isolation evidence is current. Unknown means blocked. No force-push, protection bypass, automatic merge, production write or deployment is permitted by this workflow.

## Chat source limits

Historical conversations must be exported by the owner and added under `governance/dreamco-chat-sources/`. Preserve chat IDs, titles, timestamps, message order, approvals, constraints, and hashes. Private ChatGPT conversations are not exposed to GitHub Actions automatically; missing exports remain an explicit coverage gap.

## Outputs

- `artifacts/dreamco-reconciliation/production-readiness-master-list.json`
- `artifacts/dreamco-reconciliation/production-readiness-master-list.md`
- `artifacts/dreamco-reconciliation/resource-routing-inventory.json`

The daily report is an inventory and decision queue, not an assertion that the system is production-ready.
