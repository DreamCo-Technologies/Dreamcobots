import { readFileSync, writeFileSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

import { MODEL_BENCHMARK_TARGETS } from "../shared/model-benchmark-targets";

type BenchmarkConfig = {
  schema: string;
  catalog_reviewed_on: string;
  stale_after_days: number;
  target_count: number;
  issue_refs: number[];
  policy: Record<string, boolean>;
  suites: Array<{
    id: string;
    label: string;
    modality: string;
    grader: string;
    prompt_fixture: string;
    expected: string;
  }>;
};

const evidenceDimensions = {
  reasoning: ["reason", "math", "analysis"],
  coding: ["cod", "developer", "software"],
  vision: ["vision", "image understanding", "visual"],
  imageGeneration: ["image generation", "text-to-image"],
  imageEditing: ["image editing", "inpainting", "photo"],
  video: ["video"],
  audio: ["audio", "music"],
  speech: ["speech", "voice", "transcription"],
  translation: ["translation", "multilingual", "language"],
  research: ["research", "citation", "search"],
  ocrAndDocuments: ["ocr", "document"],
  agentsAndTools: ["agent", "tool", "workflow"],
  retrieval: ["retrieval", "embedding", "search"],
} as const;

const root = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const sourcePath = resolve(root, "config", "buddy-model-benchmarks.json");
const generatedPath = resolve(root, "config", "generated", "buddy_model_benchmarks.json");
const publicScriptPath = resolve(root, "website", "data", "buddy-model-benchmarks.js");

const config = JSON.parse(readFileSync(sourcePath, "utf8")) as BenchmarkConfig;

function suiteIdsFor(category: string) {
  const common = ["instruction_following", "structured_output", "safety_boundary"];
  const normalized = category.toLowerCase();
  if (normalized.includes("coding") || normalized.includes("agent")) {
    return [...common, "arithmetic_reasoning", "code_generation", "code_repair", "tool_selection"];
  }
  if (normalized.includes("research") || normalized.includes("legal") || normalized.includes("health")) {
    return [...common, "long_context_retrieval", "grounded_research"];
  }
  if (normalized.includes("image")) return [...common, "vision_understanding"];
  if (normalized.includes("video") || normalized.includes("voice") || normalized.includes("audio") || normalized.includes("music")) {
    return [...common, "vision_understanding", "audio_understanding"];
  }
  if (normalized.includes("translation") || normalized.includes("multilingual") || normalized.includes("writing")) {
    return [...common, "multilingual", "long_context_retrieval"];
  }
  if (normalized.includes("document") || normalized.includes("retrieval") || normalized.includes("embedding")) {
    return [...common, "long_context_retrieval", "grounded_research"];
  }
  return [...common, "arithmetic_reasoning", "tool_selection"];
}

function buildEvidenceProfile(model: (typeof MODEL_BENCHMARK_TARGETS)[number]) {
  const searchable = [model.category, model.bestFor, ...model.declaredCapabilities].join(" ").toLowerCase();
  const declaredDimensions = Object.entries(evidenceDimensions)
    .filter(([, keywords]) => keywords.some((keyword) => searchable.includes(keyword)))
    .map(([dimension]) => dimension);
  const verificationRequiredDimensions = Object.keys(evidenceDimensions)
    .filter((dimension) => !declaredDimensions.includes(dimension));
  return {
    declaredDimensions,
    verificationRequiredDimensions,
    contextWindowTokens: null,
    measuredSpeed: null,
    normalizedPriceUsd: null,
    license: null,
    declaredAccessNote: model.accessNote,
    metadataStatus: model.discoveryTarget ? "verification_required" : "refresh_required",
  };
}

function buildCatalog() {
  if (MODEL_BENCHMARK_TARGETS.length !== config.target_count) {
    throw new Error(`Expected ${config.target_count} benchmark targets, found ${MODEL_BENCHMARK_TARGETS.length}`);
  }
  const suites = new Set(config.suites.map((suite) => suite.id));
  const targets = MODEL_BENCHMARK_TARGETS.map((model) => {
    const benchmarkSuites = [...new Set(suiteIdsFor(model.category))];
    const unknownSuite = benchmarkSuites.find((suite) => !suites.has(suite));
    if (unknownSuite) throw new Error(`Unknown suite ${unknownSuite} for ${model.name}`);
    const checks = {
      identity: Boolean(model.name.trim() && model.provider.trim()),
      taskFit: Boolean(model.bestFor.trim() && model.category.trim()),
      accessMetadata: Boolean(model.tier && model.accessNote.trim()),
      capabilities: model.declaredCapabilities.length > 0,
      discoveryTruth: !model.discoveryTarget || Boolean(model.officialCatalog),
      suitesAssigned: benchmarkSuites.length >= 4,
    };
    return {
      id: model.id,
      name: model.name,
      provider: model.provider,
      category: model.category,
      tier: model.tier,
      bestFor: model.bestFor,
      declaredCapabilities: model.declaredCapabilities,
      accessNote: model.accessNote,
      discoveryTarget: model.discoveryTarget,
      exactModelId: model.exactModelId,
      officialCatalog: model.officialCatalog,
      developerRegion: model.developerRegion,
      benchmarkSuites,
      promptLibrary: benchmarkSuites,
      evidenceProfile: buildEvidenceProfile(model),
      catalogChecks: checks,
      catalogReady: Object.values(checks).every(Boolean),
      liveEvidenceStatus: model.discoveryTarget ? "discovery_required" : "not_run",
      liveScore: null,
      lastLiveBenchmarkAt: null,
    };
  });
  return {
    schema: config.schema,
    catalogReviewedOn: config.catalog_reviewed_on,
    staleAfterDays: config.stale_after_days,
    policy: config.policy,
    issueRefs: config.issue_refs,
    truthContract: {
      catalogTargetMeansLiveProviderConnection: false,
      declaredCapabilityMeansBenchmarkPassed: false,
      routingRankMeansPermanentBest: false,
      promptLibraryExecutesFromStaticSite: false,
      liveScoresRequireExactModelVersionAndAdapterEvidence: true,
    },
    evidenceSchema: {
      capabilityDimensions: Object.keys(evidenceDimensions),
      declaredDimensionsAreLiveScores: false,
      unknownNumericValue: null,
      fieldsRequiringExactVersionEvidence: ["contextWindowTokens", "measuredSpeed", "normalizedPriceUsd", "license", "liveScore"],
    },
    promptLibrarySchema: {
      targetValuesReferenceSuiteIds: true,
      fixturesStoredIn: "suites",
      executionFromStaticSite: false,
    },
    summary: {
      targets: targets.length,
      providers: new Set(targets.map((target) => target.provider)).size,
      categories: new Set(targets.map((target) => target.category)).size,
      suites: config.suites.length,
      catalogReady: targets.filter((target) => target.catalogReady).length,
      liveBenchmarked: 0,
    },
    suites: config.suites,
    targets,
  };
}

function serialized(value: unknown) {
  return `${JSON.stringify(value, null, 2)}\n`;
}

const catalog = buildCatalog();
const json = serialized(catalog);
const script = `window.BUDDY_MODEL_BENCHMARKS = ${JSON.stringify(catalog)};\n`;
const checkOnly = process.argv.includes("--check");

if (checkOnly) {
  for (const [path, expected] of [[generatedPath, json], [publicScriptPath, script]] as const) {
    if (readFileSync(path, "utf8") !== expected) throw new Error(`Generated file is stale: ${path}`);
  }
  console.log(JSON.stringify(catalog.summary));
} else {
  writeFileSync(generatedPath, json);
  writeFileSync(publicScriptPath, script);
  console.log(JSON.stringify(catalog.summary));
}
