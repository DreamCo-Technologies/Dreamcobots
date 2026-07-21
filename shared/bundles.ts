export interface SubscriptionTier {
  name: string;
  price: string;
  period: string;
  features: string[];
  modelAccess: string;
  agentLimit: number;
  highlight?: boolean;
}

export interface SkillPack {
  name: string;
  description: string;
  price: string;
  providers: string[];
  agentCount: number;
  features: string[];
}

export interface IndustryVertical {
  name: string;
  description: string;
  price: string;
  targetClients: string;
  providers: string[];
  features: string[];
}

export const SUBSCRIPTION_TIERS: SubscriptionTier[] = [
  {
    name: "Free",
    price: "$0",
    period: "forever",
    features: [
      "Limited requests (50/day)",
      "2-3 open-source models",
      "Basic routing",
      "Community support",
      "Single agent access",
    ],
    modelAccess: "Mistral, Llama, Stability AI",
    agentLimit: 1,
  },
  {
    name: "Pro",
    price: "$49",
    period: "month",
    features: [
      "Unlimited requests",
      "Multi-model access (15+ models)",
      "Advanced routing & blending",
      "File uploads & processing",
      "Agent memory & context",
      "Analytics dashboard",
      "Priority support",
      "API access (10K calls/mo)",
    ],
    modelAccess: "GPT-4, Claude, Gemini, Mistral + open models",
    agentLimit: 10,
    highlight: true,
  },
  {
    name: "Elite",
    price: "$199",
    period: "month",
    features: [
      "Everything in Pro",
      "All major LLM access (50+ models)",
      "Industry-specific agents",
      "Custom workflows & automations",
      "Advanced analytics & reporting",
      "Unlimited API access",
      "Dedicated support",
      "White-label options",
    ],
    modelAccess: "All 200+ provider models",
    agentLimit: 50,
  },
  {
    name: "Enterprise",
    price: "Custom",
    period: "annual",
    features: [
      "Everything in Elite",
      "Custom fine-tuned models",
      "Private infrastructure deployment",
      "On-prem deployment options",
      "Dedicated compute resources",
      "SLA guarantees (99.99%)",
      "Custom integrations",
      "Dedicated account manager",
      "Security & compliance certifications",
    ],
    modelAccess: "Custom model training + all providers",
    agentLimit: -1,
  },
];

export const SKILL_PACKS: SkillPack[] = [
  {
    name: "Sales Agent Pack",
    description: "AI-powered sales intelligence, outreach automation, and revenue optimization",
    price: "$99/mo",
    providers: ["Gong.io", "Clay AI", "Jasper AI", "Apollo.io AI", "Drift AI", "Lavender AI"],
    agentCount: 15,
    features: ["Lead scoring & enrichment", "Automated outreach sequences", "Call analysis & coaching", "Pipeline velocity tracking", "Revenue forecasting"],
  },
  {
    name: "Coding Agent Pack",
    description: "Full-stack development assistance with AI pair programming and DevOps",
    price: "$79/mo",
    providers: ["OpenAI", "Codeium", "Tabnine", "GitHub Copilot", "DreamCo AI", "Vercel AI"],
    agentCount: 12,
    features: ["AI pair programming", "Code review & optimization", "Auto-debugging", "CI/CD automation", "Security scanning"],
  },
  {
    name: "Healthcare AI Pack",
    description: "Medical intelligence, clinical analytics, and drug discovery tools",
    price: "$299/mo",
    providers: ["Tempus", "PathAI", "Aidoc", "Abridge AI", "Insilico Medicine", "Viz.ai"],
    agentCount: 10,
    features: ["Clinical summarization", "Diagnostic imaging AI", "Drug discovery modeling", "Patient risk scoring", "Regulatory compliance"],
  },
  {
    name: "Legal AI Pack",
    description: "Contract analysis, compliance automation, and litigation intelligence",
    price: "$199/mo",
    providers: ["Harvey", "Luminance", "Ironclad", "Evisort", "Relativity AI", "DocuSign AI"],
    agentCount: 12,
    features: ["Contract review & analysis", "Compliance monitoring", "E-discovery automation", "Legal document generation", "Case analytics"],
  },
  {
    name: "Creative Pack",
    description: "AI-powered content creation across image, video, audio, and design",
    price: "$69/mo",
    providers: ["Midjourney", "Runway", "ElevenLabs", "Suno", "Canva AI", "Descript"],
    agentCount: 15,
    features: ["Image generation", "Video editing & creation", "Voice synthesis", "Music composition", "Graphic design automation"],
  },
  {
    name: "Cybersecurity Pack",
    description: "Threat detection, vulnerability scanning, and incident response",
    price: "$249/mo",
    providers: ["Darktrace", "CrowdStrike AI", "SentinelOne", "Snyk AI", "Vectra AI", "Arctic Wolf"],
    agentCount: 10,
    features: ["Real-time threat detection", "Vulnerability scanning", "Endpoint protection", "Network defense", "Incident response automation"],
  },
  {
    name: "Data & Analytics Pack",
    description: "Enterprise data intelligence, ML pipelines, and business analytics",
    price: "$149/mo",
    providers: ["Databricks", "Snowflake AI", "Pinecone", "DataRobot", "ThoughtSpot", "Alteryx AI"],
    agentCount: 15,
    features: ["Automated ML pipelines", "Vector search & RAG", "Business intelligence", "Data labeling & prep", "Predictive analytics"],
  },
  {
    name: "Automation Pack",
    description: "Robotic process automation, workflow optimization, and IT automation",
    price: "$129/mo",
    providers: ["UiPath", "Automation Anywhere", "Adept AI", "ServiceNow AI", "Samsara AI"],
    agentCount: 12,
    features: ["Business workflow automation", "IT service automation", "IoT monitoring", "Process optimization", "Smart task routing"],
  },
  {
    name: "Finance AI Pack",
    description: "Financial analytics, risk modeling, trading intelligence, and fraud detection",
    price: "$199/mo",
    providers: ["Stripe AI", "Plaid AI", "Bloomberg AI", "Kasisto", "Zest AI", "Upstart"],
    agentCount: 12,
    features: ["Fraud detection", "Credit risk modeling", "Market intelligence", "Payment optimization", "Financial forecasting"],
  },
  {
    name: "Education Pack",
    description: "Personalized learning, tutoring AI, and career development tools",
    price: "$39/mo",
    providers: ["Coursera AI", "Duolingo AI", "Khan Academy AI", "Udacity AI", "Speak AI"],
    agentCount: 8,
    features: ["Adaptive learning paths", "Language tutoring", "Career skill training", "Student analytics", "Content personalization"],
  },
];

