export interface ApiIntegration {
  name: string;
  category: string;
  description: string;
  tier: "free" | "pro" | "enterprise" | "elite";
}

export interface DivisionApiRegistry {
  division: string;
  categories: { name: string; apis: ApiIntegration[] }[];
}

export const DREAMSALESPRO_APIS: DivisionApiRegistry = {
  division: "DreamSalesPro",
  categories: [
    {
      name: "CRM & Pipeline",
      apis: [
        { name: "HubSpot", category: "crm", description: "Full-suite CRM with marketing automation", tier: "pro" },
        { name: "Salesforce", category: "crm", description: "Enterprise CRM platform", tier: "enterprise" },
        { name: "Zoho CRM", category: "crm", description: "Multi-channel CRM suite", tier: "pro" },
        { name: "Pipedrive", category: "crm", description: "Sales-focused pipeline CRM", tier: "pro" },
        { name: "Freshsales", category: "crm", description: "AI-powered CRM for sales", tier: "pro" },
        { name: "Close.com", category: "crm", description: "Inside sales CRM", tier: "pro" },
        { name: "Copper CRM", category: "crm", description: "Google Workspace CRM", tier: "pro" },
        { name: "Monday CRM", category: "crm", description: "Work OS with CRM", tier: "pro" },
        { name: "Insightly", category: "crm", description: "CRM with project management", tier: "pro" },
        { name: "Keap", category: "crm", description: "Small business CRM & automation", tier: "pro" },
      ],
    },
    {
      name: "Lead Databases",
      apis: [
        { name: "Apollo.io", category: "leads", description: "B2B lead intelligence platform", tier: "pro" },
        { name: "Hunter.io", category: "leads", description: "Email finder & verification", tier: "pro" },
        { name: "Clearbit", category: "leads", description: "Business intelligence & enrichment", tier: "enterprise" },
        { name: "Snov.io", category: "leads", description: "Email outreach & lead gen", tier: "pro" },
        { name: "RocketReach", category: "leads", description: "Professional contact finder", tier: "pro" },
        { name: "ZoomInfo", category: "leads", description: "Enterprise B2B data platform", tier: "enterprise" },
        { name: "Lusha", category: "leads", description: "Contact & company data", tier: "pro" },
        { name: "UpLead", category: "leads", description: "B2B prospecting platform", tier: "pro" },
        { name: "LeadIQ", category: "leads", description: "Prospecting workflow tool", tier: "pro" },
        { name: "Crunchbase", category: "leads", description: "Company & funding data", tier: "enterprise" },
      ],
    },
    {
      name: "Email Automation",
      apis: [
        { name: "SendGrid", category: "email", description: "Transactional & marketing email", tier: "pro" },
        { name: "Mailgun", category: "email", description: "Email API for developers", tier: "pro" },
        { name: "Amazon SES", category: "email", description: "Cloud email service", tier: "pro" },
        { name: "Mailchimp", category: "email", description: "Marketing automation platform", tier: "pro" },
        { name: "ActiveCampaign", category: "email", description: "Email marketing & CRM", tier: "pro" },
        { name: "ConvertKit", category: "email", description: "Creator email marketing", tier: "pro" },
        { name: "Lemlist", category: "email", description: "Cold email outreach", tier: "pro" },
        { name: "Instantly", category: "email", description: "Cold email at scale", tier: "pro" },
        { name: "Reply.io", category: "email", description: "Sales engagement platform", tier: "pro" },
        { name: "Outreach.io", category: "email", description: "Enterprise sales engagement", tier: "enterprise" },
      ],
    },
    {
      name: "SMS & Calling",
      apis: [
        { name: "Twilio", category: "comms", description: "Cloud communications platform", tier: "pro" },
        { name: "Vonage", category: "comms", description: "Communications APIs", tier: "pro" },
        { name: "Plivo", category: "comms", description: "Voice & SMS APIs", tier: "pro" },
        { name: "Telnyx", category: "comms", description: "Voice, messaging & networking", tier: "pro" },
        { name: "RingCentral", category: "comms", description: "Business communications", tier: "enterprise" },
        { name: "Aircall", category: "comms", description: "Cloud phone system", tier: "pro" },
        { name: "Dialpad", category: "comms", description: "AI-powered communications", tier: "pro" },
        { name: "JustCall", category: "comms", description: "Cloud phone for sales", tier: "pro" },
        { name: "OpenPhone", category: "comms", description: "Business phone system", tier: "pro" },
        { name: "CallRail", category: "comms", description: "Call tracking & analytics", tier: "pro" },
      ],
    },
    {
      name: "Appointment Booking",
      apis: [
        { name: "Calendly", category: "booking", description: "Scheduling automation", tier: "pro" },
        { name: "SavvyCal", category: "booking", description: "Personalized scheduling", tier: "pro" },
        { name: "Acuity Scheduling", category: "booking", description: "Online appointment scheduling", tier: "pro" },
        { name: "HubSpot Meetings", category: "booking", description: "CRM-integrated scheduling", tier: "pro" },
        { name: "Microsoft Bookings", category: "booking", description: "Enterprise scheduling", tier: "enterprise" },
      ],
    },
    {
      name: "Payment & Billing",
      apis: [
        { name: "Stripe", category: "payments", description: "Payment processing platform", tier: "pro" },
        { name: "PayPal", category: "payments", description: "Global payment platform", tier: "pro" },
        { name: "Square", category: "payments", description: "Commerce & payment solutions", tier: "pro" },
        { name: "Chargebee", category: "payments", description: "Subscription billing", tier: "enterprise" },
        { name: "Paddle", category: "payments", description: "SaaS billing & payments", tier: "pro" },
      ],
    },
    {
      name: "AI & Intelligence",
      apis: [
        { name: "OpenAI", category: "ai", description: "GPT models & embeddings", tier: "pro" },
        { name: "Anthropic", category: "ai", description: "Claude AI models", tier: "pro" },
        { name: "Cohere", category: "ai", description: "NLP & text analysis", tier: "pro" },
        { name: "Deepgram", category: "ai", description: "Speech recognition API", tier: "pro" },
        { name: "AssemblyAI", category: "ai", description: "Audio intelligence API", tier: "pro" },
      ],
    },
    {
      name: "Data Enrichment",
      apis: [
        { name: "ZeroBounce", category: "validation", description: "Email validation & scoring", tier: "pro" },
        { name: "NeverBounce", category: "validation", description: "Email verification", tier: "pro" },
        { name: "FullContact", category: "validation", description: "Identity resolution", tier: "enterprise" },
        { name: "Clearout", category: "validation", description: "Email & phone validation", tier: "pro" },
        { name: "Experian", category: "validation", description: "Data quality & enrichment", tier: "enterprise" },
      ],
    },
    {
      name: "Automation Layers",
      apis: [
        { name: "Zapier", category: "automation", description: "Workflow automation", tier: "pro" },
        { name: "Make.com", category: "automation", description: "Visual automation builder", tier: "pro" },
        { name: "n8n", category: "automation", description: "Open-source automation", tier: "pro" },
        { name: "Pabbly", category: "automation", description: "Business automation suite", tier: "pro" },
        { name: "Workato", category: "automation", description: "Enterprise automation", tier: "enterprise" },
      ],
    },
    {
      name: "Social Outreach",
      apis: [
        { name: "LinkedIn Marketing", category: "social", description: "LinkedIn ads & content", tier: "pro" },
        { name: "Phantombuster", category: "social", description: "Growth hacking automation", tier: "pro" },
        { name: "Dripify", category: "social", description: "LinkedIn automation tool", tier: "pro" },
        { name: "Facebook Graph", category: "social", description: "Facebook & Instagram API", tier: "pro" },
        { name: "X (Twitter)", category: "social", description: "Social media API", tier: "pro" },
      ],
    },
    {
      name: "Analytics & Performance",
      apis: [
        { name: "Google Analytics", category: "analytics", description: "Web analytics platform", tier: "pro" },
        { name: "Mixpanel", category: "analytics", description: "Product analytics", tier: "pro" },
        { name: "Amplitude", category: "analytics", description: "Digital analytics platform", tier: "enterprise" },
        { name: "Segment", category: "analytics", description: "Customer data platform", tier: "enterprise" },
        { name: "Hotjar", category: "analytics", description: "Behavior analytics", tier: "pro" },
      ],
    },
    {
      name: "Customer Support",
      apis: [
        { name: "Intercom", category: "support", description: "Customer messaging platform", tier: "pro" },
        { name: "Zendesk", category: "support", description: "Customer service platform", tier: "enterprise" },
        { name: "Freshdesk", category: "support", description: "Help desk software", tier: "pro" },
        { name: "Drift", category: "support", description: "Conversational marketing", tier: "pro" },
        { name: "Crisp", category: "support", description: "Business messaging platform", tier: "pro" },
      ],
    },
  ],
};

