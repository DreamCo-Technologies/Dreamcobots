import assert from "node:assert/strict";
import test from "node:test";

import { FleetRuntimeRegistry } from "../server/fleet-runtime";

test("instantiates and health-checks all 1,051 fleet profiles", () => {
  const registry = FleetRuntimeRegistry.fromFile();
  const summary = registry.summary();
  assert.equal(summary.instances, 1051);
  assert.equal(summary.ready, 1051);
  assert.equal(registry.healthChecks().every((runtime) => runtime.state === "ready"), true);
});

test("executes a bot-specific sandbox task packet", () => {
  const registry = FleetRuntimeRegistry.fromFile();
  const runtime = registry.get("gaming-titan");
  assert.ok(runtime);
  const result = runtime.execute({
    objective: "Build and test a teacher-led history game in the local sandbox.",
    input: { grade: 8, subject: "history" },
    requestedCapabilities: [],
    liveActionRequested: false,
  });
  assert.equal(result.status, "sandbox_task_packet_ready");
  assert.equal(result.bot.slug, "gaming-titan");
  assert.equal(result.liveExternalActionTaken, false);
});

test("stops before any requested live external action", () => {
  const registry = FleetRuntimeRegistry.fromFile();
  const runtime = registry.get("social-sharing-bot");
  assert.ok(runtime);
  const result = runtime.execute({
    objective: "Publish one approved product update to the selected social account.",
    input: {},
    requestedCapabilities: [],
    liveActionRequested: true,
  });
  assert.equal(result.status, "approval_required");
  assert.equal(result.liveExternalActionTaken, false);
  assert.equal(result.approval.oneActionOnly, true);
});

test("certifies the repository-controlled end-to-end flow for every bot", () => {
  const report = FleetRuntimeRegistry.fromFile().certifyAllEndToEnd();
  assert.equal(report.summary.profilesTested, 1051);
  assert.equal(report.summary.divisionsTested, 45);
  assert.equal(report.summary.sandboxCertified, 1051);
  assert.equal(report.summary.failed, 0);
  assert.equal(report.summary.repositoryControlledFlowComplete, true);
  assert.equal(report.summary.liveExternalFlowComplete, false);
  assert.equal(report.profiles.every((profile) => profile.status === "sandbox_certified"), true);
  assert.equal(report.profiles.every((profile) => profile.checks.platformCapabilityRegistryVerified), true);
  assert.equal(
    report.profiles.every((profile) => Object.values(profile.checks).every(Boolean)),
    true,
  );
});
