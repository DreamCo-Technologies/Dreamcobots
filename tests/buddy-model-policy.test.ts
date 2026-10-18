import assert from "node:assert/strict";
import test from "node:test";

import { readFileSync } from "node:fs";

import {
  BuddyModelAccessError,
  getBuddyModelAllowlist,
  resolveBuddyModelPlan,
  selectBuddyModelsForTask,
  validateBuddyModelAllowlist,
} from "../server/buddy-model-policy";

const OWNER = { role: "owner" } as const;

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
  }, {}, OWNER);
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
  assert.ok(plan.candidates.filter((candidate) => !candidate.discoveryTarget).every((candidate) => ["paid", "freemium"].includes(candidate.tier)));
  assert.equal(plan.automaticPaidUpgrade, false);
});

test("free-first routing excludes paid-only executable targets", () => {
  for (const access of [undefined, OWNER]) {
    const plan = selectBuddyModelsForTask({
      objective: "Write, test, and explain a small application",
      requiredCapabilities: ["coding"],
      preferredTier: "free",
      maxCandidates: 20,
      allowDiscovery: access === OWNER,
      approvePaidModelForThisRequest: false,
    }, {}, access);
    // Owner discovery keeps the previous 20-candidate breadth; normal callers see only allowlisted targets.
    if (access === OWNER) assert.equal(plan.candidates.length, 20);
    assert.ok(plan.candidates.length >= 1);
    assert.ok(plan.candidates.filter((candidate) => !candidate.discoveryTarget).every((candidate) => ["free", "freemium"].includes(candidate.tier)));
  }
});

test("Path D: selection is allowlist-only by default and discovery defaults off", () => {
  const allowlisted = new Set(getBuddyModelAllowlist().entries.map((entry) => entry.targetId));
  for (const preferredTier of ["free", "premium", "any"] as const) {
    const plan = selectBuddyModelsForTask({
      objective: "Make a video, generate music, translate, research, and write code",
      requiredCapabilities: ["video", "music", "coding"],
      preferredTier,
      maxCandidates: 20,
    }, {});
    assert.equal(plan.access.callerRole, "user");
    assert.equal(plan.access.allowlistOnly, true);
    assert.equal(plan.access.discoveryEnabled, false);
    assert.ok(plan.candidates.every((candidate) => allowlisted.has(candidate.targetId) && candidate.allowlisted));
    assert.ok(plan.candidates.every((candidate) => !candidate.discoveryTarget));
    assert.equal(plan.providerCallExecuted, false);
  }
});

test("Path D: a normal caller cannot opt into discovery; the owner can, and nothing is executed", () => {
  const request = { objective: "Find the strongest coding model", requiredCapabilities: ["coding"], allowDiscovery: true, maxCandidates: 20 };
  assert.throws(() => selectBuddyModelsForTask(request, {}), BuddyModelAccessError);
  assert.throws(() => selectBuddyModelsForTask(request, {}, { role: "user" }), /owner only/);
  const plan = selectBuddyModelsForTask(request, {}, OWNER);
  assert.equal(plan.access.discoveryEnabled, true);
  assert.equal(plan.access.discoveryExecuted, false);
  assert.equal(plan.providerCallExecuted, false);
  const outsideAllowlist = plan.candidates.filter((candidate) => !candidate.allowlisted);
  assert.ok(outsideAllowlist.length > 0);
  assert.ok(outsideAllowlist.every((candidate) => [
    "official_catalog_discovery_required",
    "allowlist_evidence_required",
  ].includes(candidate.readiness)));
});

test("Path D: the owner without allowDiscovery is still allowlist-only", () => {
  const allowlisted = new Set(getBuddyModelAllowlist().entries.map((entry) => entry.targetId));
  const plan = selectBuddyModelsForTask({ objective: "Write code", maxCandidates: 20 }, {}, OWNER);
  assert.equal(plan.access.allowlistOnly, true);
  assert.ok(plan.candidates.every((candidate) => allowlisted.has(candidate.targetId)));
});

test("allowlisted premium targets still require per-request approval and never become executable", () => {
  const unapproved = selectBuddyModelsForTask({
    objective: "Write and review production code",
    requiredCapabilities: ["coding"],
    preferredTier: "premium",
    approvePaidModelForThisRequest: false,
  }, { OPENAI_API_KEY: "configured-for-test" });
  assert.ok(unapproved.candidates.length > 0);
  assert.ok(unapproved.candidates.every((candidate) => candidate.readiness === "paid_approval_required"));
  assert.equal(unapproved.automaticPaidUpgrade, false);
  const approved = selectBuddyModelsForTask({
    objective: "Write and review production code",
    requiredCapabilities: ["coding"],
    preferredTier: "premium",
    approvePaidModelForThisRequest: true,
  }, { OPENAI_API_KEY: "configured-for-test" });
  assert.ok(approved.candidates.every((candidate) => candidate.readiness === "exact_model_verification_required"));
  assert.equal(approved.providerCallExecuted, false);
});

test("the allowlist file is valid and fails closed on unevidenced or mismatched entries", () => {
  const raw = JSON.parse(readFileSync("config/buddy/model-allowlist.json", "utf8"));
  const allowlist = validateBuddyModelAllowlist(raw);
  assert.equal(allowlist.default_policy, "deny_unlisted");
  assert.match(allowlist._comment, /Path A benchmark evidence/);
  assert.match(allowlist._comment, /Path B adapter evidence/);
  assert.ok(allowlist.entries.some((entry) => entry.connectorId === "buddy_native"));
  const withEntry = (entry: unknown) => ({ ...raw, entries: [...raw.entries, entry] });
  // Contract-only connector (Anthropic Claude Sonnet 4, target 3) is rejected.
  assert.throws(() => validateBuddyModelAllowlist(withEntry({
    targetId: 3, name: "Claude Sonnet 4", provider: "Anthropic", connectorId: "anthropic",
    evidence: { path: "B", connectorImplementationStatus: "adapter_implemented", evidenceScope: "connector_only", source: "x" },
  })), /local_ready or adapter_implemented/);
  // Missing evidence is rejected by the schema.
  assert.throws(() => validateBuddyModelAllowlist(withEntry({ targetId: 22, name: "OpenAI Swarm", provider: "OpenAI", connectorId: "openai" })));
  // Path A evidence must be complete.
  assert.throws(() => validateBuddyModelAllowlist(withEntry({
    targetId: 22, name: "OpenAI Swarm", provider: "OpenAI", connectorId: "openai", evidence: { path: "A", source: "x" },
  })));
  // Duplicate and discovery targets are rejected.
  assert.throws(() => validateBuddyModelAllowlist(withEntry(raw.entries[0])), /Duplicate/);
  assert.throws(() => validateBuddyModelAllowlist({ ...raw, default_policy: "allow_all" }));
});
