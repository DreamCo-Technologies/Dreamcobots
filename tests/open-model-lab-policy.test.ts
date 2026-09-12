import assert from "node:assert/strict";
import test from "node:test";

import {
  createBuddyOpenCoreManifest,
  createOpenModelComparisonPlan,
  createRepositoryTrackingPlan,
  createOpenSourceSandboxPlan,
  evaluateBuddyLearningEvidence,
} from "../server/open-model-lab-policy";

const buddyCoreBase = {
  releaseId: "buddy-open-core-0.1",
  modelName: "Buddy Open Core Research",
  distributionMode: "private" as const,
  architectureProfileId: "dense_edge" as const,
  exactSourceUrl: "https://huggingface.co/DreamCo-Technologies/buddy-open-core",
  immutableRevision: "release-v0.1.0",
  declaredLicense: "Apache-2.0",
  parameterBillions: 7,
  activeParameterBillions: 7,
  contextTokens: 32768,
  weightFormat: "safetensors" as const,
  quantization: "bf16" as const,
  runtimeIds: ["mlx" as const, "llama-cpp" as const],
  capabilityTracks: ["reasoning" as const, "coding" as const, "tool_use" as const],
  sourceAndLicenseReviewed: false,
  checksumsVerified: false,
  sandboxLoadPassed: false,
  sameFixtureBenchmarksPassed: false,
  holdoutPassed: false,
  securityReviewPassed: false,
};

test("Buddy Open Core creates an honest portable manifest without claiming weights", () => {
  const manifest = createBuddyOpenCoreManifest(buddyCoreBase);
  assert.equal(manifest.status, "evidence_gates_remaining");
  assert.equal(manifest.trainedWeightsCreatedByThisRequest, false);
  assert.equal(manifest.inferenceStartedByThisRequest, false);
  assert.equal(manifest.distribution.id, "private");
  assert.equal(manifest.publicationPerformed, false);
  assert.ok(manifest.apiCompatibility.includes("/v1/chat/completions"));
  assert.equal(manifest.evidence.total, 6);
});

test("Buddy Open Core keeps code, open-source, open-weight, and private releases distinct", () => {
  const modes = ["code_version", "open_source", "open_weights", "private"] as const;
  const manifests = modes.map((distributionMode) => createBuddyOpenCoreManifest({ ...buddyCoreBase, distributionMode }));
  assert.deepEqual(manifests.map((manifest) => manifest.distribution.id), modes);
  assert.equal(manifests.find((manifest) => manifest.distribution.id === "open_weights")?.distribution.publishes_weights, true);
  assert.equal(manifests.find((manifest) => manifest.distribution.id === "open_source")?.distribution.publishes_weights, false);
});

test("Buddy Open Core enforces dense and sparse parameter rules", () => {
  assert.throws(() => createBuddyOpenCoreManifest({ ...buddyCoreBase, activeParameterBillions: 3 }), /equal total and active/);
  assert.throws(() => createBuddyOpenCoreManifest({ ...buddyCoreBase, architectureProfileId: "sparse_moe", parameterBillions: 64, activeParameterBillions: 64 }), /fewer parameters/);
  const sparse = createBuddyOpenCoreManifest({ ...buddyCoreBase, architectureProfileId: "sparse_moe", parameterBillions: 64, activeParameterBillions: 8 });
  assert.equal(sparse.architecture.requires_expert_routing, true);
});

const learningEvidenceBase = {
  cycleId: "buddy-coding-adapter-001",
  baseReleaseId: "buddy-open-core-0.1",
  capabilityId: "typescript-bug-repair",
  method: "lora_adapter" as const,
  sourceManifestSha256: "a".repeat(64),
  trainingArtifactSha256: "b".repeat(64),
  graderVersion: "buddy-grader-1.0.0",
  baselineScores: [0.55, 0.57, 0.56],
  hiddenHoldoutBeforeScores: [0.60, 0.61, 0.59],
  hiddenHoldoutAfterScores: [0.82, 0.81, 0.83],
  regressionBeforeScores: [0.90, 0.91, 0.89],
  regressionAfterScores: [0.90, 0.90, 0.89],
  safetyBeforeScores: [0.93, 0.94, 0.95],
  safetyAfterScores: [0.95, 0.95, 0.96],
  approvedSourcesOnly: true,
  licenseAndProvenanceVerified: true,
  privateDataExcludedOrConsented: true,
  sandboxTrainingPassed: true,
  ownerReleaseApproved: false,
};

test("proof-carrying learning accepts repeatable holdout gains without auto-release", () => {
  const evidence = evaluateBuddyLearningEvidence(learningEvidenceBase);
  assert.equal(evidence.improvementProven, true);
  assert.equal(evidence.status, "improvement_proven_owner_approval_required");
  assert.equal(evidence.gates.hidden_holdout_improved, true);
  assert.equal(evidence.gates.regression_within_limit, true);
  assert.equal(evidence.promotedToUsers, false);
  assert.equal(evidence.globalWeightsModified, false);
  assert.equal(evidence.nextGate, "owner_release_approval");
});

test("proof-carrying learning rejects weak holdout gains and safety regression", () => {
  const evidence = evaluateBuddyLearningEvidence({
    ...learningEvidenceBase,
    hiddenHoldoutAfterScores: [0.61, 0.62, 0.60],
    safetyAfterScores: [0.80, 0.81, 0.79],
  });
  assert.equal(evidence.improvementProven, false);
  assert.equal(evidence.status, "learning_evidence_failed");
  assert.equal(evidence.gates.hidden_holdout_improved, false);
  assert.equal(evidence.gates.safety_not_regressed, false);
  assert.equal(evidence.promotedToUsers, false);
});

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
