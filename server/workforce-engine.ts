import { createHash, randomUUID } from "node:crypto";

import { z } from "zod";

export const AUTOMATION_LEVELS = {
  A: {
    label: "Fully Automatable",
    automationPercent: 95,
    explanation: "Bounded internal digital work may run in Shadow Mode after configuration and authorization.",
  },
  B: {
    label: "Autonomous With Human Approval",
    automationPercent: 80,
    explanation: "Buddy may prepare the work, but each external action requires fresh exact approval.",
  },
  C: {
    label: "Human-Supervised Assistance",
    automationPercent: 55,
    explanation: "Buddy prepares research, drafts, calculations, and options for an authorized human decision.",
  },
  D: {
    label: "Licensed Professional Controlled",
    automationPercent: 35,
    explanation: "A verified professional controls conclusions, approval, and final delivery.",
  },
  E: {
    label: "Human or Physical Execution Required",
    automationPercent: 20,
    explanation: "Buddy may coordinate and document the work but cannot claim to physically perform it.",
  },
  F: {
    label: "Prohibited or Unsupported",
    automationPercent: 0,
    explanation: "The requested work is rejected because it is illegal, deceptive, unsafe, or unauthorized.",
  },
} as const;

export type AutomationLevel = keyof typeof AUTOMATION_LEVELS;

export const jobOpportunityRequestSchema = z.object({
  ownerUserId: z.string().trim().min(2).max(80),
  title: z.string().trim().min(2).max(180),
  description: z.string().trim().min(20).max(20_000),
  responsibilities: z.array(z.string().trim().min(3).max(1_000)).max(100).default([]),
  requiredTools: z.array(z.string().trim().min(2).max(120)).max(50).default([]),
  sourceType: z.enum(["owner_supplied", "public_listing", "authorized_feed", "synthetic_test"]).default("owner_supplied"),
  sourceReference: z.string().trim().max(500).default(""),
  statedBudget: z.number().finite().nonnegative().max(100_000_000).optional(),
  currency: z.string().trim().regex(/^[A-Z]{3}$/).default("USD"),
}).strict();

export type JobOpportunityRequest = z.infer<typeof jobOpportunityRequestSchema>;

export const paymentRoutingRequestSchema = z.object({
  ownerUserId: z.string().trim().min(2).max(80),
  amount: z.number().finite().positive().max(100_000_000),
  currency: z.string().trim().regex(/^[A-Z]{3}$/).default("USD"),
  paymentType: z.enum(["one_time", "subscription", "installment", "invoice", "revenue_share", "affiliate_payout"]),
  customerRegion: z.string().trim().min(2).max(100),
  sellerRegion: z.string().trim().min(2).max(100),
  preferredProviders: z.array(z.enum(["stripe", "paypal", "square", "bank_transfer", "crypto", "piepay"])).max(6).default([]),
  prioritize: z.enum(["lowest_cost", "fastest_settlement", "highest_reliability", "customer_choice"]).default("highest_reliability"),
}).strict();

export const professionalReviewRequestSchema = z.object({
  ownerUserId: z.string().trim().min(2).max(80),
  workTitle: z.string().trim().min(3).max(200),
  domain: z.enum(["legal", "medical", "financial", "tax", "engineering", "architecture", "insurance", "real_estate"]),
  jurisdiction: z.string().trim().min(2).max(160),
  draftReference: z.string().trim().min(3).max(240),
  responsibleProfessionalId: z.string().trim().max(120).default(""),
  licenseVerificationReference: z.string().trim().max(240).default(""),
}).strict();

export const voiceSandboxRequestSchema = z.object({
  ownerUserId: z.string().trim().min(2).max(80),
  useCase: z.enum(["inbound_support", "appointment", "requested_callback", "intake", "order_status", "faq", "consented_qualification", "payment_reminder", "survey", "receptionist", "internal"]),
  script: z.string().trim().min(20).max(10_000),
  outbound: z.boolean().default(false),
  recipientConsentReference: z.string().trim().max(240).default(""),
  recordingEnabled: z.boolean().default(false),
  recordingConsentReference: z.string().trim().max(240).default(""),
}).strict();

type WorkerTeam = {
  system: "payments" | "sales" | "competition" | "opportunity";
  team: string;
  mission: string;
  capabilities: string[];
  roles: string[];
};

