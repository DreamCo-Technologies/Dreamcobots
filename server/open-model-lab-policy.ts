import { z } from "zod";

import learningStrategies from "../config/buddy-learning-strategies.json";
import openModelCatalog from "../config/buddy-open-model-coding-lab.json";

type OpenModelCatalog = {
  schema: string;
  model_families: Array<{
    id: string;
    label: string;
    developer: string;
    developer_region: string;
    access: string;
    license: string;
    official_source: string;
  }>;
  frontier_references: Array<{
    id: string;
    label: string;
    provider: string;
    access: string;
    official_source: string;
    exact_model_id_required_at_run: boolean;
    adapter_status: string;
  }>;
  coding_tasks: Array<{ id: string; label: string; grader: string }>;
  evidence_fields: string[];
  sandbox_academy: {
    levels: Array<{ id: string; label: string; outcome: string }>;
    lesson_stages: string[];
    training_data_policy: Record<string, boolean>;
  };
  open_source_sandbox: {
    supported_hosts: string[];
  };
  buddy_open_core: {
    identity: string;
    ownership: string;
    current_status: string;
    compatibility_target: string;
    distribution_modes: Array<{ id: string; label: string; publishes_code: boolean; publishes_weights: boolean; purpose: string }>;
    architecture_profiles: Array<{ id: string; label: string; purpose: string; requires_expert_routing: boolean; requires_mtp: boolean }>;
    api_compatibility: string[];
    weight_formats: string[];
    quantization_targets: string[];
    capability_tracks: string[];
    learning_system: {
      identity: string;
      methods: string[];
      research_references: Array<{ id: string; label: string; official_source: string; published_methods: string[]; buddy_extension: string; comparison_status: string }>;
      innovation_tracks: string[];
      required_cycle: string[];
      promotion_thresholds: { minimum_holdout_score: number; minimum_absolute_improvement: number; maximum_regression: number; minimum_repetitions: number };
      private_data_policy: Record<string, boolean>;
    };
    compute_tiers: Array<{ id: string; target: string; runtimes: string[] }>;
    release_gates: string[];
    truth: Record<string, boolean>;
  };
};

export const OPEN_MODEL_CATALOG = openModelCatalog as OpenModelCatalog;

type LearningTechnique = {
  id: string;
  label: string;
  category: string;
  stage: string;
  compute: "low" | "medium" | "high" | "very_high";
  objectives: string[];
  purpose: string;
  official_source: string;
  status: "catalogued";
};

type LearningStrategyCatalog = {
  schema: string;
  catalog_status: string;
  objectives: string[];
  techniques: LearningTechnique[];
  failure_controls: Array<{ id: string; metric: string; direction: "minimum" | "maximum"; threshold: number; action: string; purpose: string }>;
  study_optimizer: {
    selection_methods: string[];
    default_score_weights: Record<string, number>;
    minimum_repetitions: number;
    requires_same_fixture: boolean;
    requires_hidden_holdout: boolean;
    requires_ablation: boolean;
    automatic_production_promotion: boolean;
  };
  truth: Record<string, boolean | number>;
};

export const BUDDY_LEARNING_STRATEGIES = learningStrategies as LearningStrategyCatalog;

const sourceKinds = ["repository", "model_weights", "package"] as const;
const weightFormats = ["safetensors", "gguf", "onnx", "tflite"] as const;
const floatingRevisions = new Set(["main", "master", "latest", "head", "stable", "dev", "develop"]);

export const openModelComparisonRequestSchema = z.object({
  modelFamilyIds: z.array(z.string().min(1).max(80)).max(12).default([]),
  frontierTargets: z.array(z.object({
    referenceId: z.string().min(1).max(80),
    exactModelId: z.string().trim().min(3).max(160).regex(/^[A-Za-z0-9][A-Za-z0-9._:/-]*$/),
  }).strict()).max(8).default([]),
  taskIds: z.array(z.string().min(1).max(80)).min(1).max(10),
  repetitions: z.number().int().min(1).max(3).default(1),
  localRuntimeId: z.string().min(1).max(80).optional(),
  maxBudgetUsd: z.number().min(0).max(10_000).default(0),
  allowExternalNetwork: z.boolean().default(false),
  approvePaidAdaptersForThisRun: z.boolean().default(false),
}).strict().superRefine((value, context) => {
  if (new Set(value.modelFamilyIds).size + value.frontierTargets.length < 2) {
    context.addIssue({ code: z.ZodIssueCode.custom, message: "Select at least two open or frontier targets." });
  }
});

