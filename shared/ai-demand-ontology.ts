export const DEMAND_CATALOG_IDS = ["ai_usage", "downloaded_apps", "online_purchases"] as const;
export type DemandCatalogId = (typeof DEMAND_CATALOG_IDS)[number];

type DemandGroup = {
  category: string;
  taskCategory: string;
  capabilities: string[];
  reasons: string[];
};

export type DemandReason = {
  id: string;
  catalogId: DemandCatalogId;
  rank: number;
  reason: string;
  category: string;
  taskCategory: string;
  capabilities: string[];
};

export const DEMAND_RESEARCH_SOURCES = [
  {
    id: "openai-consumer-usage-2025",
    catalogs: ["ai_usage"],
    title: "How people are using ChatGPT",
    organization: "OpenAI Economic Research",
    url: "https://openai.com/index/how-people-are-using-chatgpt/",
    evidence: "Large-scale privacy-preserving consumer usage study covering practical guidance, information seeking, writing, asking, doing, and expressing.",
  },
  {
    id: "openai-work-usage-2026",
    catalogs: ["ai_usage"],
    title: "ChatGPT usage and adoption patterns at work",
    organization: "OpenAI",
    url: "https://openai.com/business/guides-and-resources/chatgpt-usage-and-adoption-patterns-at-work/",
    evidence: "Workplace usage clusters including writing, research, programming, analysis, troubleshooting, and media generation.",
  },
  {
    id: "sensor-tower-mobile-2026",
    catalogs: ["downloaded_apps"],
    title: "State of Mobile 2026",
    organization: "Sensor Tower",
    url: "https://sensortower.com/press/press-release-boosted-by-gen-ai-services-consumers-spent-more-money-in-apps-than-games-for-first-time",
    evidence: "Mobile attention and spending across games, social, entertainment, lifestyle, productivity, and generative AI services.",
  },
  {
    id: "apple-app-store-2025",
    catalogs: ["downloaded_apps"],
    title: "2025 App Store Transparency Report",
    organization: "Apple",
    url: "https://www.apple.com/legal/app-store/transparency/2025/",
    evidence: "Official App Store category taxonomy including utilities, games, lifestyle, productivity, entertainment, business, finance, education, food, and shopping.",
  },
  {
    id: "eurostat-ecommerce-2026",
    catalogs: ["online_purchases"],
    title: "E-commerce statistics for individuals",
    organization: "Eurostat",
    url: "https://ec.europa.eu/eurostat/statistics-explained/index.php?title=E-commerce_statistics_for_individuals",
    evidence: "Online purchase categories and benefits including broad selection, price comparison, home convenience, and consumer reviews.",
  },
  {
    id: "stripe-checkout-2026",
    catalogs: ["online_purchases"],
    title: "How agents, digital wallets, and trust are rewriting checkout",
    organization: "Stripe",
    url: "https://stripe.com/blog/global-checkout-trends",
    evidence: "Checkout research covering trust, convenience, payment preferences, localization, wallets, and cross-border purchases.",
  },
  {
    id: "baymard-commerce-2026",
    catalogs: ["online_purchases"],
    title: "Quantitative ecommerce purchase insights",
    organization: "Baymard Institute",
    url: "https://baymard.com/blog/home-and-hardware-quantitative-ux-insights",
    evidence: "Purchase factors including price, brand, reviews, convenience, delivery speed, compatibility, warranty, and returns.",
  },
] as const;

