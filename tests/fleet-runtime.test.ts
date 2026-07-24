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

test("runs an individual declared capability contract without a live side effect", () => {
  const registry = FleetRuntimeRegistry.fromFile();
  const runtime = registry.get("gaming-titan");
  assert.ok(runtime);
  const capability = runtime.profile.capability_search.split(" | ")[4];
  const result = runtime.testCapability(capability);
  assert.equal(result.capability, capability);
  assert.equal(result.status, "sandbox_contract_passed");
  assert.equal(result.checks.declaredOnProfile, true);
  assert.equal(result.checks.routedAsDeclaredCapability, true);
  assert.equal(result.checks.requiredSandboxEvidencePresent, true);
  assert.equal(result.liveExternalActionTaken, false);
  assert.deepEqual(result.failures, []);
});

test("does not certify an undeclared capability as part of a bot profile", () => {
  const registry = FleetRuntimeRegistry.fromFile();
  const runtime = registry.get("gaming-titan");
  assert.ok(runtime);
  const result = runtime.testCapability("Unregistered production deployment");
  assert.equal(result.status, "failed");
  assert.equal(result.checks.declaredOnProfile, false);
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
  assert.equal(report.summary.declaredCapabilitiesTested, 8408);
  assert.equal(report.summary.sandboxCapabilityTestsPassed, 8408);
  assert.equal(report.summary.sandboxCapabilityTestsFailed, 0);
  assert.equal(report.summary.allDeclaredCapabilitiesTested, true);
  assert.equal(report.summary.repositoryControlledFlowComplete, true);
  assert.equal(report.summary.liveExternalFlowComplete, false);
  assert.equal(report.profiles.every((profile) => profile.status === "sandbox_certified"), true);
  assert.equal(report.profiles.every((profile) => profile.capabilityTests.length === profile.declaredCapabilityCount), true);
  assert.equal(
    report.profiles.flatMap((profile) => profile.capabilityTests).every((capability) => (
      capability.status === "sandbox_contract_passed" &&
      capability.liveExternalActionTaken === false &&
      capability.failures === undefined
    )),
    true,
  );
  assert.equal(report.capabilityTestContract.checks.length, 6);
  assert.equal(report.capabilityTestContract.requiredEvidence.length, 5);
  assert.equal(report.profiles.every((profile) => profile.checks.platformCapabilityRegistryVerified), true);
  assert.equal(report.profiles.every((profile) => profile.checks.calculatorBindingVerified), true);
  assert.equal(report.profiles.every((profile) => profile.checks.distributionBindingVerified), true);
  assert.equal(report.profiles.every((profile) => profile.checks.leadSystemBindingVerified), true);
  assert.equal(
    report.profiles.every((profile) => Object.values(profile.checks).every(Boolean)),
    true,
  );
});
