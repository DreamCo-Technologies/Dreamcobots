import assert from "node:assert/strict";
import test from "node:test";

import {
  buildDivisionProductionRegistry,
  createCapabilityGapPlan,
  createDailyDivisionBenchmarkPlan,
} from "../server/division-production-policy";
import { runDailyDivisionContractBenchmarks } from "../tools/run_daily_division_benchmarks";
import { buildBuddySuccessProgram } from "../tools/generate_buddy_success_program";

test("every division has a professional charter, 100 capabilities, and production evidence gates", () => {
  const registry = buildDivisionProductionRegistry();
  assert.ok(registry.divisions.length > 0);
  assert.equal(registry.summary.capabilityContracts, registry.divisions.length * 100);
  assert.equal(registry.summary.logicalDailyWorkerSlots, registry.divisions.length * 8);
  assert.equal(registry.summary.productionReadyDivisions, 0);
  assert.ok(registry.divisions.every((division) => division.charter.purpose.length >= 60));
  assert.ok(registry.divisions.every((division) => division.charter.boundary.length >= 60));
  assert.ok(registry.divisions.every((division) => division.newCapabilityContracts === 100));
  assert.ok(registry.divisions.every((division) => division.readinessGates.length === 12));
});

test("daily benchmark plans are parallel, bounded, local-first, and do not self-release", () => {
  const registry = buildDivisionProductionRegistry();
  const plan = createDailyDivisionBenchmarkPlan({
    ownerProfileId: "owner-local",
    divisions: registry.divisions.map((division) => division.name),
    signedFixturesPerDivision: 10,
    maxConcurrency: 16,
    schedule: "daily",
    allowNetwork: false,
    maxPaidBudgetUsd: 0,
    approveNetworkForThisRun: false,
    approvePaidBudgetForThisRun: false,
  });
  assert.equal(plan.status, "local_fixture_plan_ready");
  assert.equal(plan.capacity.totalSignedFixtures, registry.divisions.length * 10);
  assert.equal(plan.capacity.logicalWorkerSlots, registry.summary.logicalDailyWorkerSlots);
  assert.equal(plan.permissions.network, false);
  assert.equal(plan.permissions.productionRelease, false);
  assert.equal(plan.executionPerformed, false);
});

test("network and paid division benchmarks require run-specific approval", () => {
  const base = {
    ownerProfileId: "owner-local",
    divisions: ["DreamCodeLab"],
    signedFixturesPerDivision: 10,
    maxConcurrency: 8,
    schedule: "once" as const,
    allowNetwork: true,
    maxPaidBudgetUsd: 25,
    approveNetworkForThisRun: false,
    approvePaidBudgetForThisRun: false,
  };
  assert.equal(createDailyDivisionBenchmarkPlan(base).status, "network_approval_required");
  assert.equal(createDailyDivisionBenchmarkPlan({ ...base, approveNetworkForThisRun: true }).status, "paid_budget_approval_required");
});

test("missing capabilities become review-branch build plans, not self-granted powers", () => {
  const plan = createCapabilityGapPlan({
    ownerProfileId: "owner-local",
    goal: "Build a reliable owner-controlled inventory forecast workflow.",
    division: "DreamRetail",
    missingCapability: "supplier lead-time drift simulation",
    availableEvidence: ["fixture:retail-lead-time-v1"],
    exactBuildApproval: true,
  });
  assert.equal(plan.status, "review_branch_and_sandbox_required");
  assert.equal(plan.selfGrantedPermissions, false);
  assert.equal(plan.automaticMerge, false);
  assert.equal(plan.automaticRelease, false);
  assert.equal(plan.productionReadyClaimed, false);
});

test("local Buddy success harness checks its 45 fleet divisions and 4,500 capability contracts", async () => {
  const result = await runDailyDivisionContractBenchmarks({ concurrency: 16 });
  const successProgram = buildBuddySuccessProgram();
  // The 45 bot-fleet divisions, 55 domain profiles, and 65 MasterBots are distinct registries.
  assert.equal(result.divisions, successProgram.divisions.length);
  assert.equal(result.divisions, 45);
  assert.equal(result.capabilitiesChecked, successProgram.divisions.length * successProgram.improvement_templates.division_capabilities.length);
  assert.equal(result.capabilitiesChecked, 4500);
  assert.equal(result.failed, 0);
  assert.equal(result.networkUsed, false);
  assert.equal(result.paidServicesUsed, false);
  assert.equal(result.productionReleasePerformed, false);
});
