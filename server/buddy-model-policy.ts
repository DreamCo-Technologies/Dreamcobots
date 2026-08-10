import { readFileSync } from "node:fs";
import { resolve } from "node:path";

import { z } from "zod";

import { MODEL_BENCHMARK_TARGETS } from "@shared/model-benchmark-targets";

type ModelConnector = {
  id: string;
  label: string;
  mode: "free" | "premium";
  protocol: string;
  implementation_status: "local_ready" | "adapter_implemented" | "contract_only";
  availability: string;
  secret_references: string[];
  task_types: string[];
};

type ModelRouterConfig = {
  schema: string;
  default_mode: "free";
  policy: Record<string, boolean>;
  connectors: ModelConnector[];
};

export const buddyModelRequestSchema = z.object({
  modelMode: z.enum(["free", "premium"]).default("free"),
  modelConnectorId: z.string().trim().regex(/^[a-z0-9_]{2,64}$/).optional(),
  selectedModelId: z.string().trim().regex(/^[A-Za-z0-9_.:/-]{1,120}$/).optional(),
  approvePaidModelForThisRequest: z.boolean().default(false),
}).strict();

export type BuddyModelRequest = z.infer<typeof buddyModelRequestSchema>;

const routingPrioritySchema = z.object({
  quality: z.number().min(0).max(1).default(0.7),
  cost: z.number().min(0).max(1).default(0.8),
  latency: z.number().min(0).max(1).default(0.5),
  privacy: z.number().min(0).max(1).default(0.7),
}).strict();

export const buddyModelSelectionRequestSchema = z.object({
  objective: z.string().trim().min(3).max(2_000),
  requiredCapabilities: z.array(z.string().trim().min(2).max(80)).max(20).default([]),
  preferredTier: z.enum(["free", "premium", "any"]).default("free"),
  priorities: routingPrioritySchema.default({
    quality: 0.7,
    cost: 0.8,
    latency: 0.5,
    privacy: 0.7,
  }),
  maxCandidates: z.number().int().min(1).max(20).default(5),
  allowDiscovery: z.boolean().default(true),
  approvePaidModelForThisRequest: z.boolean().default(false),
}).strict();

export type BuddyModelSelectionRequest = z.infer<typeof buddyModelSelectionRequestSchema>;

const TASK_SIGNALS = [
  { id: "coding", terms: ["code", "coding", "debug", "software", "app", "website", "repository", "test"] },
  { id: "reasoning", terms: ["reason", "math", "logic", "decide", "compare", "analyze"] },
  { id: "research", terms: ["research", "find sources", "cite", "citation", "literature", "fact check", "evidence"] },
  { id: "agents", terms: ["agent", "tool", "workflow", "automate", "autonomous"] },
  { id: "vision", terms: ["vision", "image understand", "photo inspect", "screenshot"] },
  { id: "image generation", terms: ["generate image", "create image", "illustration", "logo", "art"] },
  { id: "image editing", terms: ["edit image", "photo edit", "retouch", "inpaint", "photoshop"] },
  { id: "video", terms: ["video", "movie", "film", "animation", "short"] },
  { id: "voice and speech", terms: ["voice", "speech", "transcribe", "narrate", "call"] },
  { id: "music and audio", terms: ["music", "song", "audio", "sing", "rap"] },
  { id: "multilingual and translation", terms: ["translate", "translation", "multilingual", "localize", "language"] },
  { id: "safety and moderation", terms: ["safety", "moderate", "guardrail", "risk", "policy"] },
  { id: "ocr and documents", terms: ["ocr", "document", "pdf", "scan", "extract"] },
  { id: "search and retrieval", terms: ["retrieve", "retrieval", "knowledge base", "search", "rag"] },
  { id: "data analysis", terms: ["data", "analytics", "spreadsheet", "chart", "sql"] },
  { id: "embeddings", terms: ["embedding", "vector", "semantic"] },
  { id: "forecasting", terms: ["forecast", "predict", "time series"] },
  { id: "simulation", terms: ["simulation", "simulate", "game", "digital twin"] },
  { id: "3d and spatial", terms: ["3d", "spatial", "world", "scene", "modeling"] },
  { id: "accessibility", terms: ["accessibility", "accessible", "caption", "screen reader"] },
] as const;