export const openSourceSandboxPlanRequestSchema = z.object({
  sourceKind: z.enum(sourceKinds),
  sourceUrl: z.string().url().max(2_048),
  revision: z.string().min(4).max(160).regex(/^[A-Za-z0-9][A-Za-z0-9._/+:-]*$/),
  declaredLicense: z.string().min(2).max(120),
  objective: z.string().min(10).max(2_000),
  ownerConfirmsRights: z.boolean(),
  allowNetworkDuringBuild: z.boolean().default(false),
  trustRemoteCode: z.boolean().default(false),
  weightFormat: z.enum(weightFormats).optional(),
  learnerLevel: z.enum(["guided", "builder", "contributor"]).default("builder"),
  learningGoals: z.array(z.string().trim().min(3).max(160)).max(10).default([]),
  contributionMode: z.enum(["evidence_only", "issue_draft", "patch_packet", "evaluation_dataset"]).default("evidence_only"),
  limits: z.object({
    timeoutSeconds: z.number().int().min(30).max(7_200).default(900),
    cpuCores: z.number().int().min(1).max(32).default(2),
    memoryMb: z.number().int().min(512).max(131_072).default(4_096),
    diskMb: z.number().int().min(1_024).max(524_288).default(20_480),
    processCount: z.number().int().min(8).max(512).default(64),
  }).strict(),
}).strict();

export const repositoryTrackingPlanRequestSchema = z.object({
  sourceUrl: z.string().url().max(2_048),
  revision: z.string().min(4).max(160).regex(/^[A-Za-z0-9][A-Za-z0-9._/+:-]*$/),
  declaredLicense: z.string().min(2).max(120),
  cadence: z.enum(["manual", "daily", "weekly"]).default("weekly"),
  interests: z.array(z.enum(["releases", "license", "security", "tests", "issues", "models"])).min(1).max(6),
  notificationChannels: z.array(z.enum(["in_app", "email"])).min(1).max(2).default(["in_app"]),
  ownerConfirmsRights: z.boolean(),
}).strict();

export const buddyOpenCoreManifestRequestSchema = z.object({
  releaseId: z.string().trim().regex(/^[a-z0-9][a-z0-9._-]{2,79}$/),
  modelName: z.string().trim().min(3).max(120),
  distributionMode: z.enum(["code_version", "open_source", "open_weights", "private"]),
  architectureProfileId: z.enum(["dense_edge", "dense_general", "sparse_moe", "sparse_moe_mtp", "distilled_specialist"]),
  exactSourceUrl: z.string().url().max(2048),
  immutableRevision: z.string().trim().min(7).max(160).regex(/^[A-Za-z0-9][A-Za-z0-9._/+:-]*$/),
  declaredLicense: z.string().trim().min(2).max(160),
  parameterBillions: z.number().positive().max(10_000),
  activeParameterBillions: z.number().positive().max(10_000),
  contextTokens: z.number().int().min(2_048).max(10_000_000),
  weightFormat: z.enum(["safetensors", "gguf", "onnx"]),
  quantization: z.enum(["bf16", "fp16", "fp8_block", "int8", "int4", "gguf_q8", "gguf_q6", "gguf_q5", "gguf_q4"]),
  runtimeIds: z.array(z.enum(["llama-cpp", "mlx", "transformers", "vllm", "ollama"])).min(1).max(5),
  capabilityTracks: z.array(z.enum(["reasoning", "coding", "tool_use", "long_context", "multilingual", "vision", "speech_audio", "embeddings", "reranking", "agent_workflows"])).min(1).max(10),
  sourceAndLicenseReviewed: z.boolean().default(false),
  checksumsVerified: z.boolean().default(false),
  sandboxLoadPassed: z.boolean().default(false),
  sameFixtureBenchmarksPassed: z.boolean().default(false),
  holdoutPassed: z.boolean().default(false),
  securityReviewPassed: z.boolean().default(false),
}).strict().superRefine((value, context) => {
  if (value.activeParameterBillions > value.parameterBillions) context.addIssue({ code: z.ZodIssueCode.custom, message: "Active parameters cannot exceed total parameters." });
  if (value.architectureProfileId.startsWith("sparse_moe") && value.activeParameterBillions >= value.parameterBillions) context.addIssue({ code: z.ZodIssueCode.custom, message: "Sparse MoE releases must activate fewer parameters than their total." });
  if (!value.architectureProfileId.startsWith("sparse_moe") && value.activeParameterBillions !== value.parameterBillions) context.addIssue({ code: z.ZodIssueCode.custom, message: "Dense and distilled profiles must report equal total and active parameters." });
});

const learningScoresSchema = z.array(z.number().min(0).max(1)).min(3).max(20);
export const buddyLearningEvidenceRequestSchema = z.object({
  cycleId: z.string().trim().regex(/^[a-z0-9][a-z0-9._-]{2,79}$/),
  baseReleaseId: z.string().trim().min(3).max(120),
  capabilityId: z.string().trim().min(3).max(120),
  method: z.string().trim().min(3).max(120),
  sourceManifestSha256: z.string().regex(/^[a-f0-9]{64}$/i),
  trainingArtifactSha256: z.string().regex(/^[a-f0-9]{64}$/i),
  graderVersion: z.string().trim().min(3).max(120),
  baselineScores: learningScoresSchema,
  hiddenHoldoutBeforeScores: learningScoresSchema,
  hiddenHoldoutAfterScores: learningScoresSchema,
  regressionBeforeScores: learningScoresSchema,
  regressionAfterScores: learningScoresSchema,
  safetyBeforeScores: learningScoresSchema,
  safetyAfterScores: learningScoresSchema,
  approvedSourcesOnly: z.boolean(),
  licenseAndProvenanceVerified: z.boolean(),
  privateDataExcludedOrConsented: z.boolean(),
  sandboxTrainingPassed: z.boolean(),
  ownerReleaseApproved: z.boolean().default(false),
}).strict().superRefine((value, context) => {
  if (!BUDDY_LEARNING_STRATEGIES.techniques.some((item) => item.id === value.method)) {
    context.addIssue({ code: z.ZodIssueCode.custom, message: `Unknown Buddy learning technique: ${value.method}` });
  }
});

