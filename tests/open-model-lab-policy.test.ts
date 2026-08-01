import assert from "node:assert/strict";
import test from "node:test";

import {
  createOpenModelComparisonPlan,
  createRepositoryTrackingPlan,
  createOpenSourceSandboxPlan,
} from "../server/open-model-lab-policy";

test("global model comparison uses evidence and never scores developer region", () => {
  const plan = createOpenModelComparisonPlan({
    modelFamilyIds: ["gpt-oss", "qwen-coder", "mistral-open-code"],
    taskIds: ["bug_repair", "secure_review"],
    repetitions: 2,
    maxBudgetUsd: 0,
    allowExternalNetwork: false,
    approvePaidAdaptersForThisRun: false,
  });
  assert.equal(plan.modelCount, 3);
  assert.equal(plan.totalCases, 12);
  assert.equal(plan.scoring.developerRegionUsedForScoring, false);
  assert.equal(plan.liveExecutionPerformed, false);
});

test("open and frontier targets share fixtures without invented live results", () => {
  const plan = createOpenModelComparisonPlan({
    modelFamilyIds: ["gpt-oss"],
    frontierTargets: [{ referenceId: "frontier-openai-api", exactModelId: "frontier-code-model-2026-07" }],
    taskIds: ["bug_repair", "reproducibility"],
    repetitions: 1,
    maxBudgetUsd: 0,
    allowExternalNetwork: false,
    approvePaidAdaptersForThisRun: false,
  });
  assert.equal(plan.openModelCount, 1);
  assert.equal(plan.frontierTargetCount, 1);
  assert.equal(plan.scoring.openAndFrontierComparedOnSameFixtures, true);
  assert.equal(plan.status, "frontier_network_approval_required");
  assert.equal(plan.liveExecutionPerformed, false);
});

test("sandbox plan requires immutable revisions and performs no live execution", () => {
  assert.throws(() => createOpenSourceSandboxPlan({
    sourceKind: "repository",
    sourceUrl: "https://github.com/example/project",
    revision: "main",
    declaredLicense: "MIT",
    objective: "Build and test the licensed project in isolation.",
    ownerConfirmsRights: true,
    allowNetworkDuringBuild: false,
    trustRemoteCode: false,
    limits: { timeoutSeconds: 900, cpuCores: 2, memoryMb: 4096, diskMb: 20480, processCount: 64 },
  }), /Pin an exact/);

  const plan = createOpenSourceSandboxPlan({
    sourceKind: "repository",
    sourceUrl: "https://github.com/example/project",
    revision: "v1.2.3",
    declaredLicense: "MIT",
    objective: "Build and test the licensed project in isolation.",
    ownerConfirmsRights: true,
    allowNetworkDuringBuild: false,
    trustRemoteCode: false,
    limits: { timeoutSeconds: 900, cpuCores: 2, memoryMb: 4096, diskMb: 20480, processCount: 64 },
  });
  assert.equal(plan.liveExecutionPerformed, false);
  assert.equal(plan.controls.network, "off");
  assert.equal(plan.automaticMerge, false);
  assert.equal(plan.academy.automaticModelTraining, false);
  assert.equal(plan.contribution.automaticUpstreamSubmission, false);
});

test("model-weight plans block credentials, remote code, and unsafe formats", () => {
  const base = {
    sourceKind: "model_weights" as const,
    sourceUrl: "https://huggingface.co/example/model",
    revision: "abc123def456",
    declaredLicense: "Apache-2.0",
    objective: "Evaluate licensed weights against signed coding fixtures.",
    ownerConfirmsRights: true,
    allowNetworkDuringBuild: false,
    limits: { timeoutSeconds: 900, cpuCores: 2, memoryMb: 4096, diskMb: 20480, processCount: 64 },
  };
  assert.throws(() => createOpenSourceSandboxPlan({ ...base, trustRemoteCode: true, weightFormat: "safetensors" }), /Remote model code/);
  assert.throws(() => createOpenSourceSandboxPlan({
    ...base,
    sourceUrl: "https://token@example.com/model",
    trustRemoteCode: false,
    weightFormat: "safetensors",
  }), /credentials/);
  const plan = createOpenSourceSandboxPlan({ ...base, trustRemoteCode: false, weightFormat: "gguf" });
  assert.equal(plan.source.weightFormat, "gguf");
});

test("repository tracking stores metadata and requires a scheduler for background checks", () => {
  const plan = createRepositoryTrackingPlan({
    sourceUrl: "https://github.com/example/project",
    revision: "v2.0.0",
    declaredLicense: "Apache-2.0",
    cadence: "daily",
    interests: ["releases", "license", "security", "tests"],
    notificationChannels: ["in_app"],
    ownerConfirmsRights: true,
  });
  assert.equal(plan.storage.metadataOnly, true);
  assert.equal(plan.deployedSchedulerRequired, true);
  assert.equal(plan.nextCheckScheduled, false);
  assert.equal(plan.automaticPullOrExecution, false);
});
