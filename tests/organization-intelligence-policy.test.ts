import assert from "node:assert/strict";
import test from "node:test";

import {
  createOrganizationBenchmarkPlan,
  loadOrganizationIntelligenceRegistry,
} from "../server/organization-intelligence-policy";

test("organization registry combines the existing 500 targets with the complete Alliance snapshot", () => {
  const registry = loadOrganizationIntelligenceRegistry();
  assert.equal(registry.summary.existingBenchmarkTargets, 500);
  assert.ok(registry.summary.existingProviders >= 90);
  assert.ok(registry.summary.allianceMembers >= 190);
  assert.equal(registry.summary.organizationRecords, registry.existingProviders.length + registry.allianceMembers.length);
  assert.equal(registry.userNeedTaxonomy.length, 20);
  assert.equal(registry.benchmarkDimensions.length, 15);
  assert.ok(registry.allianceMembers.every((item) => item.liveBenchmarksCompleted === 0));
});

test("organization benchmark plans are bounded, evidence-first, and never accept credentials", () => {
  const registry = loadOrganizationIntelligenceRegistry();
  const plan = createOrganizationBenchmarkPlan({
    ownerProfileId: "owner-local",
    organizationIds: [registry.existingProviders[0].id, registry.allianceMembers[0].id],
    userNeedIds: registry.userNeedTaxonomy.slice(0, 3).map((item) => item.id),
    signedFixturesPerNeed: 2,
    maxConcurrency: 4,
    allowNetwork: false,
    approveNetworkForThisRun: false,
    maximumPaidBudgetUsd: 0,
    approvePaidBudgetForThisRun: false,
  });
  assert.equal(plan.status, "local_catalog_plan_ready");
  assert.equal(plan.capacity.totalCases, 12);
  assert.equal(plan.permissions.credentialValuesAccepted, false);
  assert.equal(plan.executionPerformed, false);
  assert.equal(plan.permanentBestClaimed, false);
});

test("network and paid organization benchmarks require run-specific approval", () => {
  const registry = loadOrganizationIntelligenceRegistry();
  const base = {
    ownerProfileId: "owner-local",
    organizationIds: [registry.allianceMembers[0].id],
    userNeedIds: [registry.userNeedTaxonomy[0].id],
    signedFixturesPerNeed: 1,
    maxConcurrency: 1,
  };
  assert.equal(createOrganizationBenchmarkPlan({
    ...base,
    allowNetwork: true,
    approveNetworkForThisRun: false,
    maximumPaidBudgetUsd: 0,
    approvePaidBudgetForThisRun: false,
  }).status, "network_approval_required");
  assert.equal(createOrganizationBenchmarkPlan({
    ...base,
    allowNetwork: false,
    approveNetworkForThisRun: false,
    maximumPaidBudgetUsd: 10,
    approvePaidBudgetForThisRun: false,
  }).status, "paid_budget_approval_required");
});

test("unknown organizations and user needs are rejected", () => {
  assert.throws(() => createOrganizationBenchmarkPlan({
    ownerProfileId: "owner-local",
    organizationIds: ["alliance-not-real"],
    userNeedIds: ["coding"],
    signedFixturesPerNeed: 1,
    maxConcurrency: 1,
    allowNetwork: false,
    approveNetworkForThisRun: false,
    maximumPaidBudgetUsd: 0,
    approvePaidBudgetForThisRun: false,
  }), /Unknown organization/);
});
