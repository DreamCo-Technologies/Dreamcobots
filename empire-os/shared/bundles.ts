// ---------------------------------------------------------------------------
// Marketplace bundles: subscription tiers, skill packs, industry verticals,
// and MOE (Model Orchestration Engine) routing rules
// ---------------------------------------------------------------------------

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
  price: string;
  description: string;
  agentCount: number;
  skills: string[];
}

export interface IndustryVertical {
  name: string;
  price: string;
  description: string;
  targetClients: string;
  providers: string[];
  features: string[];
}

export interface MoeRoutingRule {
  taskType: string;
  priority: string;
  costTier: "standard" | "premium";
  providers: string[];
  description?: string;
}

export const SUBSCRIPTION_TIERS: SubscriptionTier[] = [
  {
    name: "Starter",
    price: "$0",
    period: "month",
    features: [
      "3 AI bots included",
      "Guided automation only",
      "Basic analytics",
      "Community support",
    ],
    modelAccess: "GPT-4o mini",
    agentLimit: 3,
  },
  {
    name: "Pro",
    price: "$49",
    period: "month",
    features: [
      "15 AI bots included",
      "Semi-auto mode unlocked",
      "Deal calculator tools",
      "Priority support",
      "Revenue tracking",
    ],
    modelAccess: "GPT-4o + Claude 3 Haiku",
    agentLimit: 15,
  },
  {
    name: "Empire",
    price: "$199",
    period: "month",
    features: [
      "50 AI bots included",
      "Full autonomy mode",
      "Multi-division access",
      "Dedicated account manager",
      "Custom integrations",
      "White-label options",
    ],
    modelAccess: "GPT-4o + Claude 3.5 Sonnet + Gemini Pro",
    agentLimit: 50,
    highlight: true,
  },
  {
    name: "Elite",
    price: "$499",
    period: "month",
    features: [
      "Unlimited bots",
      "God-mode autonomy",
      "All divisions unlocked",
      "24/7 priority support",
      "Custom AI training",
      "SLA guarantees",
      "Advanced analytics",
    ],
    modelAccess: "All models including o1 + Claude Opus",
    agentLimit: -1,
  },
];

export const SKILL_PACKS: SkillPack[] = [
  {
    name: "Sales Automation Pack",
    price: "$29/mo",
    description: "End-to-end sales pipeline automation with lead scoring, outreach, and CRM sync.",
    agentCount: 5,
    skills: ["Lead generation", "Email outreach", "CRM sync", "Deal tracking", "Follow-up sequences"],
  },
  {
    name: "Real Estate Pack",
    price: "$39/mo",
    description: "Property sourcing, deal analysis, and offer automation for real estate investors.",
    agentCount: 4,
    skills: ["Property sourcing", "ARV calculation", "Offer generation", "Comps analysis"],
  },
  {
    name: "Social Media Pack",
    price: "$19/mo",
    description: "Automated content creation, scheduling, and engagement across all major platforms.",
    agentCount: 3,
    skills: ["Content creation", "Scheduling", "Engagement automation", "Analytics reporting"],
  },
  {
    name: "Finance & Accounting Pack",
    price: "$29/mo",
    description: "Automated bookkeeping, invoicing, and financial reporting for your empire.",
    agentCount: 4,
    skills: ["Bookkeeping", "Invoice generation", "Expense tracking", "P&L reporting"],
  },
  {
    name: "Car Flip Pack",
    price: "$24/mo",
    description: "Vehicle sourcing, valuation, and flip analysis for automotive entrepreneurs.",
    agentCount: 3,
    skills: ["Vehicle sourcing", "Price analysis", "Listing automation", "ROI tracking"],
  },
  {
    name: "E-Commerce Pack",
    price: "$34/mo",
    description: "Product sourcing, listing optimization, and order fulfillment automation.",
    agentCount: 5,
    skills: ["Product research", "Listing creation", "Price optimization", "Inventory management", "Order sync"],
  },
];