const learningObjectives = ["reasoning_quality", "study_efficiency", "low_compute", "multilingual_quality", "readability", "continual_retention", "tool_use", "alignment"] as const;
const computeLevels = ["low", "medium", "high", "very_high"] as const;

export const buddyLearningStudyRequestSchema = z.object({
  studyId: z.string().trim().regex(/^[a-z0-9][a-z0-9._-]{2,79}$/),
  baseReleaseId: z.string().trim().min(3).max(120),
  capabilityId: z.string().trim().min(3).max(120),
  objective: z.enum(learningObjectives),
  techniqueIds: z.array(z.string().trim().min(3).max(120)).max(12).default([]),
  maximumCompute: z.enum(computeLevels).default("medium"),
  seeds: z.array(z.number().int().min(1).max(2_147_483_647)).min(3).max(10).default([1729, 2718, 31415]),
  maximumTechniques: z.number().int().min(2).max(12).default(6),
  maximumTrials: z.number().int().min(6).max(120).default(36),
  maximumGpuHours: z.number().min(0).max(1_000_000).default(0),
  maximumCostUsd: z.number().min(0).max(10_000_000).default(0),
  datasetManifestSha256: z.string().regex(/^[a-f0-9]{64}$/i),
  hiddenHoldoutManifestSha256: z.string().regex(/^[a-f0-9]{64}$/i),
  allowExternalNetwork: z.boolean().default(false),
  ownerApprovedSandboxTraining: z.boolean().default(false),
}).strict().superRefine((value, context) => {
  if (new Set(value.seeds).size !== value.seeds.length) context.addIssue({ code: z.ZodIssueCode.custom, message: "Study seeds must be unique." });
  if (new Set(value.techniqueIds).size !== value.techniqueIds.length) context.addIssue({ code: z.ZodIssueCode.custom, message: "Study technique ids must be unique." });
  if (value.datasetManifestSha256.toLowerCase() === value.hiddenHoldoutManifestSha256.toLowerCase()) context.addIssue({ code: z.ZodIssueCode.custom, message: "Training and hidden-holdout manifests must be different." });
});

const learningTrialResultSchema = z.object({
  techniqueId: z.string().trim().min(3).max(120),
  seed: z.number().int().min(1).max(2_147_483_647),
  artifactSha256: z.string().regex(/^[a-f0-9]{64}$/i),
  sandboxPassed: z.boolean(),
  qualityScore: z.number().min(0).max(1),
  retentionScore: z.number().min(0).max(1),
  safetyScore: z.number().min(0).max(1),
  readabilityScore: z.number().min(0).max(1),
  targetLanguageRatio: z.number().min(0).max(1),
  repetitionRate: z.number().min(0).max(1),
  formatValidityScore: z.number().min(0).max(1),
  independentGraderAgreement: z.number().min(0).max(1),
  holdoutContaminationRate: z.number().min(0).max(1),
  privateDataLeakRate: z.number().min(0).max(1),
  groundedClaimRate: z.number().min(0).max(1),
  latencyRegressionRatio: z.number().min(-1).max(100),
  costRegressionRatio: z.number().min(-1).max(100),
  latencyMs: z.number().min(0).max(86_400_000),
  gpuHours: z.number().min(0).max(1_000_000),
  costUsd: z.number().min(0).max(10_000_000),
}).strict();

export const buddyLearningStudyResultsSchema = z.object({
  studyId: z.string().trim().regex(/^[a-z0-9][a-z0-9._-]{2,79}$/),
  studyManifestSha256: z.string().regex(/^[a-f0-9]{64}$/i),
  hiddenHoldoutManifestSha256: z.string().regex(/^[a-f0-9]{64}$/i),
  baselineQualityScore: z.number().min(0).max(1),
  results: z.array(learningTrialResultSchema).min(6).max(240),
  ownerReleaseApproved: z.boolean().default(false),
}).strict().superRefine((value, context) => {
  const trialKeys = value.results.map((item) => `${item.techniqueId}:${item.seed}`);
  if (new Set(trialKeys).size !== trialKeys.length) context.addIssue({ code: z.ZodIssueCode.custom, message: "Each technique and seed pair must be unique." });
  if (value.studyManifestSha256.toLowerCase() === value.hiddenHoldoutManifestSha256.toLowerCase()) context.addIssue({ code: z.ZodIssueCode.custom, message: "Study and hidden-holdout manifests must be different." });
});