const WORKER_TEAMS: WorkerTeam[] = [
  {
    system: "payments",
    team: "revenue_operations",
    mission: "Prepare auditable revenue operations without processing or moving money from this planning system.",
    capabilities: ["provider comparison", "fee and settlement analysis", "approval packet creation", "reconciliation planning", "risk disclosure", "audit evidence"],
    roles: ["Payment Routing Coordinator", "Subscription Billing Planner", "One-Time Payment Planner", "Installment Plan Designer", "Quote and Estimate Builder", "Invoice Workflow Planner", "Revenue Share Calculator", "Affiliate Payout Planner", "Commission Tracker", "Tax and Reporting Organizer", "Chargeback Assistance Coordinator", "Payment Analytics Agent", "Financial Forecasting Agent"],
  },
  {
    system: "sales",
    team: "executive",
    mission: "Set governed revenue goals, capacity, and evidence-based forecasts.",
    capabilities: ["goal setting", "KPI monitoring", "worker allocation", "forecasting", "capacity limits", "owner reporting"],
    roles: ["Chief Revenue Officer Bot"],
  },
  {
    system: "sales",
    team: "lead_generation",
    mission: "Find permissioned demand signals and prepare source-backed candidate records.",
    capabilities: ["authorized source research", "candidate deduplication", "need signal extraction", "permission basis recording", "fit scoring", "owner review queue"],
    roles: ["Company Finder", "Contact Finder", "Decision Maker Finder", "Local Business Hunter", "Government Contract Finder", "Grant Opportunity Finder", "RFP Finder", "AI Job Finder", "Referral Finder", "Professional Network Opportunity Finder"],
  },
  {
    system: "sales",
    team: "prospect_intelligence",
    mission: "Turn permitted public and owner-supplied evidence into explainable prospect intelligence.",
    capabilities: ["company research", "competitor comparison", "pain point analysis", "technology mapping", "news monitoring", "buying signal detection", "financial health indicators", "organization mapping"],
    roles: ["Company Research Bot", "Competitor Analyzer", "Pain Point Finder", "Technology Stack Scanner", "News Monitor", "Buying Signal Detector", "Financial Health Analyzer", "Organization Chart Builder"],
  },
  {
    system: "sales",
    team: "outreach",
    mission: "Draft permission-aware outreach and stop before every external send or call.",
    capabilities: ["message drafting", "channel permission check", "opt-out handling", "follow-up timing", "appointment preparation", "script review", "one-message approval", "suppression ledger"],
    roles: ["Cold Email Bot", "SMS Bot", "Professional Network Messaging Bot", "Social Outreach Bot", "Personalized Video Script Bot", "Follow-up Scheduler", "Appointment Setter", "Meeting Confirmation Bot"],
  },
  {
    system: "sales",
    team: "conversation",
    mission: "Prepare truthful sales conversations and human handoffs.",
    capabilities: ["needs assessment", "FAQ preparation", "objection analysis", "product demonstration plan", "identity disclosure", "uncertainty escalation", "human handoff"],
    roles: ["Live Chat Sales Agent", "Voice Sales Agent", "Website AI Representative", "FAQ Agent", "Objection Handler", "Product Demonstrator", "Needs Assessment Agent"],
  },
  {
    system: "sales",
    team: "proposal",
    mission: "Prepare nonbinding proposals, quotes, ROI evidence, contracts, and signature workflows.",
    capabilities: ["proposal drafting", "quote calculation", "ROI assumptions", "price scenario analysis", "contract draft preparation", "signature workflow planning", "risk disclosure"],
    roles: ["Proposal Writer", "Quote Generator", "ROI Calculator", "Pricing Optimizer", "Contract Generator", "E-signature Workflow Assistant"],
  },
  {
    system: "sales",
    team: "negotiation_and_closing",
    mission: "Support human-controlled negotiation, closing, payment, and onboarding decisions.",
    capabilities: ["counteroffer options", "discount analysis", "competitive comparison", "deal risk analysis", "closing checklist", "payment approval packet", "onboarding coordination"],
    roles: ["Negotiation Coach", "Counteroffer Generator", "Discount Advisor", "Competitive Comparison Agent", "Risk Analyzer", "Closing Assistant", "Payment Collection Assistant", "Contract Completion Assistant", "Onboarding Coordinator", "Customer Welcome Agent"],
  },
  {
    system: "sales",
    team: "customer_success",
    mission: "Prepare customer success actions for opted-in customers without unsolicited messaging.",
    capabilities: ["check-in planning", "upsell fit analysis", "cross-sell fit analysis", "renewal tracking", "referral request drafting", "testimonial consent check", "review request drafting"],
    roles: ["Check-in Bot", "Upsell Bot", "Cross-sell Bot", "Renewal Manager", "Referral Manager", "Testimonial Collector", "Review Request Bot"],
  },
  {
    system: "sales",
    team: "sales_operations",
    mission: "Maintain an owner-controlled sales system of record and explain performance.",
    capabilities: ["CRM synchronization plan", "pipeline management", "territory planning", "commission calculation", "dashboard preparation", "forecasting", "activity evidence", "performance coaching"],
    roles: ["CRM Synchronizer", "Pipeline Manager", "Territory Manager", "Commission Calculator", "Sales Dashboard", "Forecast Dashboard", "Activity Tracker", "Performance Coach"],
  },
  {
    system: "sales",
    team: "marketing_and_coaching",
    mission: "Build truthful campaigns and practice sales skills in a sandbox.",
    capabilities: ["campaign planning", "landing page drafting", "ad copy drafting", "email campaign preparation", "social content preparation", "webinar planning", "call review", "role-play simulation", "quality scoring"],
    roles: ["Campaign Builder", "Landing Page Assistant", "Ad Copy Generator", "Email Campaign Manager", "Social Content Creator", "Webinar Coordinator", "Call Review Agent", "Email Quality Reviewer", "Pitch Coach", "Role-play Trainer", "Closing Skills Trainer", "Sales Certification Agent"],
  },
  {
    system: "competition",
    team: "leadership_and_discovery",
    mission: "Maintain lawful, source-backed market intelligence from public documentation and approved testing.",
    capabilities: ["competitor catalog", "product discovery", "public documentation review", "open-source discovery", "marketplace monitoring", "roadmap prioritization", "source date tracking"],
    roles: ["Chief Competition Officer", "Strategy Council", "Competitive Research Director", "Product Discovery Bot", "Startup Scanner", "GitHub Repository Scanner", "AI Marketplace Scanner", "Product Launch Scanner", "App Store Scanner", "Browser Extension Scanner", "SaaS Discovery Bot", "Open Source Discovery Bot", "Patent Watch Bot"],
  },
  {
    system: "competition",
    team: "capability_and_technical_benchmark",
    mission: "Run reproducible feature, quality, cost, reliability, security, and usability comparisons.",
    capabilities: ["feature matrix", "workflow comparison", "UX comparison", "API comparison", "latency benchmark", "resource benchmark", "failure recovery test", "regression test", "reproducible evidence"],
    roles: ["Feature Comparison Bot", "Capability Inventory Bot", "Missing Feature Detector", "Duplicate Feature Detector", "Workflow Comparison Bot", "UX Comparison Bot", "API Comparison Bot", "Automation Comparison Bot", "Reasoning Comparison Bot", "Speed Benchmark Bot", "Accuracy Benchmark Bot", "Latency Benchmark Bot", "Memory Benchmark Bot", "CPU Benchmark Bot", "GPU Benchmark Bot", "Reliability Benchmark Bot", "Recovery Benchmark Bot", "Scalability Benchmark Bot"],
  },
  {
    system: "competition",
    team: "quality_and_intelligence",
    mission: "Measure model quality, customer value, security, maintainability, and improvement over prior releases.",
    capabilities: ["reasoning evaluation", "tool-use evaluation", "coding evaluation", "hallucination checks", "conversion evidence", "accessibility review", "security review", "dependency health", "technical debt", "release scorecard"],
    roles: ["Reasoning Evaluator", "Planning Evaluator", "Long Context Evaluator", "Tool Usage Evaluator", "Coding Quality Evaluator", "Research Quality Evaluator", "Creativity Evaluator", "Multi-step Execution Evaluator", "Learning Capability Evaluator", "Hallucination Evaluator", "Sales Benchmark Agent", "User Experience Reviewer", "Security Benchmark Agent", "Revenue Benchmark Agent", "Innovation Research Agent", "Quality Assurance Agent", "Code Benchmark Agent", "Executive Report Agent", "Release Learning Agent"],
  },
  {
    system: "opportunity",
    team: "autonomous_workforce_engine",
    mission: "Convert lawful market demand into Shadow Mode service evidence and owner-controlled work packets.",
    capabilities: ["market scan", "job discovery", "task extraction", "A-F classification", "capability matching", "service generation", "profit simulation", "risk review", "quality evidence", "outcome learning"],
    roles: ["Market Scan Bot", "Job Discovery Bot", "Task Extraction Bot", "Automation Classifier", "Capability Match Bot", "Service Opportunity Builder", "Feasibility Test Bot", "Profit Simulation Bot", "Risk Review Bot", "Owner Approval Coordinator", "Client Acquisition Planner", "Work Execution Coordinator", "Quality Review Bot", "Delivery Approval Coordinator", "Invoice Approval Coordinator", "Payment Tracking Bot", "Outcome Learning Bot", "Professional Collaboration Coordinator", "Voice Operations Sandbox Bot"],
  },
];