const PROVIDER_CONNECTOR_IDS: Record<string, string> = {
  dreamco: "buddy_native",
  openai: "openai",
  anthropic: "anthropic",
  google: "google_gemini",
  xai: "xai",
  mistralai: "mistral",
  cohere: "cohere",
  deepseek: "deepseek",
  microsoft: "azure_foundry",
  amazon: "amazon_bedrock",
  huggingface: "huggingface",
  alibabacloud: "alibaba_model_studio",
  baidu: "baidu_qianfan",
  ollama: "local_open_model",
  nvidia: "nvidia_nim",
  groq: "groq",
  togetherai: "together_ai",
  fireworksai: "fireworks_ai",
  cerebras: "cerebras",
  replicate: "replicate",
  stabilityai: "stability_ai",
  blackforestlabs: "black_forest_labs",
};

let configCache: ModelRouterConfig | undefined;

export function getBuddyModelRouterConfig(
  path = resolve(process.cwd(), "config", "buddy-model-router.json"),
) {
  configCache ??= JSON.parse(readFileSync(path, "utf8")) as ModelRouterConfig;
  return configCache;
}

function isConfigured(connector: ModelConnector, environment: NodeJS.ProcessEnv) {
  if (connector.availability === "always") return true;
  return connector.secret_references.some((reference) => Boolean(environment[reference]?.trim()));
}

export function resolveBuddyModelPlan(
  requestInput: z.input<typeof buddyModelRequestSchema>,
  environment: NodeJS.ProcessEnv = process.env,
) {
  const request = buddyModelRequestSchema.parse(requestInput);
  const config = getBuddyModelRouterConfig();
  const eligible = config.connectors.filter((connector) => connector.mode === request.modelMode);
  const requested = request.modelConnectorId
    ? config.connectors.find((connector) => connector.id === request.modelConnectorId)
    : undefined;

  if (request.modelConnectorId && !requested) {
    throw new Error(`Unknown model connector: ${request.modelConnectorId}`);
  }
  if (requested && requested.mode !== request.modelMode) {
    throw new Error(`${requested.label} is not available in ${request.modelMode} mode`);
  }

  const connector = requested
    || eligible.find((candidate) => isConfigured(candidate, environment))
    || eligible[0];
  if (!connector) throw new Error(`No ${request.modelMode} model route is configured`);

  const configured = isConfigured(connector, environment);
  const paidApprovalRequired = request.modelMode === "premium" && !request.approvePaidModelForThisRequest;
  const implementationReady = connector.implementation_status !== "contract_only";
  const status = request.modelMode === "free"
    ? configured && implementationReady ? "free_route_ready" : configured ? "adapter_implementation_required" : "configuration_required"
    : paidApprovalRequired
      ? "paid_approval_required"
      : configured && implementationReady
        ? "provider_adapter_ready"
        : configured
          ? "adapter_implementation_required"
          : "configuration_required";

  return {
    schema: "dreamco.buddy_model_plan.v1",
    mode: request.modelMode,
    connector: {
      id: connector.id,
      label: connector.label,
      protocol: connector.protocol,
      configured,
      implementationStatus: connector.implementation_status,
      taskTypes: connector.task_types,
    },
    selectedModelId: request.selectedModelId || "provider_default_for_task",
    status,
    paidUseApprovedForThisRequest:
      request.modelMode === "premium" && request.approvePaidModelForThisRequest,
    automaticPaidUpgrade: false,
    freeFallback: "buddy_native",
    providerCallExecuted: false,
    nextStep: status === "paid_approval_required"
      ? "Approve premium use for this one request or switch back to free."
      : status === "configuration_required"
        ? "Connect the selected provider with a backend secret reference."
        : status === "adapter_implementation_required"
          ? "The credential reference exists, but a governed execution adapter must pass sandbox tests before use."
        : request.modelMode === "premium"
          ? "The authenticated provider adapter may execute this approved request."
          : "Buddy Native will prepare the response locally without a provider charge.",
  } as const;
}