export type OpenModelComparisonRequest = z.infer<typeof openModelComparisonRequestSchema>;
export type OpenSourceSandboxPlanRequest = z.infer<typeof openSourceSandboxPlanRequestSchema>;
export type RepositoryTrackingPlanRequest = z.infer<typeof repositoryTrackingPlanRequestSchema>;
export type BuddyOpenCoreManifestRequest = z.infer<typeof buddyOpenCoreManifestRequestSchema>;
export type BuddyLearningEvidenceRequest = z.infer<typeof buddyLearningEvidenceRequestSchema>;
export type BuddyLearningStudyRequest = z.infer<typeof buddyLearningStudyRequestSchema>;
export type BuddyLearningStudyResults = z.infer<typeof buddyLearningStudyResultsSchema>;

const mean = (scores: number[]) => scores.reduce((sum, score) => sum + score, 0) / scores.length;
const computeRank = new Map(computeLevels.map((level, index) => [level, index]));

function techniquePriority(technique: LearningTechnique, objective: string) {
  let score = technique.objectives.includes(objective) ? 10 : 0;
  if (technique.objectives.includes("study_efficiency")) score += 3;
  if (technique.compute === "low") score += 3;
  if (technique.compute === "medium") score += 2;
  if (technique.category === "experiment_optimization") score -= 1;
  return score;
}

export function createBuddyLearningStudy(input: BuddyLearningStudyRequest) {
  const request = buddyLearningStudyRequestSchema.parse(input);
  const byId = new Map(BUDDY_LEARNING_STRATEGIES.techniques.map((item) => [item.id, item]));
  const unknown = request.techniqueIds.filter((id) => !byId.has(id));
  if (unknown.length) throw new Error(`Unknown Buddy learning techniques: ${unknown.join(", ")}`);
  const computeCeiling = computeRank.get(request.maximumCompute)!;
  const eligible = BUDDY_LEARNING_STRATEGIES.techniques.filter((item) => computeRank.get(item.compute)! <= computeCeiling);
  const requested = request.techniqueIds.length ? request.techniqueIds.map((id) => byId.get(id)!) : eligible
    .filter((item) => item.objectives.includes(request.objective))
    .sort((left, right) => techniquePriority(right, request.objective) - techniquePriority(left, request.objective) || left.id.localeCompare(right.id));
  const blockedByCompute = requested.filter((item) => computeRank.get(item.compute)! > computeCeiling);
  if (blockedByCompute.length) throw new Error(`Techniques exceed the ${request.maximumCompute} compute ceiling: ${blockedByCompute.map((item) => item.id).join(", ")}`);
  const maximumByTrials = Math.floor(request.maximumTrials / request.seeds.length);
  const techniques = requested.slice(0, Math.min(request.maximumTechniques, maximumByTrials));
  if (techniques.length < 2) throw new Error("The study budget must cover at least two techniques across every seed.");
  if (request.techniqueIds.length && techniques.length !== request.techniqueIds.length) throw new Error("The trial budget must cover every selected technique across every seed.");
  const trialCount = techniques.length * request.seeds.length;
  const trials = techniques.flatMap((technique) => request.seeds.map((seed) => ({
    trialId: `${request.studyId}-${technique.id}-${seed}`,
    techniqueId: technique.id,
    seed,
    stage: technique.stage,
    compute: technique.compute,
    status: "scheduled_not_executed",
    isolatedSandboxRequired: true,
    maximumGpuHours: request.maximumGpuHours / trialCount,
    maximumCostUsd: request.maximumCostUsd / trialCount,
  })));
  return {
    schema: "dreamco.buddy_learning_study.v1",
    studyId: request.studyId,
    baseReleaseId: request.baseReleaseId,
    capabilityId: request.capabilityId,
    objective: request.objective,
    status: !request.ownerApprovedSandboxTraining ? "owner_training_approval_required" : request.maximumGpuHours <= 0 ? "execution_resources_required" : "sandbox_execution_adapter_required",
    datasetManifestSha256: request.datasetManifestSha256,
    hiddenHoldoutManifestSha256: request.hiddenHoldoutManifestSha256,
    techniques,
    trials,
    trialCount,
    sameFixturesAcrossTechniques: true,
    controlledAblationRequired: true,
    failureControls: BUDDY_LEARNING_STRATEGIES.failure_controls,
    scoring: BUDDY_LEARNING_STRATEGIES.study_optimizer.default_score_weights,
    network: request.allowExternalNetwork ? "allowlisted_sources_only" : "off",
    automaticTrainingStarted: false,
    productionWeightsModified: false,
    automaticProductionPromotion: false,
  } as const;
}

type LearningTrialResult = z.infer<typeof learningTrialResultSchema>;