function slugify(value: string): string {
  return value.toLowerCase().replace(/&/g, " and ").replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "");
}

function buildWorkers() {
  return WORKER_TEAMS.flatMap((team) => team.roles.map((role) => ({
    id: `${team.system}-${slugify(role)}`,
    displayName: role,
    system: team.system,
    team: team.team,
    mission: `${role} supports ${team.mission.charAt(0).toLowerCase()}${team.mission.slice(1)}`,
    capabilities: [...team.capabilities],
    runtime: "buddy_shared_governed_worker",
    defaultMode: "shadow",
    sandbox: {
      networkDefault: "off",
      fixtures: "synthetic_or_owner_authorized",
      externalWrites: false,
      evidenceRequired: true,
    },
    approvals: {
      externalAction: "fresh_exact_owner_approval",
      moneyMovement: "fresh_exact_owner_approval_and_configured_payment_adapter",
      regulatedConclusion: "verified_professional_approval",
      identityUse: "owner_presence_and_scoped_consent",
    },
    status: "shadow_ready",
  })));
}

const PROHIBITED_TERMS = ["steal", "fraud", "fake identity", "impersonate", "bypass access", "hack into", "spoof caller", "ignore opt out", "evade platform", "forge signature"];
const PHYSICAL_TERMS = ["construct", "repair vehicle", "deliver package", "clean building", "install equipment", "nursing procedure", "physical inspection", "on-site photography", "drive truck", "operate machinery"];
const EXTERNAL_TERMS = ["send email", "send message", "publish", "deploy production", "contact lead", "place call", "submit application", "invoice customer", "charge customer", "sign contract", "accept terms", "hire worker"];
const SUPERVISED_TERMS = ["negotiate", "hiring decision", "employee evaluation", "financial planning", "security remediation", "contract analysis", "recommend strategy", "approve vendor"];
const SENSITIVE_TERMS = ["health record", "patient", "social security", "payment card", "bank account", "criminal record", "employee record", "student record", "biometric", "password", "secret key"];

