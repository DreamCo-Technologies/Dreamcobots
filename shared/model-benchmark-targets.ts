import { AI_MODELS } from "./ai-models";

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

export const OFFICIAL_MODEL_DISCOVERY_SOURCES = [
  { provider: "OpenAI", catalog: "https://developers.openai.com/api/docs/models", region: "United States" },
  { provider: "Google", catalog: "https://ai.google.dev/gemini-api/docs/models", region: "United States" },
  { provider: "Anthropic", catalog: "https://platform.claude.com/docs/en/about-claude/models/overview", region: "United States" },
  { provider: "Microsoft", catalog: "https://learn.microsoft.com/en-us/azure/foundry/foundry-models/concepts/models-sold-directly-by-azure", region: "United States" },
  { provider: "Amazon", catalog: "https://docs.aws.amazon.com/bedrock/latest/userguide/models-supported.html", region: "United States" },
  { provider: "Hugging Face", catalog: "https://huggingface.co/models", region: "Global" },
  { provider: "Alibaba Cloud", catalog: "https://www.alibabacloud.com/help/en/model-studio/models", region: "China" },
  { provider: "Baidu", catalog: "https://cloud.baidu.com/doc/qianfan/index.html", region: "China" },
  { provider: "Mistral AI", catalog: "https://docs.mistral.ai/models/overview", region: "France" },
  { provider: "Ollama", catalog: "https://ollama.com/library", region: "Global" },
  { provider: "NVIDIA", catalog: "https://docs.nvidia.com/nim/", region: "United States" },
  { provider: "Cohere", catalog: "https://docs.cohere.com/v1/docs/models", region: "Canada" },
  { provider: "xAI", catalog: "https://docs.x.ai/developers/models", region: "United States" },
  { provider: "Groq", catalog: "https://console.groq.com/docs/models", region: "United States" },
  { provider: "Together AI", catalog: "https://docs.together.ai/docs/serverless/models", region: "United States" },
  { provider: "Fireworks AI", catalog: "https://docs.fireworks.ai/models/overview", region: "United States" },
  { provider: "Cerebras", catalog: "https://inference-docs.cerebras.ai/models/overview", region: "United States" },
  { provider: "Replicate", catalog: "https://replicate.com/docs/topics/models/official-models", region: "United States" },
  { provider: "Stability AI", catalog: "https://platform.stability.ai/docs/", region: "United Kingdom" },
  { provider: "Black Forest Labs", catalog: "https://docs.bfl.ai/release-notes", region: "Germany" },
] as const;

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

const curatedTargets: ModelBenchmarkTarget[] = AI_MODELS.map((model) => ({
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
  officialCatalog: null,
  developerRegion: model.country,
}));

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