export function evaluateBuddyLearningStudy(input: BuddyLearningStudyResults) {
  const request = buddyLearningStudyResultsSchema.parse(input);
  const knownIds = new Set(BUDDY_LEARNING_STRATEGIES.techniques.map((item) => item.id));
  const unknown = [...new Set(request.results.filter((item) => !knownIds.has(item.techniqueId)).map((item) => item.techniqueId))];
  if (unknown.length) throw new Error(`Unknown Buddy learning techniques: ${unknown.join(", ")}`);
  const groups = new Map<string, LearningTrialResult[]>();
  for (const result of request.results) groups.set(result.techniqueId, [...(groups.get(result.techniqueId) ?? []), result]);
  const minimumRepetitions = BUDDY_LEARNING_STRATEGIES.study_optimizer.minimum_repetitions;
  const weights = BUDDY_LEARNING_STRATEGIES.study_optimizer.default_score_weights;
  const candidates = [...groups.entries()].map(([techniqueId, results]) => {
    const average = (field: keyof LearningTrialResult) => mean(results.map((item) => Number(item[field])));
    const metrics: Record<string, number> = {
      quality_score: average("qualityScore"),
      retention_score: Math.min(...results.map((item) => item.retentionScore)),
      safety_score: Math.min(...results.map((item) => item.safetyScore)),
      readability_score: Math.min(...results.map((item) => item.readabilityScore)),
      target_language_ratio: Math.min(...results.map((item) => item.targetLanguageRatio)),
      repetition_rate: Math.max(...results.map((item) => item.repetitionRate)),
      format_validity_score: Math.min(...results.map((item) => item.formatValidityScore)),
      independent_grader_agreement: Math.min(...results.map((item) => item.independentGraderAgreement)),
      holdout_contamination_rate: Math.max(...results.map((item) => item.holdoutContaminationRate)),
      private_data_leak_rate: Math.max(...results.map((item) => item.privateDataLeakRate)),
      grounded_claim_rate: Math.min(...results.map((item) => item.groundedClaimRate)),
      latency_regression_ratio: Math.max(...results.map((item) => item.latencyRegressionRatio)),
      cost_regression_ratio: Math.max(...results.map((item) => item.costRegressionRatio)),
      latency_ms: average("latencyMs"),
      gpu_hours: results.reduce((sum, item) => sum + item.gpuHours, 0),
      cost_usd: results.reduce((sum, item) => sum + item.costUsd, 0),
    };
    const failures = BUDDY_LEARNING_STRATEGIES.failure_controls.filter((control) => {
      const value = metrics[control.metric];
      return control.direction === "minimum" ? value < control.threshold : value > control.threshold;
    }).map((control) => ({ id: control.id, action: control.action, measured: metrics[control.metric], threshold: control.threshold }));
    if (results.some((item) => !item.sandboxPassed)) failures.push({ id: "sandbox_failure", action: "reject_candidate", measured: 0, threshold: 1 });
    if (new Set(results.map((item) => item.seed)).size < minimumRepetitions) failures.push({ id: "insufficient_repeat_runs", action: "reject_candidate", measured: results.length, threshold: minimumRepetitions });
    const qualityGain = metrics.quality_score - request.baselineQualityScore;
    if (qualityGain < OPEN_MODEL_CATALOG.buddy_open_core.learning_system.promotion_thresholds.minimum_absolute_improvement) failures.push({ id: "insufficient_quality_gain", action: "reject_candidate", measured: qualityGain, threshold: OPEN_MODEL_CATALOG.buddy_open_core.learning_system.promotion_thresholds.minimum_absolute_improvement });
    const efficiencyScore = Math.max(0, qualityGain) * weights.quality_gain
      + metrics.retention_score * weights.retention
      + metrics.safety_score * weights.safety
      + metrics.readability_score * weights.readability
      + metrics.target_language_ratio * weights.language_consistency
      + (1 - metrics.repetition_rate) * weights.low_repetition
      + (1 / (1 + metrics.cost_usd)) * weights.cost_efficiency
      + (1 / (1 + metrics.latency_ms / 1000)) * weights.latency_efficiency;
    return { techniqueId, repetitions: results.length, qualityGain, efficiencyScore, metrics, failures, eligible: failures.length === 0 };
  }).sort((left, right) => Number(right.eligible) - Number(left.eligible) || right.efficiencyScore - left.efficiencyScore || left.techniqueId.localeCompare(right.techniqueId));
  const eligibleCandidates = candidates.filter((item) => item.eligible);
  const dominates = (left: typeof candidates[number], right: typeof candidates[number]) => {
    const leftValues = [left.metrics.quality_score, left.metrics.retention_score, left.metrics.safety_score, left.metrics.readability_score, left.metrics.target_language_ratio, 1 - left.metrics.repetition_rate, -left.metrics.cost_usd, -left.metrics.latency_ms];
    const rightValues = [right.metrics.quality_score, right.metrics.retention_score, right.metrics.safety_score, right.metrics.readability_score, right.metrics.target_language_ratio, 1 - right.metrics.repetition_rate, -right.metrics.cost_usd, -right.metrics.latency_ms];
    return leftValues.every((value, index) => value >= rightValues[index]) && leftValues.some((value, index) => value > rightValues[index]);
  };
  const paretoFrontier = eligibleCandidates.filter((candidate) => !eligibleCandidates.some((other) => other.techniqueId !== candidate.techniqueId && dominates(other, candidate)));
  const winner = [...paretoFrontier].sort((left, right) => right.efficiencyScore - left.efficiencyScore || left.techniqueId.localeCompare(right.techniqueId))[0] ?? null;
  return {
    schema: "dreamco.buddy_learning_study_evaluation.v1",
    studyId: request.studyId,
    status: winner ? (request.ownerReleaseApproved ? "winning_candidate_owner_approved_signed_release_required" : "winning_candidate_owner_approval_required") : "no_candidate_passed",
    baselineQualityScore: request.baselineQualityScore,
    candidates,
    paretoFrontier,
    winner,
    studyManifestSha256: request.studyManifestSha256,
    hiddenHoldoutManifestSha256: request.hiddenHoldoutManifestSha256,
    trainingPerformedByThisEvaluation: false,
    productionWeightsModified: false,
    releasePerformed: false,
  } as const;
}

