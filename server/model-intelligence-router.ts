import { readFileSync } from "node:fs";
import { resolve } from "node:path";

import { z } from "zod";

import { MODEL_BENCHMARK_TARGETS, MODEL_BENCHMARK_TARGET_COUNT } from "@shared/model-benchmark-targets";

type ManifestProvider = {
  id: string;
  name: string;
  connector: string;
  official_catalog: string;
  secret_refs: string[];
  protocols: string[];
  server_tools: string[];
};

type ManifestModel = {
  id: string;
  provider: string;
  class: string;
  exact_model_id: string | null;
  modalities: string[];
  strengths: string[];
  tools: string[];
  context_tokens: number | null;
  weight_access: string;
  license: string;
  evidence: string;
};

type ModelCapabilityManifest = {
  schema: string;
  snapshot_date: string;
  routing_dimensions: string[];
  providers: ManifestProvider[];
  models: ManifestModel[];
};

export const modelIntelligenceRequestSchema = z.object({
  objective: z.string().trim().min(3).max(4000),
  requiredCapabilities: z.array(z.string().trim().min(2).max(120)).max(30).default([]),
  requiredTools: z.array(z.string().trim().min(2).max(120)).max(30).default([]),
  requiredModalities: z.array(z.string().trim().min(2).max(80)).max(12).default([]),
  minimumContextTokens: z.number().int().nonnegative().max(20_000_000).default(0),
  preferOpenWeight: z.boolean().default(false),
  requireOpenWeight: z.boolean().default(false),
  preferLocal: z.boolean().default(false),
  qualityPriority: z.number().min(0).max(1).default(1),
  costPriority: z.number().min(0).max(1).default(0.25),
  latencyPriority: z.number().min(0).max(1).default(0.25),
  privacyPriority: z.number().min(0).max(1).default(0.35),
  allowPaid: z.boolean().default(false),
  maxCandidates: z.number().int().min(1).max(20).default(8),
}).strict();

export type ModelIntelligenceRequest = z.infer<typeof modelIntelligenceRequestSchema>;

let manifestCache: ModelCapabilityManifest | undefined;

export function getModelCapabilityManifest(path = resolve(process.cwd(), "config", "model-capability-manifest.json")) {
  manifestCache ??= JSON.parse(readFileSync(path, "utf8")) as ModelCapabilityManifest;
  return manifestCache;
}

function norm(value: string) {
  return value.toLowerCase().replace(/[^a-z0-9]+/g, " ").trim();
}

function tokenSet(value: string) {
  return new Set(norm(value).split(/\s+/).filter((token) => token.length >= 3));
}

function tokenOverlap(left: Set<string>, right: Set<string>) {
  let count = 0;
  for (const token of left) if (right.has(token)) count += 1;
  return count;
}

function configured(provider: ManifestProvider | undefined, env: NodeJS.ProcessEnv) {
  if (!provider) return false;
  if (!provider.secret_refs.length) return true;
  return provider.secret_refs.some((key) => Boolean(env[key]?.trim()));
}

function isOpenWeight(model: ManifestModel) {
  return ["open_weight", "open_weight_base", "weights_available"].includes(model.weight_access);
}

function localCapable(model: ManifestModel) {
  return isOpenWeight(model) || ["meta", "open_weight_local"].includes(model.provider);
}

function modelSearchText(model: ManifestModel, provider?: ManifestProvider) {
  return [
    model.id,
    model.provider,
    model.class,
    model.exact_model_id || "",
    ...model.strengths,
    ...model.tools,
    ...model.modalities,
    provider?.name || "",
    ...(provider?.server_tools || []),
  ].join(" ");
}

function scoreModel(
  model: ManifestModel,
  provider: ManifestProvider | undefined,
  request: ModelIntelligenceRequest,
  env: NodeJS.ProcessEnv,
) {
  const objectiveTokens = tokenSet(`${request.objective} ${request.requiredCapabilities.join(" ")}`);
  const searchTokens = tokenSet(modelSearchText(model, provider));
  const taskMatches = tokenOverlap(objectiveTokens, searchTokens);
  const toolText = norm(`${model.tools.join(" ")} ${(provider?.server_tools || []).join(" ")}`);
  const modalityText = norm(model.modalities.join(" "));
  const toolMatches = request.requiredTools.filter((tool) => toolText.includes(norm(tool)));
  const modalityMatches = request.requiredModalities.filter((modality) => modalityText.includes(norm(modality)));
  const missingTools = request.requiredTools.filter((tool) => !toolMatches.includes(tool));
  const missingModalities = request.requiredModalities.filter((modality) => !modalityMatches.includes(modality));
  const contextFit = request.minimumContextTokens === 0 || (model.context_tokens || 0) >= request.minimumContextTokens;
  const openWeight = isOpenWeight(model);
  const canRunLocally = localCapable(model);
  const providerConfigured = configured(provider, env);

  // Quality dominates the score. Cost/latency/privacy are intentionally tie-breakers.
  const taskQualityScore = taskMatches * 20 * request.qualityPriority;
  const toolQualityScore = toolMatches.length * 32 * request.qualityPriority;
  const modalityQualityScore = modalityMatches.length * 28 * request.qualityPriority;
  const contextQualityScore = contextFit ? 18 * request.qualityPriority : -120;
  const evidenceScore = model.evidence.startsWith("official") ? 12 : 0;
  const exactModelScore = model.exact_model_id ? 8 : 0;

  let score = taskQualityScore + toolQualityScore + modalityQualityScore + contextQualityScore + evidenceScore + exactModelScore;

  if (missingTools.length) score -= missingTools.length * 90;
  if (missingModalities.length) score -= missingModalities.length * 80;
  if (request.requireOpenWeight && !openWeight) score -= 10_000;
  if (request.preferOpenWeight && openWeight) score += 16;
  if (request.preferLocal && canRunLocally) score += 16;

  // Secondary optimization only after quality/task fit.
  if (canRunLocally) {
    score += request.privacyPriority * 9;
    score += request.costPriority * 6;
  }
  if (model.strengths.some((strength) => /fast|throughput|latency/i.test(strength))) {
    score += request.latencyPriority * 6;
  }

  return {
    score: Number(score.toFixed(3)),
    taskMatches,
    toolMatches,
    modalityMatches,
    missingTools,
    missingModalities,
    contextFit,
    openWeight,
    localCapable: canRunLocally,
    providerConfigured,
  };
}

