// ---------------------------------------------------------------------------
// API registry for tiers, autonomy limits, and division integrations
// ---------------------------------------------------------------------------

export type Tier = "free" | "pro" | "enterprise" | "elite";

export interface TierPricingInfo {
  name: string;
  monthlyPrice: number;
  yearlyPrice: number;
  description: string;
  features: string[];
}

export interface ApiCategory {
  name: string;
  apis: string[];
}

export interface DivisionApiRegistry {
  categories: ApiCategory[];
}

export const TIER_PRICING: Record<Tier, TierPricingInfo> = {
  free: {
    name: "Free",
    monthlyPrice: 0,
    yearlyPrice: 0,
    description: "Get started with AI-powered automation",
    features: [
      "Up to 3 bots",
      "Basic task automation",
      "Community support",
      "100 API calls/month",
    ],
  },
  pro: {
    name: "Pro",
    monthlyPrice: 49,
    yearlyPrice: 470,
    description: "Scale your automation with advanced AI",
    features: [
      "Up to 15 bots",
      "Advanced task orchestration",
      "Priority email support",
      "10,000 API calls/month",
      "Deal calculator tools",
      "Revenue analytics",
    ],
  },
  enterprise: {
    name: "Enterprise",
    monthlyPrice: 199,
    yearlyPrice: 1910,
    description: "Full autonomous empire management",
    features: [
      "Up to 50 bots",
      "Full autonomy mode",
      "Dedicated support",
      "100,000 API calls/month",
      "Multi-division access",
      "White-label options",
      "Custom integrations",
    ],
  },
  elite: {
    name: "Elite",
    monthlyPrice: 499,
    yearlyPrice: 4790,
    description: "Unlimited power for serious empire builders",
    features: [
      "Unlimited bots",
      "God-mode autonomy",
      "24/7 dedicated support",
      "Unlimited API calls",
      "All divisions unlocked",
      "Custom AI model training",
      "SLA guarantees",
      "Advanced analytics dashboard",
    ],
  },
};

export const TIER_AUTONOMY_LIMITS: Record<string, string[]> = {
  free: ["guided"],
  pro: ["guided", "semi-auto"],
  enterprise: ["guided", "semi-auto", "auto"],
  elite: ["guided", "semi-auto", "auto", "full-auto", "god-mode"],
};

export const DIVISION_API_REGISTRIES: Record<string, DivisionApiRegistry> = {
  "DreamSalesPro": {
    categories: [
      { name: "CRM", apis: ["HubSpot", "Salesforce", "Pipedrive", "Close", "Zoho CRM"] },
      { name: "Outreach", apis: ["Apollo", "Lemlist", "Outreach", "SalesLoft", "Instantly"] },
      { name: "Data", apis: ["ZoomInfo", "Clearbit", "Hunter.io", "Clay", "RocketReach"] },
      { name: "Calling", apis: ["Twilio", "Ringover", "Dialpad", "JustCall"] },
      { name: "Video", apis: ["Vidyard", "Loom", "Dubb"] },
    ],
  },
  "DreamRealEstate": {
    categories: [
      { name: "MLS", apis: ["RETS", "Spark API", "Bridge API", "ATTOM Data"] },
      { name: "Valuation", apis: ["Zillow AVM", "HouseCanary", "First American", "CoreLogic"] },
      { name: "Comps", apis: ["PropStream", "BatchLeads", "DealMachine"] },
      { name: "Financing", apis: ["LenderFuse", "Groundfloor", "Kiavi", "LendingHome"] },
    ],
  },
  "DreamMedia": {
    categories: [
      { name: "Social", apis: ["Instagram Graph", "TikTok Business", "YouTube Data", "Twitter/X"] },
      { name: "Content", apis: ["OpenAI", "Anthropic", "Stability AI", "ElevenLabs"] },
      { name: "Analytics", apis: ["Sprout Social", "Brand24", "Mention", "Brandwatch"] },
      { name: "Scheduling", apis: ["Later", "Buffer", "Hootsuite", "Publer"] },
    ],
  },
  "DreamAuto": {
    categories: [
      { name: "Listings", apis: ["AutoTrader", "Cars.com", "CarGurus", "Manheim"] },
      { name: "Valuation", apis: ["KBB", "Black Book", "J.D. Power", "NADA"] },
      { name: "History", apis: ["Carfax", "AutoCheck", "VINCheck"] },
      { name: "Finance", apis: ["RouteOne", "DealerSocket", "Dealertrack"] },
    ],
  },
  "DreamFinance": {
    categories: [
      { name: "Banking", apis: ["Plaid", "MX", "Finicity", "Yodlee"] },
      { name: "Payments", apis: ["Stripe", "PayPal", "Square", "Braintree"] },
      { name: "Crypto", apis: ["Coinbase", "Binance", "Kraken", "CoinGecko"] },
      { name: "Analytics", apis: ["QuickBooks", "Xero", "Bench", "Pilot"] },
    ],
  },
  "DreamLogistics": {
    categories: [
      { name: "Shipping", apis: ["FedEx", "UPS", "USPS", "DHL", "EasyPost"] },
      { name: "Inventory", apis: ["ShipBob", "Flexport", "FreightQuote"] },
      { name: "Tracking", apis: ["AfterShip", "17Track", "Narvar"] },
    ],
  },
};

export function getTotalApiCount(): number {
  return Object.values(DIVISION_API_REGISTRIES).reduce(
    (total, registry) =>
      total + registry.categories.reduce((s, c) => s + c.apis.length, 0),
    0
  );
}

export function getApiCountForDivision(division: string): number {
  const registry = DIVISION_API_REGISTRIES[division];
  if (!registry) return 0;
  return registry.categories.reduce((s, c) => s + c.apis.length, 0);
}
