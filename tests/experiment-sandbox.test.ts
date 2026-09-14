import assert from "node:assert/strict";
import { test } from "node:test";
import { assessPromotion, createExperimentPlan, GovernedExperimentSandbox, type IsolatedExperimentHost } from "../framework/buddy-platform/experiment-sandbox.js";

const digest = "a".repeat(64);
const plan = () => createExperimentPlan({
  id: "model-fixture-1", kind: "model", title: "Deterministic model fixture", stableVersion: "stable-2026.09", command: ["runner", "fixture.json"], fixtureDigest: digest, baselineDigest: digest, seed: "42",
  permissions: { filesystem: "workspace_ephemeral", network: "none", secrets: "none", production: "none", tools: [{ toolId: "filesystem", mode: "fixture_only" }] },
  provenance: [{ sourceReference: "fixture://model", sourceVersion: "v1", licenseOrUsageBasis: "DreamCo synthetic fixture", transformation: "none", integrityHash: digest }], benchmarkIds: ["benchmark.fixture"], requiredPromotionGates: ["baseline", "reproducible"],
});

test("governed sandbox blocks when no isolation host exists", async () => {
  const run = await new GovernedExperimentSandbox().run(plan());
  assert.equal(run.state, "blocked");
  assert.equal(run.rollbackTarget, "stable-2026.09");
  assert.equal(run.artifacts.length, 3);
});

test("governed sandbox captures redacted bounded artifacts and quarantines limit failures", async () => {
  const host: IsolatedExperimentHost = { run: async () => ({ exitCode: 0, stdout: "Bearer top-secret-token", stderr: "", durationMs: 120_001, peakMemoryMb: 10 }) };
  const run = await new GovernedExperimentSandbox().run(plan(), host);
  assert.equal(run.state, "quarantined");
  assert.equal(run.failureReason, "Resource limit exceeded");
  assert.ok(run.artifacts.find((item) => item.type === "stdout")?.content.includes("[REDACTED]"));
});

test("governed sandbox requests cleanup even after an isolated run", async () => {
  let cleaned = false;
  const host: IsolatedExperimentHost = { run: async () => ({ exitCode: 0, stdout: "ok", stderr: "", durationMs: 1 }), cleanup: async () => { cleaned = true; } };
  const run = await new GovernedExperimentSandbox().run(plan(), host);
  assert.equal(run.state, "passed");
  assert.equal(cleaned, true);
  assert.equal(run.artifacts.at(-1)?.type, "cleanup");
});

test("sandbox rejects nondeterministic benchmark plans and unsafe permissions", () => {
  assert.throws(() => createExperimentPlan({ ...plan(), id: "benchmark-1", kind: "benchmark", seed: undefined }));
  assert.throws(() => createExperimentPlan({ ...plan(), id: "unsafe-1", permissions: { ...plan().permissions, production: "none", secrets: "none", network: "allowlist", networkAllowlist: [] } }));
});

test("promotion remains held until independent evidence gates pass", async () => {
  const host: IsolatedExperimentHost = { run: async () => ({ exitCode: 0, stdout: "ok", stderr: "", durationMs: 1 }) };
  const run = await new GovernedExperimentSandbox().run(plan(), host);
  const held = assessPromotion(run, { baselineCompared: true, reproducible: false, benchmarkPassed: true, groundingPassed: true, datasetQualityPassed: true, regressionPassed: true, ownerApproved: true });
  assert.equal(held.state, "hold");
  assert.deepEqual(held.missingGates, ["reproducible"]);
  const candidate = assessPromotion(run, { baselineCompared: true, reproducible: true, benchmarkPassed: true, groundingPassed: true, datasetQualityPassed: true, regressionPassed: true, ownerApproved: true });
  assert.equal(candidate.state, "candidate");
});