export function selectBestModelForTask(
  input: z.input<typeof modelIntelligenceRequestSchema>,
  env: NodeJS.ProcessEnv = process.env,
) {
  const request = modelIntelligenceRequestSchema.parse(input);
  const manifest = getModelCapabilityManifest();
  const providers = new Map(manifest.providers.map((provider) => [provider.id, provider]));

  const scored = manifest.models
    .map((model) => ({ model, provider: providers.get(model.provider) }))
    .map(({ model, provider }) => ({ model, provider, ...scoreModel(model, provider, request, env) }))
    .filter((candidate) => !request.requireOpenWeight || candidate.openWeight)
    .sort((a, b) => b.score - a.score || a.model.id.localeCompare(b.model.id));

  const candidates = scored.slice(0, request.maxCandidates).map((candidate, index) => {
    const paidProvider = candidate.model.weight_access === "closed" || candidate.model.license === "provider_terms";
    const approvalRequired = paidProvider && !request.allowPaid;
    const exactExecutionReady = Boolean(candidate.model.exact_model_id)
      && candidate.providerConfigured
      && !approvalRequired
      && candidate.contextFit
      && candidate.missingTools.length === 0
      && candidate.missingModalities.length === 0;

    return {
      rank: index + 1,
      modelId: candidate.model.id,
      exactModelId: candidate.model.exact_model_id,
      provider: candidate.provider?.name || candidate.model.provider,
      providerId: candidate.model.provider,
      class: candidate.model.class,
      strengths: candidate.model.strengths,
      tools: candidate.model.tools,
      modalities: candidate.model.modalities,
      contextTokens: candidate.model.context_tokens,
      weightAccess: candidate.model.weight_access,
      license: candidate.model.license,
      routingScore: candidate.score,
      taskMatchCount: candidate.taskMatches,
      matchedTools: candidate.toolMatches,
      matchedModalities: candidate.modalityMatches,
      missingTools: candidate.missingTools,
      missingModalities: candidate.missingModalities,
      contextFit: candidate.contextFit,
      providerConfigured: candidate.providerConfigured,
      paidApprovalRequired: approvalRequired,
      exactExecutionReady,
      officialCatalog: candidate.provider?.official_catalog || null,
    };
  });

  const winner = candidates[0] || null;
  return {
    schema: "dreamco.model_intelligence_selection.v1",
    objective: request.objective,
    catalogSnapshotDate: manifest.snapshot_date,
    benchmarkProgramTargetCount: MODEL_BENCHMARK_TARGET_COUNT,
    benchmarkProgramTargetsLoaded: MODEL_BENCHMARK_TARGETS.length,
    routingPolicy: "quality_first_then_tools_modalities_context_then_cost_latency_privacy",
    selected: winner,
    candidates,
    status: !winner
      ? "no_candidate"
      : winner.missingTools.length || winner.missingModalities.length || !winner.contextFit
        ? "best_known_candidate_has_requirement_gaps"
        : winner.paidApprovalRequired
          ? "best_model_found_paid_approval_required"
          : winner.providerConfigured
            ? "best_model_candidate_ready_for_live_benchmark"
            : winner.weightAccess === "open_weight"
              ? "best_open_weight_candidate_requires_runtime_configuration"
              : "best_model_candidate_requires_provider_configuration",
    truthContract: {
      bestMeansBestKnownFitNotPermanentUniversalBest: true,
      liveBenchmarkRequiredForProductionPromotion: true,
      currentCatalogRefreshRequiredBeforeExactExecution: true,
      qualityDominatesCostAndLatencyByDefault: true,
      paidExecutionRequiresApproval: true,
      noProviderCallExecutedBySelection: true,
    },
  } as const;
}
