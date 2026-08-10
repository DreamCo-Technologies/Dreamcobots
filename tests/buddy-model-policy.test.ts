import assert from "node:assert/strict";
import test from "node:test";

import {
  resolveBuddyModelPlan,
  selectBuddyModelsForTask,
} from "../server/buddy-model-policy";

test("Buddy defaults to a no-charge native model route", () => {
  const plan = resolveBuddyModelPlan({}, {});
  assert.equal(plan.mode, "free");
  assert.equal(plan.connector.id, "buddy_native");
  assert.equal(plan.status, "free_route_ready");
  assert.equal(plan.automaticPaidUpgrade, false);
  assert.equal(plan.providerCallExecuted, false);
});

test("premium mode pauses until this request is approved", () => {
  const plan = resolveBuddyModelPlan({
    modelMode: "premium",
    modelConnectorId: "openai",
    approvePaidModelForThisRequest: false,
  }, { OPENAI_API_KEY: "configured-for-test" });
  assert.equal(plan.status, "paid_approval_required");
  assert.equal(plan.paidUseApprovedForThisRequest, false);
  assert.equal(plan.providerCallExecuted, false);
});

test("approved premium mode still requires a configured provider adapter", () => {
  const plan = resolveBuddyModelPlan({
    modelMode: "premium",
    modelConnectorId: "google_gemini",
    selectedModelId: "owner-selected-model",
    approvePaidModelForThisRequest: true,
  }, {});
  assert.equal(plan.status, "configuration_required");
  assert.equal(plan.connector.configured, false);
  assert.equal(plan.selectedModelId, "owner-selected-model");
  assert.equal(plan.providerCallExecuted, false);
});

test("a configured contract-only provider is not mislabeled as an implemented adapter", () => {
  const plan = resolveBuddyModelPlan({
    modelMode: "premium",
    modelConnectorId: "google_gemini",
    approvePaidModelForThisRequest: true,
  }, { GEMINI_API_KEY: "configured-for-test" });
  assert.equal(plan.status, "adapter_implementation_required");
  assert.equal(plan.connector.implementationStatus, "contract_only");
  assert.equal(plan.providerCallExecuted, false);
});

test("Buddy ranks task-fit candidates without calling them or claiming a permanent best", () => {
  const plan = selectBuddyModelsForTask({
    objective: "Debug my repository, repair the TypeScript code, and run tests",
    requiredCapabilities: ["coding", "code repair"],
    preferredTier: "free",
    priorities: { quality: 0.8, cost: 1, latency: 0.6, privacy: 1 },
    maxCandidates: 6,
    allowDiscovery: true,
    approvePaidModelForThisRequest: false,
  }, {});
  assert.ok(plan.detectedTaskSignals.includes("coding"));
  assert.equal(plan.providerCallExecuted, false);
  assert.equal(plan.permanentBestClaimed, false);
  assert.equal(plan.truthContract.rankingIsLiveQualityEvidence, false);
  assert.equal(new Set(plan.candidates.map((candidate) => candidate.provider)).size, plan.candidates.length);
  assert.ok(plan.candidates.every((candidate) => candidate.qualityEvidenceContribution === 0));
});

test("privacy-first free routing prefers the governed local Buddy route", () => {
  const plan = selectBuddyModelsForTask({
    objective: "Privately plan and code a local app without sending my repository to a provider",
    requiredCapabilities: ["coding"],
    preferredTier: "free",
    priorities: { quality: 0.4, cost: 1, latency: 0.8, privacy: 1 },
    maxCandidates: 5,
    allowDiscovery: false,
    approvePaidModelForThisRequest: false,
  }, {});
  assert.equal(plan.candidates[0]?.connectorId, "buddy_native");
  assert.equal(plan.candidates[0]?.readiness, "local_route_ready");
});

test("premium candidates remain gated by per-request approval", () => {
  const plan = selectBuddyModelsForTask({
    objective: "Analyze and summarize a long legal document",
    requiredCapabilities: ["long context", "document analysis"],
    preferredTier: "premium",
    maxCandidates: 8,
    allowDiscovery: false,
    approvePaidModelForThisRequest: false,
  }, { ANTHROPIC_API_KEY: "configured-for-test" });
  const premium = plan.candidates.filter((candidate) => ["paid", "freemium"].includes(candidate.tier));
  assert.ok(premium.length > 0);
  assert.ok(premium.every((candidate) => candidate.readiness === "paid_approval_required"));
  assert.equal(plan.automaticPaidUpgrade, false);
});
