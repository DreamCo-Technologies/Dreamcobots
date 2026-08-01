import { readFileSync, writeFileSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

import { MODEL_BENCHMARK_TARGETS } from "../shared/model-benchmark-targets";

type BenchmarkConfig = {
  schema: string;
  catalog_reviewed_on: string;
  stale_after_days: number;
  target_count: number;
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
  if (normalized.includes("video") || normalized.includes("voice")) {
    return [...common, "vision_understanding", "audio_understanding"];
  }
  if (normalized.includes("translation") || normalized.includes("writing")) {
    return [...common, "multilingual", "long_context_retrieval"];
  }
  return [...common, "arithmetic_reasoning", "tool_selection"];
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
