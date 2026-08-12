export type ModelSourceKind =
  | "model_catalog"
  | "api_documentation"
  | "product_documentation"
  | "official_product"
  | "official_repository"
  | "local_system";

export type ModelConnectionKind =
  | "api_adapter"
  | "account_handoff"
  | "local_runtime"
  | "open_source_sandbox";

export type ModelProviderSourceProfile = {
  provider: string;
  officialSource: string;
  sourceKind: ModelSourceKind;
  connectionKind: ModelConnectionKind;
  connectorId: string | null;
  reviewedOn: string;
};

const REVIEWED_ON = "2026-08-10";

export const OFFICIAL_MODEL_DISCOVERY_SOURCES = [
  { provider: "OpenAI", catalog: "https://developers.openai.com/api/docs/models", region: "United States", connectorId: "openai" },
  { provider: "Google", catalog: "https://ai.google.dev/gemini-api/docs/models", region: "United States", connectorId: "google_gemini" },
  { provider: "Anthropic", catalog: "https://platform.claude.com/docs/en/about-claude/models/overview", region: "United States", connectorId: "anthropic" },
  { provider: "Microsoft", catalog: "https://learn.microsoft.com/en-us/azure/foundry/foundry-models/concepts/models-sold-directly-by-azure", region: "United States", connectorId: "azure_foundry" },
  { provider: "Amazon", catalog: "https://docs.aws.amazon.com/bedrock/latest/userguide/models-supported.html", region: "United States", connectorId: "amazon_bedrock" },
  { provider: "Hugging Face", catalog: "https://huggingface.co/models", region: "Global", connectorId: "huggingface" },
  { provider: "Alibaba Cloud", catalog: "https://www.alibabacloud.com/help/en/model-studio/models", region: "China", connectorId: "alibaba_model_studio" },
  { provider: "Baidu", catalog: "https://cloud.baidu.com/doc/qianfan/index.html", region: "China", connectorId: "baidu_qianfan" },
  { provider: "Mistral AI", catalog: "https://docs.mistral.ai/models/overview", region: "France", connectorId: "mistral" },
  { provider: "Ollama", catalog: "https://ollama.com/library", region: "Global", connectorId: "local_open_model" },
  { provider: "NVIDIA", catalog: "https://docs.nvidia.com/nim/", region: "United States", connectorId: "nvidia_nim" },
  { provider: "Cohere", catalog: "https://docs.cohere.com/v1/docs/models", region: "Canada", connectorId: "cohere" },
  { provider: "xAI", catalog: "https://docs.x.ai/developers/models", region: "United States", connectorId: "xai" },
  { provider: "Groq", catalog: "https://console.groq.com/docs/models", region: "United States", connectorId: "groq" },
  { provider: "Together AI", catalog: "https://docs.together.ai/docs/serverless/models", region: "United States", connectorId: "together_ai" },
  { provider: "Fireworks AI", catalog: "https://docs.fireworks.ai/models/overview", region: "United States", connectorId: "fireworks_ai" },
  { provider: "Cerebras", catalog: "https://inference-docs.cerebras.ai/models/overview", region: "United States", connectorId: "cerebras" },
  { provider: "Replicate", catalog: "https://replicate.com/docs/topics/models/official-models", region: "United States", connectorId: "replicate" },
  { provider: "Stability AI", catalog: "https://platform.stability.ai/docs/", region: "United Kingdom", connectorId: "stability_ai" },
  { provider: "Black Forest Labs", catalog: "https://docs.bfl.ai/release-notes", region: "Germany", connectorId: "black_forest_labs" },
] as const;