export const INDUSTRY_VERTICALS: IndustryVertical[] = [
  {
    name: "Healthcare System",
    description: "End-to-end healthcare AI for hospitals, clinics, and pharma companies",
    price: "$25K-$500K/year",
    targetClients: "Hospitals, Pharma, Healthcare Providers",
    providers: ["Tempus", "PathAI", "Aidoc", "Abridge AI", "Insilico Medicine", "BenevolentAI", "Olive AI", "Owkin", "Viz.ai"],
    features: ["Clinical decision support", "Drug discovery pipelines", "Medical imaging analysis", "Patient flow optimization", "Regulatory compliance automation", "Clinical trial matching"],
  },
  {
    name: "Finance System",
    description: "Comprehensive AI for banking, insurance, trading, and risk management",
    price: "$50K-$500K/year",
    targetClients: "Banks, Insurance, Hedge Funds, FinTech",
    providers: ["Bloomberg AI", "Two Sigma AI", "Kasisto", "Zest AI", "Upstart", "Stripe AI", "Plaid AI", "Tractable AI", "Lemonade AI", "Kensho"],
    features: ["Algorithmic trading", "Credit scoring AI", "Fraud detection", "Insurance claims automation", "Market intelligence", "Regulatory reporting"],
  },
  {
    name: "Retail System",
    description: "AI-powered retail optimization from inventory to checkout-free stores",
    price: "$25K-$250K/year",
    targetClients: "Retail Chains, E-commerce, CPG Brands",
    providers: ["Alibaba DAMO Academy", "Trigo", "Standard AI", "Afresh", "Clay AI", "Jasper AI"],
    features: ["Demand forecasting", "Checkout-free technology", "Personalized marketing", "Supply chain optimization", "Price optimization", "Customer analytics"],
  },
  {
    name: "Manufacturing System",
    description: "Industrial AI for predictive maintenance, quality control, and supply chain",
    price: "$50K-$500K/year",
    targetClients: "Manufacturers, Automotive, Aerospace",
    providers: ["C3 AI", "SAP AI", "Samsara AI", "Covariant", "NVIDIA", "Databricks"],
    features: ["Predictive maintenance", "Quality inspection AI", "Supply chain optimization", "Digital twin simulation", "Energy optimization", "Production planning"],
  },
  {
    name: "Government System",
    description: "Secure AI for defense, intelligence, and public sector operations",
    price: "$100K-$5M/year",
    targetClients: "Federal Agencies, Defense, Intelligence",
    providers: ["Palantir", "Anduril", "Shield AI", "Vannevar Labs", "Scale AI"],
    features: ["Intelligence analytics", "Autonomous systems", "Secure data processing", "Threat assessment", "Mission planning", "Compliance frameworks"],
  },
  {
    name: "Real Estate System",
    description: "Property intelligence, deal analysis, and portfolio management AI",
    price: "$10K-$100K/year",
    targetClients: "Investors, Property Managers, Brokerages",
    providers: ["Databricks", "Snowflake AI", "SAP AI", "OpenAI"],
    features: ["Property valuation AI", "Deal scoring & analysis", "Portfolio optimization", "Market trend prediction", "Tenant screening", "Maintenance prediction"],
  },
  {
    name: "Automotive System",
    description: "Autonomous driving, fleet management, and automotive AI solutions",
    price: "$50K-$1M/year",
    targetClients: "Auto Manufacturers, Fleet Operators, Mobility Companies",
    providers: ["Wayve", "Cruise", "Aurora Innovation", "Nuro", "Samsara AI", "NVIDIA"],
    features: ["Autonomous driving AI", "Fleet optimization", "Vehicle diagnostics", "Predictive maintenance", "Route optimization", "Safety systems"],
  },
  {
    name: "Energy System",
    description: "AI for energy optimization, grid management, and sustainability",
    price: "$25K-$500K/year",
    targetClients: "Utilities, Oil & Gas, Renewable Energy",
    providers: ["C3 AI", "ClimateAI", "Tomorrow.io", "Databricks", "NVIDIA"],
    features: ["Grid optimization", "Demand forecasting", "Renewable integration", "Carbon tracking", "Predictive maintenance", "Energy trading AI"],
  },
  {
    name: "Defense System",
    description: "Military-grade AI for autonomous platforms, cybersecurity, and intelligence",
    price: "$500K-$10M/year",
    targetClients: "Military, Intelligence Agencies, Defense Contractors",
    providers: ["Anduril", "Shield AI", "Skydio", "Palantir", "Vannevar Labs", "Scale AI"],
    features: ["Autonomous drones & aircraft", "Threat detection", "Intelligence fusion", "Mission planning AI", "Cyber warfare defense", "Logistics optimization"],
  },
];