function normalized(value: string) {
  return value.toLowerCase().replace(/[^a-z0-9]/g, "");
}

function matchingTaskSignals(objective: string, requiredCapabilities: string[]) {
  const searchable = `${objective} ${requiredCapabilities.join(" ")}`.toLowerCase();
  const matches = TASK_SIGNALS.filter((signal) => signal.terms.some((term) => searchable.includes(term)));
  return matches.length ? matches : [{ id: "reasoning", terms: ["general task"] } as const];
}

function targetRoutingScore(
  target: (typeof MODEL_BENCHMARK_TARGETS)[number],
  request: BuddyModelSelectionRequest,
  taskSignals: ReturnType<typeof matchingTaskSignals>,
) {
  const searchable = [target.name, target.provider, target.category, target.bestFor, ...target.declaredCapabilities]
    .join(" ")
    .toLowerCase();
  const matchedSignals = taskSignals.filter((signal) => searchable.includes(signal.id));
  const matchedCapabilities = request.requiredCapabilities.filter((capability) => searchable.includes(capability.toLowerCase()));
  const isFree = target.tier === "free";
  const isPremium = target.tier === "paid" || target.tier === "freemium";
  const tierFit = request.preferredTier === "any"
    || (request.preferredTier === "free" && isFree)
    || (request.preferredTier === "premium" && isPremium);
  const localOrOwnerControlled = ["dreamco", "ollama"].includes(normalized(target.provider));
  const objectiveTerms = request.objective.toLowerCase().split(/\W+/).filter((term) => term.length >= 4);
  const objectiveMatches = new Set(objectiveTerms.filter((term) => searchable.includes(term))).size;
  const score = matchedSignals.length * 26
    + matchedCapabilities.length * 12
    + Math.min(10, objectiveMatches)
    + (tierFit ? 8 : -8)
    + (!target.discoveryTarget ? 4 : 0)
    + (isFree ? request.priorities.cost * 8 : -request.priorities.cost * 3)
    + (localOrOwnerControlled ? request.priorities.privacy * 10 : 0)
    + (localOrOwnerControlled ? request.priorities.latency * 3 : 0);
  const metadataCoverage = Math.min(1, 0.25
    + (matchedSignals.length ? 0.3 : 0)
    + (request.requiredCapabilities.length
      ? (matchedCapabilities.length / request.requiredCapabilities.length) * 0.3
      : 0.15)
    + (!target.discoveryTarget ? 0.15 : 0));

  return {
    target,
    score: Number(score.toFixed(3)),
    metadataCoverage: Number(metadataCoverage.toFixed(2)),
    matchedSignals: matchedSignals.map((signal) => signal.id),
    matchedCapabilities,
    tierFit,
    localOrOwnerControlled,
  };
}