const PROFESSIONAL_DOMAINS: Array<{ domain: string; terms: string[]; bots: string[] }> = [
  { domain: "medical", terms: ["diagnose", "treatment plan", "prescribe", "physician", "nurse", "pharmacist", "therapy", "medical advice"], bots: ["telehealth-assistant", "therapy-notes-ai"] },
  { domain: "legal", terms: ["legal advice", "represent in court", "legal opinion", "attorney", "court filing", "patent opinion"], bots: ["legal-risk-scorer", "legal-contract-lifecycle"] },
  { domain: "tax", terms: ["tax return", "tax attestation", "tax preparer", "accounting attestation"], bots: ["tax-optimizer", "client-billing"] },
  { domain: "financial", terms: ["investment recommendation", "financial advisor", "securities", "personalized portfolio"], bots: ["investment-opp-scorer", "financial-kpi-auto"] },
  { domain: "engineering", terms: ["engineering certification", "structural approval", "engineering stamp"], bots: ["construction-estimator", "safety-compliance-const"] },
  { domain: "architecture", terms: ["architecture stamp", "architect of record", "building code approval"], bots: ["construction-analytics-elite", "safety-compliance-const"] },
  { domain: "real_estate", terms: ["licensed real estate", "represent buyer", "represent seller", "real estate agent"], bots: ["commercial-scanner", "property-mgmt"] },
  { domain: "insurance", terms: ["insurance determination", "insurance agent", "bind coverage"], bots: ["risk-manager", "client-billing"] },
];

const CAPABILITY_ROUTES = [
  { terms: ["code", "software", "website", "api", "database", "bug", "deployment"], bots: ["code-reader", "ai-pair-prog", "test-generator", "deployment-mgr"] },
  { terms: ["sales", "lead", "crm", "proposal", "customer"], bots: ["icp-builder", "pitch-craft-ai", "sales-performance", "client-success"] },
  { terms: ["photo", "image", "design", "video", "animation"], bots: ["photo-video-app-bot", "video-editor-ai", "brand-builder"] },
  { terms: ["data", "spreadsheet", "analysis", "dashboard"], bots: ["analytics-hub", "data-cleaner", "bi-dashboard"] },
  { terms: ["contract", "grant", "rfp", "government"], bots: ["gov-contract-bot", "grant-finder", "consulting-proposal"] },
  { terms: ["payment", "invoice", "subscription", "commission"], bots: ["payment-gateway", "subscription-lifecycle-mgr", "client-billing"] },
  { terms: ["education", "teach", "course", "tutor"], bots: ["curriculum-mapper", "tutoring-matcher", "video-script"] },
  { terms: ["research", "competitor", "market"], bots: ["research-bot", "competitive-intel", "competitive-benchmark"] },
  { terms: ["schedule", "administrative", "assistant", "project"], bots: ["task-scheduler", "project-management", "operations-setup"] },
];