export const MOE_ROUTING_RULES = [
  { taskType: "Legal Contract Review", providers: ["Harvey", "OpenAI", "Anthropic"], priority: "accuracy", costTier: "premium" },
  { taskType: "Image Generation", providers: ["Stability AI", "Midjourney", "Runway"], priority: "quality", costTier: "standard" },
  { taskType: "Enterprise Analytics", providers: ["Databricks", "Snowflake AI", "Palantir"], priority: "scale", costTier: "premium" },
  { taskType: "Cyber Threat Detection", providers: ["Darktrace", "SentinelOne", "CrowdStrike AI"], priority: "speed", costTier: "premium" },
  { taskType: "Code Generation", providers: ["OpenAI", "Codeium", "Tabnine"], priority: "speed", costTier: "standard" },
  { taskType: "Voice Synthesis", providers: ["ElevenLabs", "Resemble AI", "Speechmatics"], priority: "quality", costTier: "standard" },
  { taskType: "Medical Diagnosis", providers: ["Tempus", "PathAI", "Aidoc"], priority: "accuracy", costTier: "premium" },
  { taskType: "Financial Analysis", providers: ["Bloomberg AI", "Kensho", "Two Sigma AI"], priority: "accuracy", costTier: "premium" },
  { taskType: "Content Marketing", providers: ["Jasper AI", "Copy.ai", "Grammarly"], priority: "speed", costTier: "standard" },
  { taskType: "Customer Support", providers: ["Intercom AI", "Zendesk AI", "Forethought AI"], priority: "speed", costTier: "standard" },
  { taskType: "Drug Discovery", providers: ["Insilico Medicine", "Atomwise", "BenevolentAI"], priority: "accuracy", costTier: "premium" },
  { taskType: "Autonomous Navigation", providers: ["Wayve", "Cruise", "Aurora Innovation"], priority: "safety", costTier: "premium" },
  { taskType: "Data Labeling", providers: ["Scale AI", "Snorkel AI", "Labelbox"], priority: "scale", costTier: "standard" },
  { taskType: "Translation", providers: ["DeepL", "Google AI", "OpenAI"], priority: "accuracy", costTier: "standard" },
  { taskType: "Video Creation", providers: ["Runway", "Pika Labs", "Synthesia"], priority: "quality", costTier: "standard" },
  { taskType: "Sales Outreach", providers: ["Apollo.io AI", "Clay AI", "Lavender AI"], priority: "speed", costTier: "standard" },
  { taskType: "Contract Analysis", providers: ["Ironclad", "Evisort", "Luminance"], priority: "accuracy", costTier: "premium" },
  { taskType: "HR Automation", providers: ["Deel AI", "Rippling AI", "Gusto AI"], priority: "compliance", costTier: "standard" },
  { taskType: "3D Modeling", providers: ["Luma AI", "Unity AI", "Epic Games AI"], priority: "quality", costTier: "premium" },
  { taskType: "Blockchain Analytics", providers: ["Chainalysis", "Fireblocks AI", "OpenSea AI"], priority: "accuracy", costTier: "premium" },
];