export function selectBuddyModelsForTask(
  requestInput: z.input<typeof buddyModelSelectionRequestSchema>,
  environment: NodeJS.ProcessEnv = process.env,
) {
  const request = buddyModelSelectionRequestSchema.parse(requestInput);
  const config = getBuddyModelRouterConfig();
  const taskSignals = matchingTaskSignals(request.objective, request.requiredCapabilities);
  const scored = MODEL_BENCHMARK_TARGETS
    .filter((target) => request.allowDiscovery || !target.discoveryTarget)
    .map((target) => targetRoutingScore(target, request, taskSignals))
    .sort((left, right) => right.score - left.score || left.target.id - right.target.id);
  const providerDiverse = scored.filter((candidate, index, all) => (
    all.findIndex((item) => normalized(item.target.provider) === normalized(candidate.target.provider)) === index
  ));
  const ranked = providerDiverse.slice(0, request.maxCandidates).map((candidate, index) => {
    const connectorId = PROVIDER_CONNECTOR_IDS[normalized(candidate.target.provider)] || null;
    const connector = connectorId ? config.connectors.find((item) => item.id === connectorId) : undefined;
    const connectorConfigured = connector ? isConfigured(connector, environment) : false;
    const paidApprovalRequired = ["paid", "freemium"].includes(candidate.target.tier)
      && !request.approvePaidModelForThisRequest;
    const readiness = candidate.target.discoveryTarget
      ? "official_catalog_discovery_required"
      : paidApprovalRequired
        ? "paid_approval_required"
        : !connector
          ? "adapter_required"
          : !connectorConfigured
            ? "configuration_required"
            : connector.implementation_status === "contract_only"
              ? "adapter_required"
            : candidate.target.provider === "DreamCo"
              ? "local_route_ready"
              : "exact_model_verification_required";
    return {
      rank: index + 1,
      targetId: candidate.target.id,
      name: candidate.target.name,
      provider: candidate.target.provider,
      category: candidate.target.category,
      tier: candidate.target.tier,
      discoveryTarget: candidate.target.discoveryTarget,
      officialCatalog: candidate.target.officialCatalog,
      declaredTaskFit: candidate.target.bestFor,
      matchedTaskSignals: candidate.matchedSignals,
      matchedRequiredCapabilities: candidate.matchedCapabilities,
      routingFitScore: candidate.score,
      routingMetadataCoverage: candidate.metadataCoverage,
      routingMetadataCoverageMeaning: "Coverage of declared catalog metadata for this request; not a quality or benchmark score.",
      qualityEvidenceContribution: 0,
      connectorId,
      connectorConfigured,
      readiness,
    };
  });
  const first = ranked[0];
  const selectedStatus = first?.readiness || "no_catalog_candidate";

  return {
    schema: "dreamco.buddy_model_selection.v1",
    objective: request.objective,
    detectedTaskSignals: taskSignals.map((signal) => signal.id),
    requiredCapabilities: request.requiredCapabilities,
    preferredTier: request.preferredTier,
    priorities: request.priorities,
    candidateCount: ranked.length,
    candidates: ranked,
    selectedCandidateTargetId: first?.targetId || null,
    status: selectedStatus,
    paidUseApprovedForThisRequest: request.approvePaidModelForThisRequest,
    automaticPaidUpgrade: false,
    providerCallExecuted: false,
    permanentBestClaimed: false,
    freeFallback: {
      connectorId: "buddy_native",
      status: "free_route_ready",
      note: "Buddy Native can plan, route, and prepare sandbox work without a provider charge.",
    },
    nextStep: selectedStatus === "official_catalog_discovery_required"
      ? "Resolve the exact current model ID, version, access terms, and price from the official catalog, then benchmark it."
      : selectedStatus === "paid_approval_required"
        ? "Approve paid use for this request or keep the Buddy Native fallback."
        : selectedStatus === "configuration_required"
          ? "Connect the selected provider using a backend secret reference."
          : selectedStatus === "adapter_required"
            ? "Build and test a governed adapter before execution."
            : selectedStatus === "exact_model_verification_required"
              ? "Record the exact provider model ID and run signed benchmarks before production routing."
              : "The local route may prepare this task; no external model has been called.",
    truthContract: {
      rankingUsesDeclaredMetadataOnly: true,
      rankingIsLiveQualityEvidence: false,
      currentBestModelClaimed: false,
      liveBenchmarkRequiredBeforeProductionPromotion: true,
    },
  } as const;
}