export const INDUSTRY_VERTICALS: IndustryVertical[] = [
  {
    name: "Real Estate",
    price: "$99/mo",
    description: "Complete real estate investment automation — from deal sourcing to closing.",
    targetClients: "Investors, wholesalers, flippers, agents",
    providers: ["Zillow", "ATTOM", "PropStream", "MLS APIs", "DealMachine"],
    features: [
      "Automated property sourcing",
      "ARV and deal analysis",
      "Offer letter generation",
      "CRM pipeline management",
      "Contractor bid tracking",
    ],
  },
  {
    name: "Automotive",
    price: "$79/mo",
    description: "End-to-end car flip and dealership automation.",
    targetClients: "Car flippers, dealers, auction buyers",
    providers: ["KBB", "Manheim", "CarGurus", "AutoTrader", "Carfax"],
    features: [
      "Vehicle sourcing automation",
      "Valuation and comp analysis",
      "Listing creation",
      "Flip ROI calculator",
      "Buyer outreach",
    ],
  },
  {
    name: "E-Commerce",
    price: "$89/mo",
    description: "Multi-channel e-commerce empire management and automation.",
    targetClients: "Amazon sellers, Shopify merchants, dropshippers",
    providers: ["Amazon SP-API", "Shopify", "eBay", "Walmart", "TikTok Shop"],
    features: [
      "Product research",
      "Listing optimization",
      "Price intelligence",
      "Inventory sync",
      "Returns management",
    ],
  },
  {
    name: "Digital Agency",
    price: "$129/mo",
    description: "Full-service digital agency automation for agencies and freelancers.",
    targetClients: "Agencies, consultants, freelancers",
    providers: ["HubSpot", "GoHighLevel", "Stripe", "Google Ads", "Meta Ads"],
    features: [
      "Client onboarding automation",
      "Proposal generation",
      "Campaign management",
      "Reporting dashboards",
      "Invoice & payment automation",
    ],
  },
];

export const MOE_ROUTING_RULES: MoeRoutingRule[] = [
  {
    taskType: "code-generation",
    priority: "high",
    costTier: "premium",
    providers: ["Claude 3.5 Sonnet", "GPT-4o", "Gemini 1.5 Pro"],
    description: "Complex code generation and debugging tasks",
  },
  {
    taskType: "content-writing",
    priority: "medium",
    costTier: "standard",
    providers: ["GPT-4o mini", "Claude 3 Haiku", "Llama 3.1 70B"],
    description: "Blog posts, social media content, and marketing copy",
  },
  {
    taskType: "data-analysis",
    priority: "high",
    costTier: "premium",
    providers: ["GPT-4o", "Claude 3.5 Sonnet", "Gemini 1.5 Pro"],
    description: "Data processing, analytics, and insights generation",
  },
  {
    taskType: "lead-scoring",
    priority: "medium",
    costTier: "standard",
    providers: ["GPT-4o mini", "Claude 3 Haiku"],
    description: "CRM lead qualification and scoring",
  },
  {
    taskType: "deal-analysis",
    priority: "high",
    costTier: "premium",
    providers: ["GPT-4o", "Claude 3.5 Sonnet"],
    description: "Real estate and automotive deal evaluation",
  },
  {
    taskType: "email-outreach",
    priority: "low",
    costTier: "standard",
    providers: ["GPT-4o mini", "Llama 3.1 8B"],
    description: "Personalized cold email and follow-up sequences",
  },
  {
    taskType: "image-generation",
    priority: "medium",
    costTier: "premium",
    providers: ["DALL-E 3", "Stable Diffusion XL", "Midjourney"],
    description: "Marketing visuals and product imagery",
  },
  {
    taskType: "sentiment-analysis",
    priority: "low",
    costTier: "standard",
    providers: ["GPT-4o mini", "Claude 3 Haiku", "Mistral 7B"],
    description: "Customer feedback and social listening",
  },
  {
    taskType: "voice-synthesis",
    priority: "medium",
    costTier: "premium",
    providers: ["ElevenLabs", "OpenAI TTS", "Deepgram"],
    description: "Automated voice messages and audio content",
  },
  {
    taskType: "web-scraping",
    priority: "low",
    costTier: "standard",
    providers: ["Firecrawl", "Apify", "BrightData"],
    description: "Competitive intelligence and data harvesting",
  },
  {
    taskType: "contract-review",
    priority: "high",
    costTier: "premium",
    providers: ["Claude 3.5 Sonnet", "GPT-4o"],
    description: "Legal document review and risk analysis",
  },
  {
    taskType: "financial-modeling",
    priority: "high",
    costTier: "premium",
    providers: ["GPT-4o", "Claude 3.5 Sonnet"],
    description: "Revenue forecasting and financial projections",
  },
];
