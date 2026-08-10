import { AI_MODELS } from "./ai-models";
import {
  getModelProviderSource,
  OFFICIAL_MODEL_DISCOVERY_SOURCES,
} from "./model-provider-sources";

export { OFFICIAL_MODEL_DISCOVERY_SOURCES } from "./model-provider-sources";

export type ModelBenchmarkTarget = {
  id: number;
  name: string;
  provider: string;
  category: string;
  tier: string;
  bestFor: string;
  declaredCapabilities: string[];
  accessNote: string;
  discoveryTarget: boolean;
  exactModelId: string | null;
  officialCatalog: string | null;
  developerRegion: string;
};

export const MODEL_BENCHMARK_TARGET_COUNT = 500;

export const MODEL_DISCOVERY_TASKS = [
  "Coding",
  "Reasoning",
  "Research",
  "Agents",
  "Vision",
  "Image Generation",
  "Image Editing",
  "Video",
  "Voice and Speech",
  "Music and Audio",
  "Multilingual and Translation",
  "Safety and Moderation",
  "OCR and Documents",
  "Search and Retrieval",
  "Data Analysis",
  "Embeddings",
  "Forecasting",
  "Simulation",
  "3D and Spatial",
  "Accessibility",
] as const;

const curatedTargets: ModelBenchmarkTarget[] = AI_MODELS.map((model) => {
  const source = getModelProviderSource(model.provider);
  if (!source) throw new Error(`Missing official source profile for curated provider: ${model.provider}`);
  return {
    id: model.id,
    name: model.name,
    provider: model.provider,
    category: model.category,
    tier: model.tier,
    bestFor: model.bestFor,
    declaredCapabilities: [...new Set([...model.freeFeatures, ...model.paidFeatures])],
    accessNote: model.paidPrice,
    discoveryTarget: false,
    exactModelId: null,
    officialCatalog: source.officialSource,
    developerRegion: model.country,
  };
});

const discoveryTargets: ModelBenchmarkTarget[] = OFFICIAL_MODEL_DISCOVERY_SOURCES.flatMap((source, sourceIndex) =>
  MODEL_DISCOVERY_TASKS.map((task, taskIndex) => ({
    id: 101 + sourceIndex * MODEL_DISCOVERY_TASKS.length + taskIndex,
    name: `${source.provider} ${task} discovery lane`,
    provider: source.provider,
    category: task,
    tier: "discovery",
    bestFor: `Discovering the current ${task.toLowerCase()} candidates from the provider's official catalog before a benchmark run.`,
    declaredCapabilities: [
      "Official-catalog model discovery",
      "Exact model ID and version capture",
      "Task-specific benchmark assignment",
      "Availability, terms, region, and cost evidence",
    ],
    accessNote: "Discovery only; access terms and prices must be refreshed from the official source.",
    discoveryTarget: true,
    exactModelId: null,
    officialCatalog: source.catalog,
    developerRegion: source.region,
  })),
);

export const MODEL_BENCHMARK_TARGETS = [...curatedTargets, ...discoveryTargets];

if (MODEL_BENCHMARK_TARGETS.length !== MODEL_BENCHMARK_TARGET_COUNT) {
  throw new Error(`Expected ${MODEL_BENCHMARK_TARGET_COUNT} model benchmark targets, found ${MODEL_BENCHMARK_TARGETS.length}`);
}
