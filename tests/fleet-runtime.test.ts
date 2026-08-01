import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { resolve } from "node:path";
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

test("Buddy chooses the strongest declared specialist for a natural-language task", () => {
  const registry = FleetRuntimeRegistry.fromFile();
  const result = registry.routeCapability({
    objective: "Build and test a multiplayer video game with procedural levels.",
    requestedCapabilities: [],
    liveActionRequested: false,
  });
  assert.equal(result.selected.slug, "gaming-titan");
  assert.ok(result.matchedCapabilities.includes("Game building and modding"));
  assert.equal(result.coverage.profilesSearched, 1051);
  assert.equal(result.coverage.declaredCapabilitiesSearched, 8408);
  assert.equal(result.modelPlan.mode, "free");
  assert.equal(result.modelPlan.connector.id, "buddy_native");
  assert.equal(result.execution.status, "sandbox_task_packet_ready");
});

test("Buddy premium routing never upgrades or spends automatically", () => {
  const registry = FleetRuntimeRegistry.fromFile();
  const result = registry.routeCapability({
    objective: "Prepare a careful architecture review for this application.",
    requestedCapabilities: [],
    liveActionRequested: false,
    modelMode: "premium",
    modelConnectorId: "anthropic",
    approvePaidModelForThisRequest: false,
  });
  assert.equal(result.modelPlan.mode, "premium");
  assert.equal(result.modelPlan.status, "paid_approval_required");
  assert.equal(result.modelPlan.automaticPaidUpgrade, false);
  assert.equal(result.modelPlan.providerCallExecuted, false);
  assert.equal(result.execution.liveExternalActionTaken, false);
});

test("Buddy honors an explicitly selected bot and still gates live actions", () => {
  const registry = FleetRuntimeRegistry.fromFile();
  const result = registry.routeCapability({
    objective: "Publish an approved cross-platform campaign update.",
    preferredBotSlug: "social-sharing-bot",
    requestedCapabilities: ["Cross-platform content adaptation"],
    liveActionRequested: true,
  });
  assert.equal(result.selected.slug, "social-sharing-bot");
  assert.equal(result.selectionReason, "owner_selected_specialist");
  assert.equal(result.execution.status, "approval_required");
  assert.equal(result.execution.liveExternalActionTaken, false);
});

test("Buddy can explicitly route every catalog profile", () => {
  const registry = FleetRuntimeRegistry.fromFile();
  const catalog = JSON.parse(readFileSync(resolve(process.cwd(), "config", "generated", "bots.catalog.json"), "utf8"));
  for (const bot of catalog.bots) {
    const result = registry.routeCapability({
      objective: `Prepare a sandbox task for ${bot.identity.display_name}.`,
      preferredBotSlug: bot.identity.slug,
      requestedCapabilities: [],
      liveActionRequested: false,
    });
    assert.equal(result.selected.slug, bot.identity.slug);
    assert.equal(result.execution.status, "sandbox_task_packet_ready");
  }
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