function normalizedText(request: JobOpportunityRequest): string {
  return [request.title, request.description, ...request.responsibilities, ...request.requiredTools].join(" ").toLowerCase();
}

function includesAny(text: string, terms: string[]): string[] {
  return terms.filter((term) => text.includes(term));
}

function taskLevel(task: string): { level: AutomationLevel; professionalDomains: string[]; reasons: string[] } {
  const text = task.toLowerCase();
  const prohibited = includesAny(text, PROHIBITED_TERMS);
  if (prohibited.length) return { level: "F", professionalDomains: [], reasons: [`Prohibited signal: ${prohibited.join(", ")}`] };
  const professionalDomains = PROFESSIONAL_DOMAINS.filter((item) => includesAny(text, item.terms).length).map((item) => item.domain);
  if (professionalDomains.length) return { level: "D", professionalDomains, reasons: [`Professional control required: ${professionalDomains.join(", ")}`] };
  const physical = includesAny(text, PHYSICAL_TERMS);
  if (physical.length) return { level: "E", professionalDomains: [], reasons: [`Physical execution signal: ${physical.join(", ")}`] };
  const external = includesAny(text, EXTERNAL_TERMS);
  if (external.length) return { level: "B", professionalDomains: [], reasons: [`Fresh approval required before: ${external.join(", ")}`] };
  const supervised = includesAny(text, SUPERVISED_TERMS);
  if (supervised.length) return { level: "C", professionalDomains: [], reasons: [`Human decision remains responsible for: ${supervised.join(", ")}`] };
  return { level: "A", professionalDomains: [], reasons: ["Bounded internal digital preparation with reviewable output."] };
}

function extractTasks(request: JobOpportunityRequest): string[] {
  const explicit = request.responsibilities.map((item) => item.trim()).filter(Boolean);
  if (explicit.length) return [...new Set(explicit)].slice(0, 100);
  const extracted = request.description
    .split(/[\n.;]+/)
    .map((item) => item.replace(/^[-*\d.)\s]+/, "").trim())
    .filter((item) => item.length >= 8);
  return [...new Set(extracted.length ? extracted : [request.description.trim()])].slice(0, 100);
}

function routeCapabilities(text: string, professionalDomains: string[]) {
  const matches = CAPABILITY_ROUTES.filter((route) => route.terms.some((term) => text.includes(term))).flatMap((route) => route.bots);
  for (const domain of professionalDomains) {
    const match = PROFESSIONAL_DOMAINS.find((item) => item.domain === domain);
    if (match) matches.push(...match.bots);
  }
  return [...new Set(matches.length ? matches : ["research-bot", "task-scheduler", "analytics-hub"])].slice(0, 8);
}

function roundMoney(value: number): number {
  return Math.round(value * 100) / 100;
}