export const DIVISION_API_REGISTRIES: Record<string, DivisionApiRegistry> = {
  DreamSalesPro: DREAMSALESPRO_APIS,
  DreamContent: {
    division: "DreamContent",
    categories: [
      {
        name: "Video & Media",
        apis: [
          { name: "YouTube Data", category: "video", description: "YouTube channel & video management", tier: "pro" },
          { name: "TikTok", category: "video", description: "Short-form video platform", tier: "pro" },
          { name: "Instagram Graph", category: "social", description: "Instagram content & analytics", tier: "pro" },
          { name: "Canva", category: "design", description: "Design & content creation", tier: "pro" },
          { name: "Adobe Creative Cloud", category: "design", description: "Professional creative tools", tier: "enterprise" },
        ],
      },
      {
        name: "Publishing & Monetization",
        apis: [
          { name: "WordPress", category: "cms", description: "Content management system", tier: "pro" },
          { name: "Medium", category: "publishing", description: "Online publishing platform", tier: "pro" },
          { name: "Substack", category: "newsletter", description: "Newsletter platform", tier: "pro" },
          { name: "Gumroad", category: "commerce", description: "Digital product sales", tier: "pro" },
          { name: "Patreon", category: "membership", description: "Creator membership platform", tier: "pro" },
        ],
      },
      {
        name: "Distribution & Analytics",
        apis: [
          { name: "Buffer", category: "scheduling", description: "Social media scheduling", tier: "pro" },
          { name: "Hootsuite", category: "management", description: "Social media management", tier: "pro" },
          { name: "Pinterest", category: "social", description: "Visual discovery platform", tier: "pro" },
          { name: "Unsplash", category: "media", description: "Stock photography", tier: "free" },
          { name: "Pexels", category: "media", description: "Free stock photos & videos", tier: "free" },
        ],
      },
      {
        name: "Education Platforms",
        apis: [
          { name: "Teachable", category: "education", description: "Online course platform", tier: "pro" },
          { name: "Kajabi", category: "education", description: "All-in-one creator platform", tier: "enterprise" },
          { name: "Thinkific", category: "education", description: "Course creation platform", tier: "pro" },
          { name: "Ko-fi", category: "tipping", description: "Creator support platform", tier: "free" },
          { name: "Shutterstock Contributor", category: "stock", description: "Stock media marketplace", tier: "pro" },
        ],
      },
    ],
  },
  DreamFinance: {
    division: "DreamFinance",
    categories: [
      {
        name: "Payment Processing",
        apis: [
          { name: "Stripe", category: "payments", description: "Payment infrastructure", tier: "pro" },
          { name: "PayPal", category: "payments", description: "Global payments", tier: "pro" },
          { name: "Square", category: "payments", description: "Commerce platform", tier: "pro" },
          { name: "Wise", category: "transfers", description: "International transfers", tier: "pro" },
          { name: "Payoneer", category: "payments", description: "Cross-border payments", tier: "pro" },
        ],
      },
      {
        name: "Accounting & Tax",
        apis: [
          { name: "QuickBooks", category: "accounting", description: "Business accounting software", tier: "pro" },
          { name: "Xero", category: "accounting", description: "Cloud accounting", tier: "pro" },
          { name: "FreshBooks", category: "invoicing", description: "Invoicing & accounting", tier: "pro" },
          { name: "TaxJar", category: "tax", description: "Sales tax automation", tier: "pro" },
          { name: "Avalara", category: "tax", description: "Tax compliance automation", tier: "enterprise" },
        ],
      },
      {
        name: "Banking & Data",
        apis: [
          { name: "Plaid", category: "banking", description: "Financial data connectivity", tier: "enterprise" },
          { name: "Mercury", category: "banking", description: "Startup banking", tier: "pro" },
          { name: "Brex", category: "banking", description: "Corporate card & finance", tier: "enterprise" },
          { name: "Ramp", category: "expenses", description: "Expense management", tier: "enterprise" },
          { name: "Gusto", category: "payroll", description: "Payroll & HR platform", tier: "pro" },
        ],
      },
      {
        name: "Trading & Crypto",
        apis: [
          { name: "Coinbase", category: "crypto", description: "Cryptocurrency exchange", tier: "pro" },
          { name: "Binance", category: "crypto", description: "Crypto trading platform", tier: "pro" },
          { name: "Kraken", category: "crypto", description: "Crypto exchange", tier: "pro" },
          { name: "Bill.com", category: "ap-ar", description: "Accounts payable/receivable", tier: "enterprise" },
          { name: "Wave", category: "accounting", description: "Free accounting software", tier: "free" },
        ],
      },
    ],
  },
  DreamRetail: {
    division: "DreamRetail",
    categories: [
      {
        name: "E-Commerce Platforms",
        apis: [
          { name: "Shopify", category: "ecommerce", description: "E-commerce platform", tier: "pro" },
          { name: "WooCommerce", category: "ecommerce", description: "WordPress e-commerce", tier: "pro" },
          { name: "BigCommerce", category: "ecommerce", description: "Enterprise e-commerce", tier: "enterprise" },
          { name: "Square Online", category: "ecommerce", description: "Online selling", tier: "pro" },
          { name: "TikTok Shop", category: "social-commerce", description: "Social commerce", tier: "pro" },
        ],
      },
      {
        name: "Marketplaces",
        apis: [
          { name: "Amazon Seller", category: "marketplace", description: "Amazon selling API", tier: "pro" },
          { name: "Etsy", category: "marketplace", description: "Handmade marketplace", tier: "pro" },
          { name: "eBay", category: "marketplace", description: "Online auction & sales", tier: "pro" },
          { name: "Walmart Marketplace", category: "marketplace", description: "Walmart selling", tier: "enterprise" },
          { name: "Facebook Commerce", category: "marketplace", description: "Facebook & Instagram shops", tier: "pro" },
        ],
      },
      {
        name: "Fulfillment & Logistics",
        apis: [
          { name: "ShipStation", category: "shipping", description: "Order fulfillment", tier: "pro" },
          { name: "Printful", category: "pod", description: "Print-on-demand fulfillment", tier: "pro" },
          { name: "Printify", category: "pod", description: "Print-on-demand platform", tier: "pro" },
          { name: "AfterShip", category: "tracking", description: "Shipment tracking", tier: "pro" },
          { name: "Stripe Connect", category: "marketplace-payments", description: "Marketplace payments", tier: "enterprise" },
        ],
      },
      {
        name: "Sourcing & Dropshipping",
        apis: [
          { name: "CJ Dropshipping", category: "dropshipping", description: "Dropshipping supplier", tier: "pro" },
          { name: "Spocket", category: "dropshipping", description: "US/EU dropshipping", tier: "pro" },
          { name: "Alibaba", category: "sourcing", description: "Global sourcing platform", tier: "pro" },
          { name: "AliExpress", category: "sourcing", description: "Consumer sourcing", tier: "pro" },
          { name: "Faire", category: "wholesale", description: "Wholesale marketplace", tier: "pro" },
        ],
      },
    ],
  },
  DreamAutomation: {
    division: "DreamAutomation",
    categories: [
      {
        name: "Workflow Automation",
        apis: [
          { name: "Zapier", category: "automation", description: "App integration automation", tier: "pro" },
          { name: "Make.com", category: "automation", description: "Visual automation builder", tier: "pro" },
          { name: "n8n", category: "automation", description: "Open-source workflow automation", tier: "pro" },
          { name: "Retool", category: "internal-tools", description: "Internal tool builder", tier: "enterprise" },
          { name: "Appsmith", category: "internal-tools", description: "Open-source app builder", tier: "pro" },
        ],
      },
      {
        name: "Communication",
        apis: [
          { name: "Slack", category: "messaging", description: "Team communication", tier: "pro" },
          { name: "Microsoft Teams", category: "messaging", description: "Enterprise collaboration", tier: "enterprise" },
          { name: "Twilio", category: "comms", description: "Cloud communications", tier: "pro" },
          { name: "SendGrid", category: "email", description: "Email delivery", tier: "pro" },
          { name: "Discord", category: "community", description: "Community platform", tier: "free" },
        ],
      },
      {
        name: "Productivity",
        apis: [
          { name: "Google Sheets", category: "data", description: "Spreadsheet automation", tier: "pro" },
          { name: "Airtable", category: "database", description: "Database & spreadsheet hybrid", tier: "pro" },
          { name: "Notion", category: "workspace", description: "All-in-one workspace", tier: "pro" },
          { name: "Trello", category: "projects", description: "Project management boards", tier: "pro" },
          { name: "Asana", category: "projects", description: "Work management platform", tier: "pro" },
        ],
      },
      {
        name: "Deployment & Hosting",
        apis: [
          { name: "Vercel", category: "hosting", description: "Frontend deployment", tier: "pro" },
          { name: "Firebase", category: "backend", description: "App development platform", tier: "pro" },
          { name: "Supabase", category: "backend", description: "Open-source Firebase alternative", tier: "pro" },
          { name: "Cloudinary", category: "media", description: "Media management & delivery", tier: "pro" },
          { name: "DocuSign", category: "documents", description: "Electronic signatures", tier: "enterprise" },
        ],
      },
    ],
  },
  DreamRealEstate: {
    division: "DreamRealEstate",
    categories: [
      {
        name: "Property Data",
        apis: [
          { name: "Zillow", category: "listings", description: "Property listings & valuations", tier: "pro" },
          { name: "Realtor.com", category: "listings", description: "Real estate listings", tier: "pro" },
          { name: "ATTOM Data", category: "data", description: "Property data solutions", tier: "enterprise" },
          { name: "CoreLogic", category: "analytics", description: "Property intelligence", tier: "enterprise" },
          { name: "Reonomy", category: "commercial", description: "Commercial property intelligence", tier: "enterprise" },
        ],
      },
      {
        name: "Management & Operations",
        apis: [
          { name: "AppFolio", category: "management", description: "Property management software", tier: "pro" },
          { name: "Buildium", category: "management", description: "Property management platform", tier: "pro" },
          { name: "Yardi", category: "management", description: "Real estate management", tier: "enterprise" },
          { name: "RentManager", category: "management", description: "Property management suite", tier: "pro" },
          { name: "CoStar", category: "commercial", description: "Commercial real estate data", tier: "elite" },
        ],
      },
    ],
  },
  DreamData: {
    division: "DreamData",
    categories: [
      {
        name: "Analytics & BI",
        apis: [
          { name: "Google Analytics", category: "web-analytics", description: "Web analytics", tier: "pro" },
          { name: "Mixpanel", category: "product-analytics", description: "Product analytics", tier: "pro" },
          { name: "Tableau", category: "bi", description: "Business intelligence", tier: "enterprise" },
          { name: "Looker", category: "bi", description: "Data exploration platform", tier: "enterprise" },
          { name: "Datadog", category: "monitoring", description: "Infrastructure monitoring", tier: "enterprise" },
        ],
      },
      {
        name: "Data Collection",
        apis: [
          { name: "Segment", category: "cdp", description: "Customer data platform", tier: "enterprise" },
          { name: "Algolia", category: "search", description: "Search & discovery", tier: "pro" },
          { name: "SimilarWeb", category: "intelligence", description: "Digital intelligence", tier: "enterprise" },
          { name: "SEMrush", category: "seo", description: "SEO & marketing tools", tier: "pro" },
          { name: "Ahrefs", category: "seo", description: "SEO toolset", tier: "pro" },
        ],
      },
    ],
  },
  DreamGlobal: {
    division: "DreamGlobal",
    categories: [
      {
        name: "International Operations",
        apis: [
          { name: "Wise", category: "transfers", description: "International money transfers", tier: "pro" },
          { name: "Payoneer", category: "payments", description: "Cross-border payments", tier: "pro" },
          { name: "DeepL", category: "translation", description: "AI translation service", tier: "pro" },
          { name: "Google Translate", category: "translation", description: "Translation API", tier: "pro" },
          { name: "Avalara", category: "tax", description: "Global tax compliance", tier: "enterprise" },
        ],
      },
    ],
  },
  DreamAIInfra: {
    division: "DreamAIInfra",
    categories: [
      {
        name: "AI Models & APIs",
        apis: [
          { name: "OpenAI", category: "llm", description: "GPT models & APIs", tier: "pro" },
          { name: "Anthropic", category: "llm", description: "Claude AI models", tier: "pro" },
          { name: "Google Vertex AI", category: "ml", description: "ML platform", tier: "enterprise" },
          { name: "Hugging Face", category: "models", description: "ML model hub", tier: "pro" },
          { name: "AWS SageMaker", category: "ml", description: "ML deployment platform", tier: "enterprise" },
        ],
      },
      {
        name: "Infrastructure",
        apis: [
          { name: "AWS", category: "cloud", description: "Cloud infrastructure", tier: "enterprise" },
          { name: "Google Cloud", category: "cloud", description: "Cloud platform", tier: "enterprise" },
          { name: "Azure", category: "cloud", description: "Microsoft cloud platform", tier: "enterprise" },
          { name: "Replicate", category: "inference", description: "ML model hosting", tier: "pro" },
          { name: "Modal", category: "compute", description: "Serverless GPU compute", tier: "pro" },
        ],
      },
    ],
  },
  DreamProServices: {
    division: "DreamProServices",
    categories: [
      {
        name: "Course & Content",
        apis: [
          { name: "Teachable", category: "education", description: "Online course platform", tier: "pro" },
          { name: "Kajabi", category: "education", description: "Creator business platform", tier: "enterprise" },
          { name: "Thinkific", category: "education", description: "Course creation", tier: "pro" },
          { name: "Gumroad", category: "digital-products", description: "Digital product sales", tier: "pro" },
          { name: "ClickFunnels", category: "funnels", description: "Sales funnel builder", tier: "pro" },
        ],
      },
      {
        name: "Legal & Documents",
        apis: [
          { name: "DocuSign", category: "esign", description: "Electronic signatures", tier: "enterprise" },
          { name: "PandaDoc", category: "documents", description: "Document automation", tier: "pro" },
          { name: "HelloSign", category: "esign", description: "E-signature solution", tier: "pro" },
          { name: "GoHighLevel", category: "agency", description: "Agency management platform", tier: "pro" },
          { name: "Kartra", category: "marketing", description: "All-in-one marketing", tier: "pro" },
        ],
      },
    ],
  },
  DreamTrade: {
    division: "DreamTrade",
    categories: [
      {
        name: "Trading Platforms",
        apis: [
          { name: "Alpaca", category: "trading", description: "Commission-free trading API", tier: "pro" },
          { name: "Interactive Brokers", category: "trading", description: "Professional trading", tier: "enterprise" },
          { name: "Coinbase Pro", category: "crypto", description: "Crypto trading", tier: "pro" },
          { name: "Binance", category: "crypto", description: "Crypto exchange", tier: "pro" },
          { name: "TradingView", category: "charting", description: "Trading charts & analysis", tier: "pro" },
        ],
      },
    ],
  },
  DreamFlow: {
    division: "DreamFlow",
    categories: [
      {
        name: "Automation & Data",
        apis: [
          { name: "Puppeteer", category: "scraping", description: "Browser automation", tier: "pro" },
          { name: "Playwright", category: "scraping", description: "Cross-browser automation", tier: "pro" },
          { name: "ScrapingBee", category: "scraping", description: "Web scraping API", tier: "pro" },
          { name: "Bright Data", category: "proxy", description: "Proxy & data collection", tier: "enterprise" },
          { name: "Oxylabs", category: "proxy", description: "Web scraping infrastructure", tier: "enterprise" },
        ],
      },
    ],
  },
  DreamMarket: {
    division: "DreamMarket",
    categories: [
      {
        name: "Marketplace & Affiliate",
        apis: [
          { name: "Amazon Seller", category: "marketplace", description: "Amazon selling", tier: "pro" },
          { name: "eBay", category: "marketplace", description: "Online marketplace", tier: "pro" },
          { name: "Shopify", category: "ecommerce", description: "E-commerce platform", tier: "pro" },
          { name: "Impact", category: "affiliate", description: "Partnership management", tier: "pro" },
          { name: "ShareASale", category: "affiliate", description: "Affiliate network", tier: "pro" },
        ],
      },
    ],
  },
  DreamEmpire: {
    division: "DreamEmpire",
    categories: [
      {
        name: "Enterprise Operations",
        apis: [
          { name: "Datadog", category: "monitoring", description: "Infrastructure monitoring", tier: "enterprise" },
          { name: "PagerDuty", category: "incidents", description: "Incident management", tier: "enterprise" },
          { name: "Jira", category: "projects", description: "Project tracking", tier: "enterprise" },
          { name: "Confluence", category: "docs", description: "Team documentation", tier: "enterprise" },
          { name: "Grafana", category: "dashboards", description: "Observability dashboards", tier: "pro" },
        ],
      },
    ],
  },
  CommandCore: {
    division: "CommandCore",
    categories: [
      {
        name: "System Operations",
        apis: [
          { name: "Prometheus", category: "monitoring", description: "Metrics & alerting", tier: "enterprise" },
          { name: "Sentry", category: "errors", description: "Error tracking", tier: "pro" },
          { name: "Datadog", category: "apm", description: "Application performance", tier: "enterprise" },
          { name: "New Relic", category: "observability", description: "Full-stack observability", tier: "enterprise" },
          { name: "Slack", category: "notifications", description: "Alert notifications", tier: "pro" },
        ],
      },
    ],
  },
  GameTitan: {
    division: "GameTitan",
    categories: [
      {
        name: "Gaming & Analytics",
        apis: [
          { name: "Steam Web", category: "gaming", description: "Steam platform API", tier: "pro" },
          { name: "Riot Games", category: "gaming", description: "League of Legends API", tier: "pro" },
          { name: "Twitch", category: "streaming", description: "Live streaming platform", tier: "pro" },
          { name: "Discord", category: "community", description: "Gaming community platform", tier: "free" },
          { name: "Unity Analytics", category: "game-dev", description: "Game analytics", tier: "pro" },
        ],
      },
    ],
  },
};