const AI_USAGE_GROUPS: DemandGroup[] = [
  { category: "Practical guidance", taskCategory: "Reasoning", capabilities: ["practical guidance", "planning", "decision support"], reasons: [
    "Get step-by-step help with an unfamiliar task", "Compare choices before making a decision", "Create a plan for a personal goal", "Troubleshoot an everyday problem", "Prepare a checklist for a complex process", "Turn a vague goal into clear next actions", "Get recommendations tailored to constraints", "Practice a difficult conversation or scenario", "Understand risks and tradeoffs", "Organize advice from several viewpoints",
  ] },
  { category: "Information and research", taskCategory: "Research", capabilities: ["web research", "source synthesis", "fact checking"], reasons: [
    "Find an answer faster than manual searching", "Summarize current information from reliable sources", "Research a product, service, or market", "Explain a news topic with supporting context", "Compare evidence across sources", "Build a cited research brief", "Find laws, programs, grants, or public resources", "Extract key findings from long reports", "Identify unanswered questions and research gaps", "Monitor a topic for meaningful updates",
  ] },
  { category: "Writing and communication", taskCategory: "Multilingual and Translation", capabilities: ["writing", "editing", "tone adaptation"], reasons: [
    "Draft an email or message", "Rewrite text for clarity", "Adjust tone for a specific audience", "Summarize meeting notes", "Create a report, memo, or proposal", "Develop an outline before writing", "Proofread grammar and spelling", "Turn bullet points into polished copy", "Prepare scripts, speeches, or presentations", "Translate and localize communication",
  ] },
  { category: "Coding and technical work", taskCategory: "Coding", capabilities: ["coding", "debugging", "software testing"], reasons: [
    "Generate a working code prototype", "Debug an error or failed test", "Explain unfamiliar code", "Write unit and integration tests", "Refactor code for maintainability", "Design an application architecture", "Create scripts that automate repetitive work", "Review code for security and quality", "Learn a programming language or framework", "Prepare an application for deployment",
  ] },
  { category: "Learning and education", taskCategory: "Reasoning", capabilities: ["tutoring", "curriculum design", "assessment"], reasons: [
    "Learn a concept at the right reading level", "Get personalized tutoring", "Create a study plan", "Generate quizzes and practice problems", "Receive feedback on an assignment", "Turn notes into flashcards", "Build a lesson or course", "Practice a language", "Simulate a lab or training scenario", "Convert learning material into an educational game",
  ] },
  { category: "Data and analysis", taskCategory: "Data Analysis", capabilities: ["data analysis", "visualization", "forecasting"], reasons: [
    "Clean and organize a dataset", "Analyze a spreadsheet", "Write or debug a database query", "Explain trends and anomalies", "Create charts and dashboards", "Build a forecast or scenario", "Calculate metrics and return on investment", "Compare business performance", "Turn data into an executive summary", "Design a repeatable analytics workflow",
  ] },
  { category: "Creative and media", taskCategory: "Image Generation", capabilities: ["creative ideation", "image generation", "media production"], reasons: [
    "Brainstorm creative concepts", "Generate or edit an image", "Develop a brand identity or logo", "Write a story, poem, or screenplay", "Plan a video or movie", "Create music, lyrics, or audio concepts", "Build characters and fictional worlds", "Design a game or simulation", "Create social media content", "Prepare a storyboard and production packet",
  ] },
  { category: "Business and customers", taskCategory: "Agents", capabilities: ["business planning", "sales", "customer operations"], reasons: [
    "Develop a business plan", "Research customer needs", "Qualify and organize leads", "Draft sales outreach for approval", "Prepare marketing campaigns", "Improve customer support responses", "Document standard operating procedures", "Analyze competitors", "Create a product requirements document", "Plan a launch or expansion",
  ] },
  { category: "Personal productivity", taskCategory: "Agents", capabilities: ["task management", "scheduling", "personal organization"], reasons: [
    "Prioritize a task list", "Plan a day, week, or project", "Prepare for a meeting or appointment", "Track goals and progress", "Organize files, notes, or knowledge", "Create reminders and recurring routines", "Plan travel and logistics", "Manage bills and subscriptions", "Prepare forms and applications", "Coordinate work across several apps",
  ] },
  { category: "Accessibility and support", taskCategory: "Accessibility", capabilities: ["accessibility", "speech", "simplification"], reasons: [
    "Read or summarize difficult text", "Convert speech to text", "Turn text into accessible speech", "Create captions and transcripts", "Describe an image", "Simplify instructions for cognitive accessibility", "Translate communication in real time", "Adapt content for screen readers", "Practice job interviews and role-play", "Reflect on emotions without replacing professional care",
  ] },
];