const curatedProviderSources: ModelProviderSourceProfile[] = [
  { provider: "DeepSeek", officialSource: "https://api-docs.deepseek.com/", sourceKind: "api_documentation", connectionKind: "api_adapter", connectorId: "deepseek", reviewedOn: REVIEWED_ON },
  { provider: "Meta", officialSource: "https://www.llama.com/", sourceKind: "model_catalog", connectionKind: "local_runtime", connectorId: "local_open_model", reviewedOn: REVIEWED_ON },
  { provider: "Perplexity AI", officialSource: "https://docs.perplexity.ai/", sourceKind: "api_documentation", connectionKind: "api_adapter", connectorId: null, reviewedOn: REVIEWED_ON },
  { provider: "Microsoft/GitHub", officialSource: "https://docs.github.com/en/copilot", sourceKind: "product_documentation", connectionKind: "account_handoff", connectorId: null, reviewedOn: REVIEWED_ON },
  { provider: "Anysphere", officialSource: "https://docs.cursor.com/", sourceKind: "product_documentation", connectionKind: "account_handoff", connectorId: null, reviewedOn: REVIEWED_ON },
  { provider: "DreamCo", officialSource: "buddy.html", sourceKind: "local_system", connectionKind: "local_runtime", connectorId: "buddy_native", reviewedOn: REVIEWED_ON },
  { provider: "Cognition", officialSource: "https://docs.devin.ai/", sourceKind: "product_documentation", connectionKind: "account_handoff", connectorId: null, reviewedOn: REVIEWED_ON },
  { provider: "Significant Gravitas", officialSource: "https://github.com/Significant-Gravitas/AutoGPT", sourceKind: "official_repository", connectionKind: "open_source_sandbox", connectorId: null, reviewedOn: REVIEWED_ON },
  { provider: "Yohei Nakajima", officialSource: "https://github.com/yoheinakajima/babyagi", sourceKind: "official_repository", connectionKind: "open_source_sandbox", connectorId: null, reviewedOn: REVIEWED_ON },
  { provider: "Reworkd", officialSource: "https://github.com/reworkd/AgentGPT", sourceKind: "official_repository", connectionKind: "open_source_sandbox", connectorId: null, reviewedOn: REVIEWED_ON },
  { provider: "DeepWisdom", officialSource: "https://github.com/FoundationAgents/MetaGPT", sourceKind: "official_repository", connectionKind: "open_source_sandbox", connectorId: null, reviewedOn: REVIEWED_ON },
  { provider: "CrewAI Inc.", officialSource: "https://docs.crewai.com/", sourceKind: "product_documentation", connectionKind: "api_adapter", connectorId: null, reviewedOn: REVIEWED_ON },
  { provider: "SuperAGI", officialSource: "https://github.com/TransformerOptimus/SuperAGI", sourceKind: "official_repository", connectionKind: "open_source_sandbox", connectorId: null, reviewedOn: REVIEWED_ON },
  { provider: "GPT-Engineer", officialSource: "https://github.com/AntonOsika/gpt-engineer", sourceKind: "official_repository", connectionKind: "open_source_sandbox", connectorId: null, reviewedOn: REVIEWED_ON },
  { provider: "Monica", officialSource: "https://monica.im/", sourceKind: "official_product", connectionKind: "account_handoff", connectorId: null, reviewedOn: REVIEWED_ON },
  { provider: "Midjourney", officialSource: "https://docs.midjourney.com/", sourceKind: "product_documentation", connectionKind: "account_handoff", connectorId: null, reviewedOn: REVIEWED_ON },
  { provider: "DreamCo/Open Source", officialSource: "open-model-lab.html", sourceKind: "local_system", connectionKind: "local_runtime", connectorId: "local_open_model", reviewedOn: REVIEWED_ON },
  { provider: "Runway", officialSource: "https://docs.dev.runwayml.com/", sourceKind: "api_documentation", connectionKind: "api_adapter", connectorId: null, reviewedOn: REVIEWED_ON },
  { provider: "Jasper", officialSource: "https://developers.jasper.ai/", sourceKind: "api_documentation", connectionKind: "api_adapter", connectorId: null, reviewedOn: REVIEWED_ON },
  { provider: "Copy.ai", officialSource: "https://www.copy.ai/", sourceKind: "official_product", connectionKind: "account_handoff", connectorId: null, reviewedOn: REVIEWED_ON },
  { provider: "Notion", officialSource: "https://developers.notion.com/", sourceKind: "api_documentation", connectionKind: "api_adapter", connectorId: null, reviewedOn: REVIEWED_ON },
  { provider: "Salesforce", officialSource: "https://developer.salesforce.com/docs/platform/einstein-genai/overview", sourceKind: "api_documentation", connectionKind: "api_adapter", connectorId: null, reviewedOn: REVIEWED_ON },
  { provider: "HubSpot", officialSource: "https://developers.hubspot.com/", sourceKind: "api_documentation", connectionKind: "api_adapter", connectorId: null, reviewedOn: REVIEWED_ON },
  { provider: "Zapier", officialSource: "https://docs.zapier.com/platform/home", sourceKind: "api_documentation", connectionKind: "api_adapter", connectorId: null, reviewedOn: REVIEWED_ON },
  { provider: "Make", officialSource: "https://developers.make.com/", sourceKind: "api_documentation", connectionKind: "api_adapter", connectorId: null, reviewedOn: REVIEWED_ON },
  { provider: "Tidio", officialSource: "https://developers.tidio.com/", sourceKind: "api_documentation", connectionKind: "api_adapter", connectorId: null, reviewedOn: REVIEWED_ON },
  { provider: "Intercom", officialSource: "https://developers.intercom.com/", sourceKind: "api_documentation", connectionKind: "api_adapter", connectorId: null, reviewedOn: REVIEWED_ON },
  { provider: "Grammarly", officialSource: "https://developer.grammarly.com/", sourceKind: "api_documentation", connectionKind: "api_adapter", connectorId: null, reviewedOn: REVIEWED_ON },
  { provider: "Synthesia", officialSource: "https://docs.synthesia.io/", sourceKind: "api_documentation", connectionKind: "api_adapter", connectorId: null, reviewedOn: REVIEWED_ON },
  { provider: "Descript", officialSource: "https://www.descript.com/", sourceKind: "official_product", connectionKind: "account_handoff", connectorId: null, reviewedOn: REVIEWED_ON },
  { provider: "Canva", officialSource: "https://www.canva.dev/docs/", sourceKind: "api_documentation", connectionKind: "api_adapter", connectorId: null, reviewedOn: REVIEWED_ON },
  { provider: "Kuaishou", officialSource: "https://klingai.com/", sourceKind: "official_product", connectionKind: "account_handoff", connectorId: null, reviewedOn: REVIEWED_ON },
  { provider: "LangChain Inc.", officialSource: "https://docs.langchain.com/", sourceKind: "product_documentation", connectionKind: "open_source_sandbox", connectorId: null, reviewedOn: REVIEWED_ON },
  { provider: "Alibaba", officialSource: "https://qwenlm.github.io/", sourceKind: "model_catalog", connectionKind: "local_runtime", connectorId: "local_open_model", reviewedOn: REVIEWED_ON },
  { provider: "01.AI", officialSource: "https://www.lingyiwanwu.com/en", sourceKind: "official_product", connectionKind: "local_runtime", connectorId: "local_open_model", reviewedOn: REVIEWED_ON },
  { provider: "Suno", officialSource: "https://suno.com/", sourceKind: "official_product", connectionKind: "account_handoff", connectorId: null, reviewedOn: REVIEWED_ON },
  { provider: "Udio", officialSource: "https://www.udio.com/", sourceKind: "official_product", connectionKind: "account_handoff", connectorId: null, reviewedOn: REVIEWED_ON },
  { provider: "Tavily", officialSource: "https://docs.tavily.com/", sourceKind: "api_documentation", connectionKind: "api_adapter", connectorId: null, reviewedOn: REVIEWED_ON },
  { provider: "Mendable", officialSource: "https://docs.mendable.ai/", sourceKind: "api_documentation", connectionKind: "api_adapter", connectorId: null, reviewedOn: REVIEWED_ON },
  { provider: "Pinecone", officialSource: "https://docs.pinecone.io/", sourceKind: "api_documentation", connectionKind: "api_adapter", connectorId: null, reviewedOn: REVIEWED_ON },
  { provider: "Weaviate", officialSource: "https://docs.weaviate.io/", sourceKind: "api_documentation", connectionKind: "api_adapter", connectorId: null, reviewedOn: REVIEWED_ON },
  { provider: "Stripe", officialSource: "https://docs.stripe.com/", sourceKind: "api_documentation", connectionKind: "api_adapter", connectorId: null, reviewedOn: REVIEWED_ON },
  { provider: "Plaid", officialSource: "https://plaid.com/docs/", sourceKind: "api_documentation", connectionKind: "api_adapter", connectorId: null, reviewedOn: REVIEWED_ON },
  { provider: "Google DeepMind", officialSource: "https://deepmind.google/models/", sourceKind: "model_catalog", connectionKind: "account_handoff", connectorId: null, reviewedOn: REVIEWED_ON },
  { provider: "Harvey", officialSource: "https://www.harvey.ai/", sourceKind: "official_product", connectionKind: "account_handoff", connectorId: null, reviewedOn: REVIEWED_ON },
  { provider: "Thomson Reuters", officialSource: "https://developerportal.thomsonreuters.com/", sourceKind: "api_documentation", connectionKind: "api_adapter", connectorId: null, reviewedOn: REVIEWED_ON },
  { provider: "Khan Academy", officialSource: "https://www.khanacademy.org/khan-labs", sourceKind: "official_product", connectionKind: "account_handoff", connectorId: null, reviewedOn: REVIEWED_ON },
  { provider: "Duolingo", officialSource: "https://www.duolingo.com/", sourceKind: "official_product", connectionKind: "account_handoff", connectorId: null, reviewedOn: REVIEWED_ON },
  { provider: "Tome", officialSource: "https://tome.app/", sourceKind: "official_product", connectionKind: "account_handoff", connectorId: null, reviewedOn: REVIEWED_ON },
  { provider: "Beautiful.ai", officialSource: "https://www.beautiful.ai/", sourceKind: "official_product", connectionKind: "account_handoff", connectorId: null, reviewedOn: REVIEWED_ON },
  { provider: "Semrush", officialSource: "https://developer.semrush.com/api/", sourceKind: "api_documentation", connectionKind: "api_adapter", connectorId: null, reviewedOn: REVIEWED_ON },
  { provider: "Surfer", officialSource: "https://docs.surferseo.com/", sourceKind: "api_documentation", connectionKind: "api_adapter", connectorId: null, reviewedOn: REVIEWED_ON },
  { provider: "Ahrefs", officialSource: "https://docs.ahrefs.com/docs/api/reference/introduction", sourceKind: "api_documentation", connectionKind: "api_adapter", connectorId: null, reviewedOn: REVIEWED_ON },
  { provider: "Scale AI", officialSource: "https://scale.com/docs", sourceKind: "api_documentation", connectionKind: "api_adapter", connectorId: null, reviewedOn: REVIEWED_ON },
  { provider: "W&B", officialSource: "https://docs.wandb.ai/", sourceKind: "product_documentation", connectionKind: "api_adapter", connectorId: null, reviewedOn: REVIEWED_ON },
  { provider: "Undetectable AI", officialSource: "https://undetectable.ai/", sourceKind: "official_product", connectionKind: "account_handoff", connectorId: null, reviewedOn: REVIEWED_ON },
  { provider: "Pictory", officialSource: "https://pictory.ai/", sourceKind: "official_product", connectionKind: "account_handoff", connectorId: null, reviewedOn: REVIEWED_ON },
  { provider: "Luma Labs", officialSource: "https://docs.lumalabs.ai/docs/api", sourceKind: "api_documentation", connectionKind: "api_adapter", connectorId: null, reviewedOn: REVIEWED_ON },
  { provider: "HeyGen", officialSource: "https://docs.heygen.com/", sourceKind: "api_documentation", connectionKind: "api_adapter", connectorId: null, reviewedOn: REVIEWED_ON },
  { provider: "Relevance AI", officialSource: "https://relevanceai.com/docs", sourceKind: "product_documentation", connectionKind: "api_adapter", connectorId: null, reviewedOn: REVIEWED_ON },
  { provider: "Beam AI", officialSource: "https://beam.ai/", sourceKind: "official_product", connectionKind: "account_handoff", connectorId: null, reviewedOn: REVIEWED_ON },
  { provider: "Rasa", officialSource: "https://rasa.com/docs/", sourceKind: "product_documentation", connectionKind: "open_source_sandbox", connectorId: null, reviewedOn: REVIEWED_ON },
  { provider: "Botpress", officialSource: "https://botpress.com/docs", sourceKind: "product_documentation", connectionKind: "api_adapter", connectorId: null, reviewedOn: REVIEWED_ON },
  { provider: "Typeform", officialSource: "https://www.typeform.com/developers/", sourceKind: "api_documentation", connectionKind: "api_adapter", connectorId: null, reviewedOn: REVIEWED_ON },
  { provider: "Gamma", officialSource: "https://developers.gamma.app/", sourceKind: "api_documentation", connectionKind: "api_adapter", connectorId: null, reviewedOn: REVIEWED_ON },
  { provider: "ByteDance", officialSource: "https://seed.bytedance.com/en/", sourceKind: "model_catalog", connectionKind: "account_handoff", connectorId: null, reviewedOn: REVIEWED_ON },
  { provider: "Wordware", officialSource: "https://docs.wordware.ai/", sourceKind: "product_documentation", connectionKind: "api_adapter", connectorId: null, reviewedOn: REVIEWED_ON },
  { provider: "Phind", officialSource: "https://www.phind.com/", sourceKind: "official_product", connectionKind: "account_handoff", connectorId: null, reviewedOn: REVIEWED_ON },
  { provider: "Tabnine", officialSource: "https://docs.tabnine.com/", sourceKind: "product_documentation", connectionKind: "account_handoff", connectorId: null, reviewedOn: REVIEWED_ON },
  { provider: "Codeium", officialSource: "https://docs.windsurf.com/", sourceKind: "product_documentation", connectionKind: "account_handoff", connectorId: null, reviewedOn: REVIEWED_ON },
  { provider: "Legalese Decoder", officialSource: "https://legalesedecoder.com/", sourceKind: "official_product", connectionKind: "account_handoff", connectorId: null, reviewedOn: REVIEWED_ON },
  { provider: "DataRobot", officialSource: "https://docs.datarobot.com/", sourceKind: "product_documentation", connectionKind: "api_adapter", connectorId: null, reviewedOn: REVIEWED_ON },
  { provider: "Obviously AI", officialSource: "https://docs.obviously.ai/", sourceKind: "product_documentation", connectionKind: "account_handoff", connectorId: null, reviewedOn: REVIEWED_ON },
  { provider: "Consensus", officialSource: "https://consensus.app/", sourceKind: "official_product", connectionKind: "account_handoff", connectorId: null, reviewedOn: REVIEWED_ON },
  { provider: "Elicit", officialSource: "https://elicit.com/", sourceKind: "official_product", connectionKind: "account_handoff", connectorId: null, reviewedOn: REVIEWED_ON },
  { provider: "Pika Labs", officialSource: "https://pika.art/", sourceKind: "official_product", connectionKind: "account_handoff", connectorId: null, reviewedOn: REVIEWED_ON },
  { provider: "Lovable", officialSource: "https://docs.lovable.dev/", sourceKind: "product_documentation", connectionKind: "account_handoff", connectorId: null, reviewedOn: REVIEWED_ON },
  { provider: "Vercel", officialSource: "https://vercel.com/docs/ai", sourceKind: "product_documentation", connectionKind: "api_adapter", connectorId: null, reviewedOn: REVIEWED_ON },
  { provider: "StackBlitz", officialSource: "https://developer.stackblitz.com/", sourceKind: "product_documentation", connectionKind: "api_adapter", connectorId: null, reviewedOn: REVIEWED_ON },
  { provider: "OpenAgents", officialSource: "https://github.com/xlang-ai/OpenAgents", sourceKind: "official_repository", connectionKind: "open_source_sandbox", connectorId: null, reviewedOn: REVIEWED_ON },
];

