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
      name: "CRM & Sales",
      apis: [
        { name: "HubSpot CRM", category: "crm", description: "Full-suite CRM with marketing automation", tier: "pro" },
        { name: "Salesforce", category: "crm", description: "Enterprise CRM REST API", tier: "enterprise" },
        { name: "Pipedrive", category: "crm", description: "Sales-focused pipeline CRM", tier: "pro" },
        { name: "Zoho CRM", category: "crm", description: "Multi-channel CRM suite", tier: "pro" },
        { name: "Close", category: "crm", description: "Inside sales CRM for startups & SMBs", tier: "pro" },
        { name: "Freshworks CRM", category: "crm", description: "AI-powered sales & marketing CRM", tier: "pro" },
        { name: "Monday.com", category: "crm", description: "Work OS with CRM & project management", tier: "pro" },
        { name: "Asana", category: "crm", description: "Work management & project tracking", tier: "pro" },
        { name: "Trello", category: "crm", description: "Kanban-style project management boards", tier: "pro" },
        { name: "ClickUp", category: "crm", description: "All-in-one project & task management", tier: "pro" },
        { name: "Notion", category: "crm", description: "All-in-one workspace & knowledge base", tier: "pro" },
        { name: "Airtable", category: "crm", description: "Spreadsheet-database hybrid platform", tier: "pro" },
        { name: "Calendly", category: "crm", description: "Scheduling automation for meetings", tier: "pro" },
        { name: "Zoom", category: "crm", description: "Video conferencing & webinars API", tier: "pro" },
        { name: "Twilio", category: "crm", description: "Cloud communications (SMS, voice, video)", tier: "pro" },
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
      name: "Email & Outreach",
      apis: [
        { name: "SendGrid", category: "email", description: "Transactional & marketing email delivery", tier: "pro" },
        { name: "Mailgun", category: "email", description: "Email API for developers", tier: "pro" },
        { name: "Amazon SES", category: "email", description: "AWS cloud email service at scale", tier: "pro" },
        { name: "Postmark", category: "email", description: "Transactional email with best deliverability", tier: "pro" },
        { name: "Brevo", category: "email", description: "All-in-one marketing platform (ex-Sendinblue)", tier: "pro" },
        { name: "HubSpot Email", category: "email", description: "CRM-integrated email marketing", tier: "pro" },
        { name: "ActiveCampaign", category: "email", description: "Email marketing & CRM automation", tier: "pro" },
        { name: "Mailchimp", category: "email", description: "Marketing automation platform", tier: "pro" },
        { name: "Klaviyo", category: "email", description: "E-commerce email & SMS marketing", tier: "pro" },
        { name: "Lemlist", category: "email", description: "Personalized cold email outreach", tier: "pro" },
        { name: "Reply.io", category: "email", description: "Multichannel sales engagement", tier: "pro" },
        { name: "GMass", category: "email", description: "Gmail-based mass email & mail merge", tier: "pro" },
        { name: "Apollo.io", category: "email", description: "B2B lead intelligence & outreach", tier: "pro" },
        { name: "Hunter.io", category: "email", description: "Email finder & domain search", tier: "pro" },
        { name: "Clearbit", category: "email", description: "Business intelligence & lead enrichment", tier: "enterprise" },
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
        { name: "Adyen", category: "payments", description: "Global payments technology platform", tier: "enterprise" },
        { name: "Braintree", category: "payments", description: "Full-stack payment platform by PayPal", tier: "pro" },
        { name: "Authorize.net", category: "payments", description: "Payment gateway for online transactions", tier: "pro" },
        { name: "Plaid", category: "payments", description: "Financial data connectivity & verification", tier: "enterprise" },
        { name: "Wise", category: "payments", description: "International money transfers API", tier: "pro" },
        { name: "Checkout.com", category: "payments", description: "Enterprise payment processing", tier: "enterprise" },
        { name: "Dwolla", category: "payments", description: "ACH payment platform & bank transfers", tier: "enterprise" },
        { name: "Chargebee", category: "payments", description: "Subscription billing & revenue ops", tier: "enterprise" },
        { name: "Recurly", category: "payments", description: "Subscription management platform", tier: "enterprise" },
        { name: "Paddle", category: "payments", description: "SaaS billing, tax & payments", tier: "pro" },
        { name: "FastSpring", category: "payments", description: "Global digital commerce platform", tier: "enterprise" },
        { name: "Coinbase Commerce", category: "payments", description: "Cryptocurrency payment processing", tier: "pro" },
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
        name: "Payments & Billing",
        apis: [
          { name: "Stripe", category: "payments", description: "Payment processing & billing infrastructure", tier: "pro" },
          { name: "PayPal REST", category: "payments", description: "Global payment platform REST API", tier: "pro" },
          { name: "Square Payments", category: "payments", description: "Commerce & payment solutions", tier: "pro" },
          { name: "Adyen", category: "payments", description: "Global payments technology platform", tier: "enterprise" },
          { name: "Braintree", category: "payments", description: "Full-stack payment platform by PayPal", tier: "pro" },
          { name: "Authorize.net", category: "payments", description: "Payment gateway for online transactions", tier: "pro" },
          { name: "Plaid", category: "payments", description: "Financial data connectivity & bank verification", tier: "enterprise" },
          { name: "Wise", category: "payments", description: "International money transfers API", tier: "pro" },
          { name: "Checkout.com", category: "payments", description: "Enterprise-grade payment processing", tier: "enterprise" },
          { name: "Dwolla", category: "payments", description: "ACH payment platform & bank transfers", tier: "enterprise" },
          { name: "Chargebee", category: "payments", description: "Subscription billing & revenue operations", tier: "enterprise" },
          { name: "Recurly", category: "payments", description: "Subscription management & recurring billing", tier: "enterprise" },
          { name: "Paddle", category: "payments", description: "SaaS billing, tax & payments", tier: "pro" },
          { name: "FastSpring", category: "payments", description: "Global digital commerce platform", tier: "enterprise" },
          { name: "Coinbase Commerce", category: "payments", description: "Cryptocurrency payment processing", tier: "pro" },
        ],
      },
      {
        name: "Accounting & Tax",
        apis: [
          { name: "QuickBooks", category: "accounting", description: "Business accounting software", tier: "pro" },
          { name: "Xero", category: "accounting", description: "Cloud accounting platform", tier: "pro" },
          { name: "FreshBooks", category: "invoicing", description: "Invoicing & accounting", tier: "pro" },
          { name: "TaxJar", category: "tax", description: "Sales tax automation", tier: "pro" },
          { name: "Avalara", category: "tax", description: "Tax compliance automation", tier: "enterprise" },
        ],
      },
      {
        name: "Banking & Data",
        apis: [
          { name: "Mercury", category: "banking", description: "Startup banking API", tier: "pro" },
          { name: "Brex", category: "banking", description: "Corporate card & finance", tier: "enterprise" },
          { name: "Ramp", category: "expenses", description: "Expense management platform", tier: "enterprise" },
          { name: "Gusto", category: "payroll", description: "Payroll & HR platform", tier: "pro" },
          { name: "Bill.com", category: "ap-ar", description: "Accounts payable/receivable", tier: "enterprise" },
        ],
      },
      {
        name: "Trading & Crypto",
        apis: [
          { name: "Coinbase", category: "crypto", description: "Cryptocurrency exchange", tier: "pro" },
          { name: "Binance", category: "crypto", description: "Crypto trading platform", tier: "pro" },
          { name: "Kraken", category: "crypto", description: "Crypto exchange platform", tier: "pro" },
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
          { name: "Shopify", category: "ecommerce", description: "Leading e-commerce platform with storefront API", tier: "pro" },
          { name: "WooCommerce", category: "ecommerce", description: "WordPress-powered e-commerce REST API", tier: "pro" },
          { name: "BigCommerce", category: "ecommerce", description: "Enterprise e-commerce with headless commerce", tier: "enterprise" },
          { name: "ClickFunnels", category: "ecommerce", description: "Sales funnel builder & landing pages", tier: "pro" },
          { name: "Square POS", category: "ecommerce", description: "Point-of-sale & omnichannel commerce", tier: "pro" },
          { name: "Stripe Billing", category: "ecommerce", description: "Subscription billing & recurring payments", tier: "pro" },
          { name: "Afterpay", category: "ecommerce", description: "Buy-now-pay-later payment integration", tier: "pro" },
        ],
      },
      {
        name: "Marketplaces",
        apis: [
          { name: "Amazon Selling Partner", category: "marketplace", description: "Amazon seller central API for listings & orders", tier: "pro" },
          { name: "eBay", category: "marketplace", description: "Global online auction & fixed-price marketplace", tier: "pro" },
          { name: "Etsy", category: "marketplace", description: "Handmade & vintage goods marketplace", tier: "pro" },
          { name: "Walmart Marketplace", category: "marketplace", description: "Walmart third-party seller API", tier: "enterprise" },
          { name: "AliExpress", category: "marketplace", description: "Consumer sourcing & dropshipping marketplace", tier: "pro" },
          { name: "Alibaba Open Platform", category: "marketplace", description: "B2B global wholesale sourcing", tier: "enterprise" },
          { name: "Faire", category: "marketplace", description: "Independent retail wholesale marketplace", tier: "pro" },
        ],
      },
      {
        name: "Digital Products & Courses",
        apis: [
          { name: "Gumroad", category: "digital", description: "Digital product sales & creator commerce", tier: "pro" },
          { name: "Teachable", category: "digital", description: "Online course creation & sales platform", tier: "pro" },
          { name: "Kajabi", category: "digital", description: "All-in-one creator & coaching platform", tier: "enterprise" },
        ],
      },
      {
        name: "Fulfillment & Logistics",
        apis: [
          { name: "ShipStation", category: "shipping", description: "Multi-carrier shipping & order fulfillment", tier: "pro" },
          { name: "Printful", category: "pod", description: "Print-on-demand production & fulfillment", tier: "pro" },
          { name: "Printify", category: "pod", description: "Print-on-demand product creation network", tier: "pro" },
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
        name: "Property Data & Listings",
        apis: [
          { name: "Zillow", category: "listings", description: "Property listings, Zestimate valuations & market data", tier: "pro" },
          { name: "Realtor.com", category: "listings", description: "MLS-powered real estate listings API", tier: "pro" },
          { name: "Redfin", category: "listings", description: "Real estate brokerage data & market insights", tier: "pro" },
          { name: "ATTOM", category: "data", description: "Property data, tax, deed & foreclosure records", tier: "enterprise" },
          { name: "CoreLogic", category: "data", description: "Property intelligence & analytics platform", tier: "enterprise" },
        ],
      },
      {
        name: "Investment & Analysis",
        apis: [
          { name: "RentCast", category: "analysis", description: "Rental property analysis & market rents", tier: "pro" },
          { name: "Mashvisor", category: "analysis", description: "Investment property analytics & Airbnb data", tier: "pro" },
          { name: "PropStream", category: "analysis", description: "Real estate data & lead generation", tier: "enterprise" },
          { name: "BatchLeads", category: "analysis", description: "Property skip tracing & lead lists", tier: "pro" },
        ],
      },
      {
        name: "Communication & Outreach",
        apis: [
          { name: "Twilio SMS", category: "comms", description: "SMS campaigns for motivated seller outreach", tier: "pro" },
        ],
      },
      {
        name: "Documents & Legal",
        apis: [
          { name: "DocuSign", category: "esign", description: "Electronic signatures for contracts & leases", tier: "enterprise" },
          { name: "HelloSign", category: "esign", description: "E-signature solution for real estate docs", tier: "pro" },
        ],
      },
      {
        name: "Mapping & Location",
        apis: [
          { name: "Google Maps", category: "mapping", description: "Geocoding, directions & property mapping", tier: "pro" },
          { name: "OpenStreetMap", category: "mapping", description: "Open-source mapping & geospatial data", tier: "free" },
          { name: "Census Bureau Data", category: "demographics", description: "US census demographics & economic data", tier: "free" },
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