export function analyzeJobOpportunity(input: JobOpportunityRequest) {
  const request = jobOpportunityRequestSchema.parse(input);
  const sourceText = normalizedText(request);
  const sensitiveSignals = includesAny(sourceText, SENSITIVE_TERMS);
  const tasks = extractTasks(request).map((task, index) => {
    const classification = taskLevel(task);
    return {
      taskId: `job-task-${String(index + 1).padStart(3, "0")}`,
      task,
      level: classification.level,
      label: AUTOMATION_LEVELS[classification.level].label,
      automationPercent: AUTOMATION_LEVELS[classification.level].automationPercent,
      explanation: AUTOMATION_LEVELS[classification.level].explanation,
      reasons: classification.reasons,
      professionalDomains: classification.professionalDomains,
      sensitiveDataLikely: SENSITIVE_TERMS.some((term) => task.toLowerCase().includes(term)),
      matchedBots: routeCapabilities(task.toLowerCase(), classification.professionalDomains),
    };
  });
  const levels = Object.fromEntries(Object.keys(AUTOMATION_LEVELS).map((level) => [level, tasks.filter((task) => task.level === level).length]));
  const professionalDomains = [...new Set(tasks.flatMap((task) => task.professionalDomains))];
  const estimatedHours = tasks.reduce((total, task) => total + ({ A: 0.5, B: 0.75, C: 1.5, D: 2.5, E: 2, F: 0.25 }[task.level]), 0);
  const recommendedPrice = Math.max(75, estimatedHours * 95);
  const statedOrRecommended = request.statedBudget ?? recommendedPrice;
  const humanPercent = tasks.length ? tasks.reduce((total, task) => total + (100 - task.automationPercent), 0) / tasks.length : 100;
  const estimatedCost = estimatedHours * (20 + humanPercent * 0.45) + professionalDomains.length * 125;
  const riskScore = Math.min(100, levels.F * 50 + levels.D * 18 + levels.E * 12 + levels.C * 8 + sensitiveSignals.length * 10);
  const rejected = levels.F > 0;
  return {
    schema: "dreamco.buddy_job_opportunity_analysis.v1",
    analysisId: `job-analysis-${randomUUID()}`,
    fingerprint: createHash("sha256").update(`${request.title}:${request.description}`).digest("hex").slice(0, 24),
    title: request.title,
    source: {
      type: request.sourceType,
      reference: request.sourceReference || "owner_noted_source",
      collectionAuthorized: request.sourceType !== "public_listing" || Boolean(request.sourceReference),
    },
    shadowMode: true,
    status: rejected ? "rejected" : "shadow_analysis_ready",
    tasks,
    summary: {
      tasksClassified: tasks.length,
      levels,
      professionalDomains,
      sensitiveSignals,
      matchedBots: [...new Set(tasks.flatMap((task) => task.matchedBots))],
      estimatedHours: Math.round(estimatedHours * 10) / 10,
      automationPercent: tasks.length ? Math.round(tasks.reduce((total, task) => total + task.automationPercent, 0) / tasks.length) : 0,
      humanOversightPercent: Math.round(humanPercent),
      riskScore,
    },
    economics: {
      currency: request.currency,
      statedBudget: request.statedBudget ?? null,
      suggestedPlanningPrice: roundMoney(recommendedPrice),
      estimatedDeliveryCost: roundMoney(estimatedCost),
      estimatedGrossMargin: roundMoney(statedOrRecommended - estimatedCost),
      noEarningsGuaranteed: true,
    },
    approvalGates: ["client_contact", "application", "identity_or_resume_use", "binding_price", "contract", "production_access", "final_delivery", "invoice", "charge", "money_transfer"],
    externalActionsTaken: false,
  } as const;
}

export function createServiceOpportunity(input: JobOpportunityRequest) {
  const analysis = analyzeJobOpportunity(input);
  const blocked = analysis.status === "rejected";
  return {
    schema: "dreamco.buddy_service_opportunity.v1",
    serviceId: `service-${analysis.fingerprint}`,
    status: blocked ? "rejected" : "shadow_demo_required",
    serviceName: `${analysis.title} Support Service`,
    targetCustomer: "Organizations with a documented need matching the source opportunity",
    customerProblem: analysis.title,
    evidenceOfDemand: [{ source: analysis.source, analysisId: analysis.analysisId }],
    proposedDeliverables: analysis.tasks.filter((task) => task.level !== "F").map((task) => task.task).slice(0, 20),
    requiredBots: analysis.summary.matchedBots,
    requiredProfessionals: analysis.summary.professionalDomains,
    economics: analysis.economics,
    riskScore: analysis.summary.riskScore,
    qualityMetrics: ["acceptance criteria coverage", "sandbox pass rate", "source evidence coverage", "owner approval coverage", "client acceptance evidence"],
    sandbox: { required: true, status: "not_run", networkDefault: "off", syntheticData: true },
    publication: { published: false, ownerApprovalRequired: true },
    sales: { proposalSent: false, priceBound: false, contractSigned: false },
    delivery: { finalDelivered: false, invoiceSent: false, customerCharged: false },
  } as const;
}

const PAYMENT_PROVIDERS = [
  { id: "stripe", methods: ["card", "bank", "wallet"], status: "adapter_configuration_required", verificationRequired: false },
  { id: "paypal", methods: ["wallet", "card"], status: "adapter_configuration_required", verificationRequired: false },
  { id: "square", methods: ["card", "point_of_sale"], status: "adapter_configuration_required", verificationRequired: false },
  { id: "bank_transfer", methods: ["ach", "wire"], status: "bank_and_processor_configuration_required", verificationRequired: true },
  { id: "crypto", methods: ["owner_selected_wallet"], status: "regulated_and_wallet_review_required", verificationRequired: true },
  { id: "piepay", methods: ["owner_specified"], status: "provider_identity_and_api_verification_required", verificationRequired: true },
] as const;