const DOWNLOADED_APP_GROUPS: DemandGroup[] = [
  { category: "Communication and community", taskCategory: "Agents", capabilities: ["messaging", "community", "collaboration"], reasons: [
    "Message friends and family", "Make voice or video calls", "Join interest-based communities", "Collaborate with coworkers", "Share photos and updates", "Meet new people", "Manage group conversations", "Attend virtual events", "Communicate across languages", "Stay connected across devices",
  ] },
  { category: "Entertainment and games", taskCategory: "Simulation", capabilities: ["games", "streaming", "interactive entertainment"], reasons: [
    "Play casual games", "Play competitive multiplayer games", "Stream movies and television", "Watch short-form video", "Listen to music and podcasts", "Read digital books or comics", "Follow live sports", "Explore interactive stories", "Use augmented or virtual reality", "Pass time with personalized entertainment",
  ] },
  { category: "Productivity and work", taskCategory: "Agents", capabilities: ["productivity", "documents", "automation"], reasons: [
    "Manage tasks and projects", "Create and edit documents", "Take and organize notes", "Scan and manage files", "Join work meetings", "Track time and habits", "Automate routine work", "Access business systems remotely", "Sign documents", "Coordinate a mobile workforce",
  ] },
  { category: "Money and commerce", taskCategory: "Data Analysis", capabilities: ["personal finance", "payments", "commerce"], reasons: [
    "Check bank accounts", "Send or receive money", "Pay bills", "Track a budget", "Invest or monitor markets", "Manage credit", "Shop online", "Compare prices and coupons", "Sell products or services", "Accept business payments",
  ] },
  { category: "Travel and local discovery", taskCategory: "Search and Retrieval", capabilities: ["maps", "booking", "local search"], reasons: [
    "Navigate with maps", "Check traffic and transit", "Book flights or lodging", "Order transportation", "Find nearby businesses", "Plan a trip itinerary", "Translate while traveling", "Store tickets and boarding passes", "Track deliveries or vehicles", "Discover local events and experiences",
  ] },
  { category: "Health and wellness", taskCategory: "Safety and Moderation", capabilities: ["wellness tracking", "health education", "safety boundaries"], reasons: [
    "Track exercise", "Monitor sleep", "Plan meals and nutrition", "Practice meditation", "Track symptoms for a clinician", "Manage medication reminders", "Access telehealth", "Support a fitness program", "Track reproductive health", "Access crisis and safety resources",
  ] },
  { category: "Education and skills", taskCategory: "Reasoning", capabilities: ["learning", "practice", "assessment"], reasons: [
    "Take an online course", "Learn a language", "Help with homework", "Practice professional skills", "Prepare for a test", "Learn music or art", "Access a digital library", "Teach a child", "Complete workplace training", "Build and test code",
  ] },
  { category: "Lifestyle and services", taskCategory: "Search and Retrieval", capabilities: ["booking", "delivery", "service discovery"], reasons: [
    "Order food", "Buy groceries", "Book beauty or personal care", "Find home services", "Manage smart-home devices", "Plan recipes", "Organize family schedules", "Find housing or real estate", "Care for pets", "Access government or community services",
  ] },
  { category: "Creation and publishing", taskCategory: "Image Editing", capabilities: ["photo editing", "video editing", "publishing"], reasons: [
    "Take and edit photos", "Record and edit video", "Create graphics and designs", "Make music or audio", "Publish social content", "Live stream", "Build presentations", "Write and publish stories", "Create avatars or characters", "Manage a creator business",
  ] },
  { category: "Utilities and device control", taskCategory: "Coding", capabilities: ["device utilities", "security", "file management"], reasons: [
    "Protect passwords and accounts", "Store files in the cloud", "Back up a device", "Block spam and fraud", "Control connected devices", "Monitor battery, storage, or network use", "Scan documents and codes", "Customize device accessibility", "Use a browser or search utility", "Install developer and diagnostic tools",
  ] },
];