export function getApiCountForDivision(division: string): number {
  const reg = DIVISION_API_REGISTRIES[division];
  if (!reg) return 0;
  return reg.categories.reduce((sum, c) => sum + c.apis.length, 0);
}

export function getTotalApiCount(): number {
  return Object.values(DIVISION_API_REGISTRIES).reduce(
    (sum, reg) => sum + reg.categories.reduce((s, c) => s + c.apis.length, 0),
    0
  );
}

export const TIER_AUTONOMY_LIMITS: Record<string, string[]> = {
  free: ["guided"],
  pro: ["guided", "semi-autonomous"],
  enterprise: ["guided", "semi-autonomous", "full-autonomy"],
  elite: ["guided", "semi-autonomous", "full-autonomy"],
};

export const TIER_PRICING = {
  free: { price: 0, label: "Free", features: ["1 bot", "Guided mode only", "Community support", "Basic analytics", "Sandbox mode only"] },
  pro: { price: 29, label: "Pro", features: ["Up to 25 bots", "Semi-autonomous mode", "Email support", "Full analytics", "Sandbox + Live modes", "API integrations", "Priority queue"] },
  enterprise: { price: 499, label: "Enterprise", features: ["Up to 100 bots", "Full autonomy mode", "Dedicated support", "Custom analytics", "All operational modes", "Premium API integrations", "SLA guarantee", "White-label option", "Custom model fine-tuning"] },
  elite: { price: 2500, label: "Elite", features: ["Unlimited bots", "Full autonomy mode", "24/7 concierge support", "Custom dashboards", "All modes + priority", "All 200+ API integrations", "99.99% SLA", "White-label + reseller rights", "Custom AI model training", "Dedicated infrastructure", "Revenue share program"] },
};