export function evaluateBuddyLearningEvidence(input: BuddyLearningEvidenceRequest) {
  const request = buddyLearningEvidenceRequestSchema.parse(input);
  const thresholds = OPEN_MODEL_CATALOG.buddy_open_core.learning_system.promotion_thresholds;
  const baseline = mean(request.baselineScores);
  const holdoutBefore = mean(request.hiddenHoldoutBeforeScores);
  const holdoutAfter = mean(request.hiddenHoldoutAfterScores);
  const regressionBefore = mean(request.regressionBeforeScores);
  const regressionAfter = mean(request.regressionAfterScores);
  const safetyBefore = mean(request.safetyBeforeScores);
  const safetyAfter = mean(request.safetyAfterScores);
  const gates = {
    failing_baseline_recorded: baseline < thresholds.minimum_holdout_score,
    approved_sources_only: request.approvedSourcesOnly,
    license_and_provenance_verified: request.licenseAndProvenanceVerified,
    private_data_excluded_or_consented: request.privateDataExcludedOrConsented,
    sandbox_training_passed: request.sandboxTrainingPassed,
    hidden_holdout_improved: holdoutAfter - holdoutBefore >= thresholds.minimum_absolute_improvement,
    holdout_threshold_met: holdoutAfter >= thresholds.minimum_holdout_score,
    regression_within_limit: regressionBefore - regressionAfter <= thresholds.maximum_regression,
    safety_not_regressed: safetyAfter >= safetyBefore,
    repeated_runs_present: [request.baselineScores, request.hiddenHoldoutBeforeScores, request.hiddenHoldoutAfterScores, request.regressionBeforeScores, request.regressionAfterScores, request.safetyBeforeScores, request.safetyAfterScores].every((scores) => scores.length >= thresholds.minimum_repetitions),
  };
  const improvementProven = Object.values(gates).every(Boolean);
  return {
    schema: "dreamco.buddy_learning_evidence.v1",
    cycleId: request.cycleId,
    baseReleaseId: request.baseReleaseId,
    capabilityId: request.capabilityId,
    method: request.method,
    status: improvementProven ? (request.ownerReleaseApproved ? "approved_release_candidate" : "improvement_proven_owner_approval_required") : "learning_evidence_failed",
    scores: { baseline, hiddenHoldoutBefore: holdoutBefore, hiddenHoldoutAfter: holdoutAfter, absoluteImprovement: holdoutAfter - holdoutBefore, regressionBefore, regressionAfter, safetyBefore, safetyAfter },
    gates,
    evidence: { sourceManifestSha256: request.sourceManifestSha256, trainingArtifactSha256: request.trainingArtifactSha256, graderVersion: request.graderVersion },
    improvementProven,
    promotedToUsers: false,
    globalWeightsModified: false,
    nextGate: improvementProven ? (request.ownerReleaseApproved ? "signed_reversible_release" : "owner_release_approval") : Object.entries(gates).find(([, passed]) => !passed)?.[0] ?? "review_failed_evidence",
  } as const;
}

export function createBuddyOpenCoreManifest(input: BuddyOpenCoreManifestRequest) {
  const request = buddyOpenCoreManifestRequestSchema.parse(input);
  const source = validatedSourceUrl(request.exactSourceUrl);
  if (floatingRevisions.has(request.immutableRevision.toLowerCase())) throw new Error("Buddy Open Core requires an immutable model revision.");
  const profile = OPEN_MODEL_CATALOG.buddy_open_core.architecture_profiles.find((item) => item.id === request.architectureProfileId)!;
  const distribution = OPEN_MODEL_CATALOG.buddy_open_core.distribution_modes.find((item) => item.id === request.distributionMode)!;
  const evidence = {
    source_and_license_reviewed: request.sourceAndLicenseReviewed,
    checksums_verified: request.checksumsVerified,
    sandbox_load_passed: request.sandboxLoadPassed,
    same_fixture_benchmarks_passed: request.sameFixtureBenchmarksPassed,
    hidden_holdout_passed: request.holdoutPassed,
    security_review_passed: request.securityReviewPassed,
  };
  const passed = Object.values(evidence).filter(Boolean).length;
  return {
    schema: "dreamco.buddy_open_core_manifest.v1",
    releaseId: request.releaseId,
    modelName: request.modelName,
    distribution,
    status: passed === Object.keys(evidence).length ? "release_candidate_owner_review_required" : "evidence_gates_remaining",
    architecture: { ...profile, parameterBillions: request.parameterBillions, activeParameterBillions: request.activeParameterBillions, contextTokens: request.contextTokens },
    artifact: { source: source.toString(), revision: request.immutableRevision, declaredLicense: request.declaredLicense, weightFormat: request.weightFormat, quantization: request.quantization },
    runtimes: [...new Set(request.runtimeIds)],
    capabilities: [...new Set(request.capabilityTracks)],
    apiCompatibility: OPEN_MODEL_CATALOG.buddy_open_core.api_compatibility,
    evidence: { ...evidence, passed, total: Object.keys(evidence).length },
    trainedWeightsCreatedByThisRequest: false,
    inferenceStartedByThisRequest: false,
    productionReleaseCreated: false,
    publicationPerformed: false,
    nextGate: passed === Object.keys(evidence).length ? "owner_review_and_signed_reversible_release" : OPEN_MODEL_CATALOG.buddy_open_core.release_gates.find((_gate, index) => index >= passed) ?? "complete_remaining_release_gates",
  } as const;
}