const discoveryProfiles: ModelProviderSourceProfile[] = OFFICIAL_MODEL_DISCOVERY_SOURCES.map((source) => ({
  provider: source.provider,
  officialSource: source.catalog,
  sourceKind: "model_catalog",
  connectionKind: source.provider === "Ollama" ? "local_runtime" : "api_adapter",
  connectorId: source.connectorId,
  reviewedOn: REVIEWED_ON,
}));

export const MODEL_PROVIDER_SOURCE_PROFILES = [...discoveryProfiles, ...curatedProviderSources];

const sourceByProvider = new Map(MODEL_PROVIDER_SOURCE_PROFILES.map((profile) => [profile.provider, profile]));

if (sourceByProvider.size !== MODEL_PROVIDER_SOURCE_PROFILES.length) {
  throw new Error("Model provider source profiles must use unique provider names");
}

export function getModelProviderSource(provider: string) {
  return sourceByProvider.get(provider) || null;
}

export function buildModelConnectionSetupPath(profile: ModelProviderSourceProfile) {
  if (profile.connectorId === "buddy_native") return "buddy.html";
  if (profile.connectionKind === "local_runtime" || profile.connectionKind === "open_source_sandbox") {
    return `open-model-lab.html?source=${encodeURIComponent(profile.officialSource)}&provider=${encodeURIComponent(profile.provider)}`;
  }
  const method = profile.connectionKind === "account_handoff" ? "browser_session_handoff" : "custom_rest";
  return `connections.html?app=${encodeURIComponent(profile.provider)}&url=${encodeURIComponent(profile.officialSource)}&method=${method}`;
}