export function createPaymentRoutingPlan(input: z.input<typeof paymentRoutingRequestSchema>) {
  const request = paymentRoutingRequestSchema.parse(input);
  const selected = request.preferredProviders.length
    ? PAYMENT_PROVIDERS.filter((provider) => request.preferredProviders.includes(provider.id))
    : PAYMENT_PROVIDERS.filter((provider) => provider.id !== "piepay");
  return {
    schema: "dreamco.buddy_payment_routing_plan.v1",
    planId: `payment-plan-${randomUUID()}`,
    status: "comparison_ready_exact_approval_required",
    request,
    rankedProviders: selected.map((provider, index) => ({
      rank: index + 1,
      ...provider,
      feesVerified: false,
      settlementVerified: false,
      credentialsConfigured: false,
      sandboxPassed: false,
    })),
    nextSteps: ["verify current provider identity and terms", "verify fees, currencies, regions, and settlement", "configure a backend secret reference", "run provider sandbox fixtures", "prepare one transaction preview", "request exact approval for that transaction"],
    safeguards: ["no raw payment credentials in browser", "no card data stored by Buddy", "no automatic provider enrollment", "no automatic charge", "no automatic payout", "one approval cannot authorize recurring transfers"],
    quoteCreated: false,
    invoiceSent: false,
    paymentProcessed: false,
    fundsMoved: false,
  } as const;
}

export function createProfessionalReviewPacket(input: z.input<typeof professionalReviewRequestSchema>) {
  const request = professionalReviewRequestSchema.parse(input);
  const verified = Boolean(request.responsibleProfessionalId && request.licenseVerificationReference);
  return {
    schema: "dreamco.buddy_professional_review_packet.v1",
    reviewId: `professional-review-${randomUUID()}`,
    status: verified ? "awaiting_professional_review" : "verified_professional_required",
    request,
    controls: ["jurisdiction recorded", "license verification required", "source dates preserved", "draft labeled", "conflict check required", "review notes required", "approved version fingerprint required"],
    responsibleProfessionalVerified: verified,
    reviewCompleted: false,
    approvedVersion: null,
    approvalTimestamp: null,
    finalDeliverableReleased: false,
  } as const;
}

export function createVoiceSandboxPlan(input: z.input<typeof voiceSandboxRequestSchema>) {
  const request = voiceSandboxRequestSchema.parse(input);
  if (request.outbound && !request.recipientConsentReference) {
    throw new Error("Outbound voice simulations require a recipient consent reference before live enablement can be considered.");
  }
  if (request.recordingEnabled && !request.recordingConsentReference) {
    throw new Error("Recording simulations require a recording consent reference.");
  }
  return {
    schema: "dreamco.buddy_voice_operations_sandbox.v1",
    sandboxId: `voice-sandbox-${randomUUID()}`,
    status: "simulation_ready",
    useCase: request.useCase,
    script: request.script,
    testStages: ["AI identity disclosure", "business purpose disclosure", "consent check", "approved script path", "uncertainty escalation", "opt-out handling", "human transfer", "material action log"],
    simulatedCallOnly: true,
    outboundCampaignEnabled: false,
    recordingEnabled: false,
    liveProviderConfigured: false,
    exactApprovalRequiredForEachLiveCampaign: true,
  } as const;
}

const JOB_TITLES = [
  "Sales Representative", "Cold Caller", "Customer Service Representative", "Software Developer", "Web Designer", "Graphic Designer", "Photo Editor", "Video Editor", "Marketing Consultant", "Business Consultant",
  "Attorney", "Paralegal", "Physician", "Nurse", "Pharmacist", "Accountant", "Tax Preparer", "Financial Advisor", "Engineer", "Architect",
  "Real Estate Agent", "Insurance Agent", "Recruiter", "Teacher", "Mechanic", "Construction Worker", "Delivery Driver", "Property Manager", "Executive Assistant", "Data Analyst",
  "Data Entry Specialist", "Data Engineer", "Cybersecurity Analyst", "Cloud Operations Engineer", "DevOps Engineer", "Quality Assurance Engineer", "Project Manager", "Product Manager", "Procurement Coordinator", "Logistics Coordinator",
  "Bookkeeping Assistant", "Legal Operations Assistant", "Medical Administrative Assistant", "Healthcare Documentation Specialist", "Research Analyst", "Technical Writer", "Copywriter", "SEO Specialist", "Social Media Manager", "Content Producer",
  "Mobile Developer", "Backend Developer", "Frontend Developer", "API Integration Specialist", "Database Administrator", "Accessibility Auditor", "Security Review Assistant", "Automation Consultant", "CRM Administrator", "Spreadsheet Automation Specialist",
  "Dashboard Developer", "Document Processing Specialist", "Competitive Intelligence Analyst", "Proposal Writer", "RFP Researcher", "Grant Researcher", "Appointment Setter", "Sales Operations Analyst", "Customer Success Manager", "Renewal Manager",
  "Translation Specialist", "Transcription Specialist", "Ecommerce Manager", "Retail Operations Manager", "Restaurant Administrator", "Manufacturing Planner", "Construction Administrator", "Automotive Service Advisor", "Transportation Dispatcher", "Nonprofit Operations Coordinator",
  "Government Contract Researcher", "Grant Application Assistant", "Human Resources Coordinator", "Training Content Developer", "Course Designer", "Tutor", "Animation Producer", "Presentation Designer", "Brand Manager", "Email Campaign Manager",
  "Invoice Coordinator", "Payment Reconciliation Analyst", "Subscription Operations Manager", "Commission Analyst", "Market Researcher", "Vendor Comparison Analyst", "Workflow Auditor", "Knowledge Base Builder", "Internal Search Designer", "AI Assistant Setup Specialist",
];