const ONLINE_PURCHASE_GROUPS: DemandGroup[] = [
  { category: "Convenience and time", taskCategory: "Agents", capabilities: ["checkout", "automation", "convenience"], reasons: [
    "Buy without traveling to a store", "Shop at any time", "Complete checkout quickly", "Save payment and delivery details", "Reorder a familiar product", "Schedule recurring delivery", "Use one-click or wallet checkout", "Avoid crowds and waiting lines", "Combine research and purchase in one session", "Delegate an approved purchase to an assistant",
  ] },
  { category: "Price and value", taskCategory: "Search and Retrieval", capabilities: ["price comparison", "coupons", "value analysis"], reasons: [
    "Find a lower price", "Compare prices across sellers", "Use a coupon or promotion", "Earn cashback or rewards", "Access an online-only discount", "Buy a bundle", "Choose a subscription discount", "Compare total cost of ownership", "Track a price drop", "Buy used, refurbished, or surplus goods",
  ] },
  { category: "Selection and access", taskCategory: "Research", capabilities: ["product discovery", "comparison", "accessibility"], reasons: [
    "Access a wider selection", "Buy something unavailable locally", "Purchase from another country", "Find a specific size, color, or configuration", "Order a customized product", "Access a niche specialist", "Buy directly from a creator", "Purchase accessible products", "Find rare or collectible items", "Preorder a new product",
  ] },
  { category: "Trust and confidence", taskCategory: "Safety and Moderation", capabilities: ["reviews", "fraud checks", "purchase risk"], reasons: [
    "Read customer reviews", "Buy from a trusted brand", "Verify product compatibility", "Review warranty coverage", "Confirm return and refund terms", "Use buyer protection", "Choose a trusted payment method", "Check seller reputation", "Verify authenticity", "Review privacy and data practices",
  ] },
  { category: "Delivery and fulfillment", taskCategory: "Forecasting", capabilities: ["delivery", "inventory", "logistics"], reasons: [
    "Get home delivery", "Receive same-day or faster delivery", "Pick up an order locally", "Track a shipment", "Send a gift directly", "Schedule delivery for a preferred time", "Avoid carrying a large item", "Reserve inventory before visiting", "Arrange installation with delivery", "Access simple online returns",
  ] },
  { category: "Digital content and experiences", taskCategory: "Video", capabilities: ["digital delivery", "media", "events"], reasons: [
    "Subscribe to movies or television", "Subscribe to music or podcasts", "Buy a video game", "Purchase an in-game item", "Buy an ebook or audiobook", "Purchase event tickets", "Pay for a live stream", "Buy a digital creator product", "License stock media or software", "Access premium online communities",
  ] },
  { category: "Learning and professional growth", taskCategory: "Reasoning", capabilities: ["education", "credentials", "career development"], reasons: [
    "Buy an online course", "Pay for tutoring", "Purchase test preparation", "Earn a professional certification", "Attend a virtual conference", "Buy educational software", "Purchase school materials", "Access research or publications", "Hire a coach or mentor", "Pay for job-search services",
  ] },
  { category: "Business and software", taskCategory: "Coding", capabilities: ["software", "business services", "infrastructure"], reasons: [
    "Subscribe to business software", "Buy cloud hosting or storage", "Register a domain", "Purchase an API or data service", "Hire a freelancer or contractor", "Buy advertising", "Purchase design or development services", "Pay for accounting or legal support", "Order business supplies", "Buy a license for commercial use",
  ] },
  { category: "Financial and household commitments", taskCategory: "Data Analysis", capabilities: ["billing", "financial planning", "household management"], reasons: [
    "Pay a utility bill", "Pay rent or housing costs", "Make an insurance payment", "Pay taxes or government fees", "Repay a loan", "Add money to savings or investments", "Purchase travel or event insurance", "Pay for healthcare", "Make a charitable donation", "Support a creator or crowdfunding campaign",
  ] },
  { category: "Personalized and recurring service", taskCategory: "Agents", capabilities: ["personalization", "subscriptions", "service management"], reasons: [
    "Receive personalized recommendations", "Maintain an ongoing membership", "Book an appointment", "Reserve travel or accommodation", "Order transportation", "Pay for food delivery", "Subscribe to recurring essentials", "Upgrade to remove ads or limits", "Unlock premium support", "Pay for a safer, faster, or more reliable experience",
  ] },
];

function flatten(catalogId: DemandCatalogId, groups: DemandGroup[]) {
  let rank = 0;
  return groups.flatMap((group) => group.reasons.map((reason) => ({
    id: `${catalogId}-${String(++rank).padStart(3, "0")}`,
    catalogId,
    rank,
    reason,
    category: group.category,
    taskCategory: group.taskCategory,
    capabilities: group.capabilities,
  })));
}

export const DEMAND_REASONS: DemandReason[] = [
  ...flatten("ai_usage", AI_USAGE_GROUPS),
  ...flatten("downloaded_apps", DOWNLOADED_APP_GROUPS),
  ...flatten("online_purchases", ONLINE_PURCHASE_GROUPS),
];

for (const catalogId of DEMAND_CATALOG_IDS) {
  const count = DEMAND_REASONS.filter((reason) => reason.catalogId === catalogId).length;
  if (count !== 100) throw new Error(`Expected 100 ${catalogId} reasons, found ${count}`);
}