function unique<T>(values: T[]) {
  return [...new Set(values)];
}

export function createOpenModelComparisonPlan(input: OpenModelComparisonRequest) {
  const request = openModelComparisonRequestSchema.parse(input);
  const modelIds = unique(request.modelFamilyIds);
  const frontierMap = new Map(OPEN_MODEL_CATALOG.frontier_references.map((target) => [target.id, target]));
  const frontierTargets = request.frontierTargets.map((target) => {
    const reference = frontierMap.get(target.referenceId);
    if (!reference) throw new Error(`Unknown frontier reference: ${target.referenceId}`);
    return { ...reference, exactModelId: target.exactModelId };
  });
  const taskIds = unique(request.taskIds);
  const modelMap = new Map(OPEN_MODEL_CATALOG.model_families.map((model) => [model.id, model]));
  const taskMap = new Map(OPEN_MODEL_CATALOG.coding_tasks.map((task) => [task.id, task]));
  const models = modelIds.map((id) => {
    const model = modelMap.get(id);
    if (!model) throw new Error(`Unknown open-model family: ${id}`);
    return model;
  });
  const tasks = taskIds.map((id) => {
    const task = taskMap.get(id);
    if (!task) throw new Error(`Unknown coding task: ${id}`);
    return task;
  });
  const status = frontierTargets.length && !request.allowExternalNetwork
    ? "frontier_network_approval_required"
    : frontierTargets.length && (!request.approvePaidAdaptersForThisRun || request.maxBudgetUsd <= 0)
      ? "frontier_budget_approval_required"
      : request.allowExternalNetwork
        ? "live_sandbox_and_adapters_required"
        : "local_evaluation_plan_ready";
  const targetCount = models.length + frontierTargets.length;
  return {
    schema: "dreamco.buddy_open_model_comparison_plan.v2",
    status,
    modelCount: targetCount,
    openModelCount: models.length,
    frontierTargetCount: frontierTargets.length,
    taskCount: tasks.length,
    totalCases: targetCount * tasks.length * request.repetitions,
    repetitions: request.repetitions,
    models: models.map((model) => ({
      id: model.id,
      label: model.label,
      developer: model.developer,
      developerRegion: model.developer_region,
      access: model.access,
      license: model.license,
      officialSource: model.official_source,
    })),
    frontierTargets: frontierTargets.map((target) => ({
      referenceId: target.id,
      exactModelId: target.exactModelId,
      label: target.label,
      provider: target.provider,
      access: target.access,
      officialSource: target.official_source,
      adapterStatus: target.adapter_status,
    })),
    tasks,
    localRuntimeId: request.localRuntimeId ?? null,
    externalNetworkApprovedForThisRun: request.allowExternalNetwork,
    paidAdaptersApprovedForThisRun: request.approvePaidAdaptersForThisRun,
    maxBudgetUsd: request.maxBudgetUsd,
    liveExecutionPerformed: false,
    scoring: {
      developerRegionUsedForScoring: false,
      groupingUnit: "exact model checkpoint",
      openAndFrontierComparedOnSameFixtures: models.length > 0 && frontierTargets.length > 0,
      rankingInputs: [
        "signed test results",
        "license fit",
        "hardware and energy use",
        "latency",
        "actual cost",
        "language coverage",
        "safety regressions",
      ],
    },
    evidenceRequired: OPEN_MODEL_CATALOG.evidence_fields,
  } as const;
}