function syntheticDescription(title: string): string {
  const text = title.toLowerCase();
  if (/attorney|physician|nurse|pharmacist|tax preparer|financial advisor|engineer|architect|real estate agent|insurance agent/.test(text)) {
    return `Prepare research, organize records, and draft review materials for a ${title}. A verified licensed professional must control regulated conclusions and final delivery.`;
  }
  if (/mechanic|construction worker|delivery driver/.test(text)) {
    return `Coordinate schedules, prepare checklists, estimate supplies, and document work for a ${title}, while a qualified person performs all physical execution and safety decisions.`;
  }
  if (/sales|cold caller|appointment|email campaign|social media/.test(text)) {
    return `Research permitted demand signals, prepare personalized scripts, send message only after exact approval, honor opt-outs, and report outcomes for a ${title}.`;
  }
  if (/software|developer|engineer|api|database|devops|quality assurance|automation|search designer/.test(text)) {
    return `Inspect requirements, build a sandbox proof, write and test code, document acceptance evidence, and deploy production changes only after exact approval for this ${title} project.`;
  }
  return `Analyze requirements, organize source-backed information, prepare draft deliverables, calculate effort and quality checks, and request approval before any external action for a ${title}.`;
}

export function buildSyntheticJobFixtures() {
  return JOB_TITLES.map((title, index) => ({
    ownerUserId: "synthetic-owner",
    title,
    description: syntheticDescription(title),
    responsibilities: [],
    requiredTools: [],
    sourceType: "synthetic_test" as const,
    sourceReference: `fixture:job-${String(index + 1).padStart(3, "0")}`,
    currency: "USD",
  }));
}

export function buildWorkforceRegistry() {
  const workers = buildWorkers();
  const fixtures = buildSyntheticJobFixtures();
  return {
    schema: "dreamco.buddy_autonomous_opportunity_workforce.v1",
    name: "Buddy Autonomous Opportunity and Workforce Engine",
    defaultMode: "shadow",
    loop: ["market_scan", "job_discovery", "task_extraction", "capability_match", "service_creation", "feasibility_test", "profit_simulation", "risk_review", "owner_approval", "client_acquisition", "work_execution", "quality_review", "delivery", "invoice", "payment_tracking", "outcome_learning"],
    summary: {
      workerBots: workers.length,
      systems: [...new Set(workers.map((worker) => worker.system))].length,
      teams: [...new Set(workers.map((worker) => `${worker.system}:${worker.team}`))].length,
      automationLevels: Object.keys(AUTOMATION_LEVELS).length,
      syntheticJobFixtures: fixtures.length,
      liveExternalActionsEnabled: false,
    },
    workers,
    automationLevels: AUTOMATION_LEVELS,
    paymentProviders: PAYMENT_PROVIDERS,
    syntheticJobs: fixtures,
    continuousDiscovery: {
      schedule: "owner_configurable_recurring_task",
      indefinitePotential: true,
      individualRunMaximumHours: 24,
      checkpointRequired: true,
      allowedInShadowMode: ["authorized search", "categorization", "task matching", "profit simulation", "sandbox demo", "draft preparation", "owner reporting"],
      freshApprovalRequired: ["application", "message", "call", "publication", "contract", "production access", "delivery", "invoice", "charge", "transfer"],
    },
    dashboardSections: ["revenue candidates", "sandbox services", "owner approvals", "professional review", "outreach queue", "active projects", "completed work", "invoices", "paid revenue", "expected revenue", "recurring revenue", "cost and profit", "automation and human effort", "failed opportunities", "risk alerts"],
    truthBoundary: "The engine discovers, analyzes, simulates, drafts, and tests. It does not promise earnings or independently contact, contract, deliver regulated work, invoice, charge, or move money.",
  } as const;
}