export function createOpenSourceSandboxPlan(input: OpenSourceSandboxPlanRequest) {
  const request = openSourceSandboxPlanRequestSchema.parse(input);
  const source = new URL(request.sourceUrl);
  if (source.username || source.password || source.search || source.hash) {
    throw new Error("Source URLs must not contain credentials, query strings, or fragments.");
  }
  if (source.protocol !== "https:" || !OPEN_MODEL_CATALOG.open_source_sandbox.supported_hosts.includes(source.hostname)) {
    throw new Error("Source must use HTTPS on an approved open-source host.");
  }
  if (floatingRevisions.has(request.revision.toLowerCase())) {
    throw new Error("Pin an exact commit, immutable tag, or model revision instead of a floating branch.");
  }
  if (!request.ownerConfirmsRights) {
    throw new Error("The owner must confirm the source license and usage rights.");
  }
  if (request.trustRemoteCode) {
    throw new Error("Remote model code is disabled in Buddy sandboxes.");
  }
  if (request.sourceKind === "model_weights" && !request.weightFormat) {
    throw new Error("Model weights require an approved non-pickle weight format.");
  }
  if (request.sourceKind !== "model_weights" && request.weightFormat) {
    throw new Error("Weight format only applies to model-weight sources.");
  }
  return {
    schema: "dreamco.buddy_open_source_sandbox_plan.v1",
    status: request.allowNetworkDuringBuild ? "network_approval_and_sandbox_adapter_required" : "sandbox_adapter_required",
    source: {
      kind: request.sourceKind,
      url: source.toString(),
      revision: request.revision,
      declaredLicense: request.declaredLicense,
      weightFormat: request.weightFormat ?? null,
    },
    objective: request.objective,
    liveExecutionPerformed: false,
    sandboxAdapterRequired: true,
    controls: {
      sourceMount: "read_only",
      workingDirectory: "ephemeral",
      user: "non_root",
      hostSockets: "none",
      secrets: "none",
      network: request.allowNetworkDuringBuild ? "one_run_approval_required" : "off",
      trustRemoteCode: false,
      limits: request.limits,
      outputs: "quarantined_until_tests_and_owner_review",
    },
    stages: [
      "verify exact revision, publisher, license, and file hashes",
      "scan secrets, malware, unsafe serialization, dependencies, and source provenance",
      "generate SBOM and open-source security scorecard evidence",
      "build in a disposable sandbox with locked dependencies",
      "run upstream, compatibility, mutation, security, and adversarial tests",
      "record logs, resource use, failures, and reproducible artifact hashes",
      "show source, behavior, license, and dependency diffs",
      "request owner approval for a reversible integration checkpoint",
    ],
    academy: {
      learnerLevel: request.learnerLevel,
      learningGoals: request.learningGoals,
      lessonStages: OPEN_MODEL_CATALOG.sandbox_academy.lesson_stages,
      evidenceJournal: [
        "architecture notes",
        "commands and environment fingerprints",
        "failed and passing test evidence",
        "plain-language explanation of each change",
        "reflection and next-skill recommendation",
      ],
      buddyTrainingUse: "owner_private_retrieval_and_preference_learning_only_unless_separately_approved",
      automaticModelTraining: false,
      trainingDataPolicy: OPEN_MODEL_CATALOG.sandbox_academy.training_data_policy,
    },
    contribution: {
      mode: request.contributionMode,
      automaticUpstreamSubmission: false,
      ownerReviewRequired: true,
      packet: [
        "reproducible failing fixture",
        "minimal change or evaluation artifact",
        "license and contribution-guide check",
        "before and after benchmark evidence",
        "issue, documentation, or patch draft",
      ],
    },
    automaticMerge: false,
    automaticPublish: false,
  } as const;
}

function validatedSourceUrl(raw: string) {
  const source = new URL(raw);
  if (source.username || source.password || source.search || source.hash) {
    throw new Error("Source URLs must not contain credentials, query strings, or fragments.");
  }
  if (source.protocol !== "https:" || !OPEN_MODEL_CATALOG.open_source_sandbox.supported_hosts.includes(source.hostname)) {
    throw new Error("Source must use HTTPS on an approved open-source host.");
  }
  return source;
}

export function createRepositoryTrackingPlan(input: RepositoryTrackingPlanRequest) {
  const request = repositoryTrackingPlanRequestSchema.parse(input);
  const source = validatedSourceUrl(request.sourceUrl);
  if (floatingRevisions.has(request.revision.toLowerCase())) {
    throw new Error("Pin an exact starting revision instead of a floating branch.");
  }
  if (!request.ownerConfirmsRights) {
    throw new Error("Confirm the repository license and your right to evaluate it.");
  }
  return {
    schema: "dreamco.buddy_repository_tracking_plan.v1",
    status: request.cadence === "manual" ? "manual_tracking_ready" : "deployed_scheduler_required",
    repository: {
      url: source.toString(),
      startingRevision: request.revision,
      declaredLicense: request.declaredLicense,
    },
    cadence: request.cadence,
    interests: unique(request.interests),
    notificationChannels: unique(request.notificationChannels),
    storage: {
      metadataOnly: true,
      sourceCodeCopiedByTracker: false,
      credentialsStored: false,
      retentionDays: 90,
    },
    changeEvidence: [
      "old and new exact revision",
      "release and changelog links",
      "license and model-card diff",
      "security advisory references",
      "upstream test status",
      "local sandbox compatibility status",
    ],
    nextCheckScheduled: false,
    deployedSchedulerRequired: request.cadence !== "manual",
    automaticPullOrExecution: false,
    automaticIssueOrPatchSubmission: false,
  } as const;
}
