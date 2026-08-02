export type BuddyIntent = "Build" | "Fix" | "Create" | "Plan" | "Discover";

export type SuccessQuestion = {
  id: string;
  section: string;
  label: string;
  help: string;
  type: "text" | "textarea" | "select" | "multiselect" | "number";
  options?: string[];
  required?: boolean;
};

export const SUCCESS_QUESTIONNAIRE: SuccessQuestion[] = [
  { id: "primary_outcome", section: "Goals", label: "What result matters most right now?", help: "Name a concrete outcome Buddy can help measure.", type: "textarea", required: true },
  { id: "success_measure", section: "Goals", label: "How will you know it worked?", help: "Examples: a working prototype, five qualified leads, or four hours saved.", type: "textarea", required: true },
  { id: "income_target", section: "Goals", label: "What income target would you like to work toward?", help: "This is a planning target, not a guarantee.", type: "number" },
  { id: "target_period", section: "Goals", label: "Target period", help: "Choose the period Buddy should use for estimates.", type: "select", options: ["week", "month", "quarter", "year"] },
  { id: "timeline", section: "Goals", label: "When would you like the first useful result?", help: "Buddy will use this to keep the first build small enough.", type: "select", options: ["today", "this week", "this month", "this quarter", "exploring"] },
  { id: "hours_available", section: "Capacity", label: "Hours available each week", help: "Use a realistic number so plans stay practical.", type: "number" },
  { id: "effort_preference", section: "Capacity", label: "Preferred effort level", help: "Automation still requires review and approval for important actions.", type: "select", options: ["lowest practical effort", "balanced", "hands-on learning"] },
  { id: "budget_range", section: "Capacity", label: "Optional monthly tool budget", help: "Buddy defaults to free and local resources and never spends from this answer.", type: "select", options: ["free only", "under 25", "25 to 100", "100 to 500", "case by case"] },
  { id: "skills", section: "Strengths", label: "Skills you already have", help: "List practical, creative, technical, or people skills.", type: "textarea" },
  { id: "experience", section: "Strengths", label: "Experience Buddy should build on", help: "Include jobs, hobbies, industries, and completed projects.", type: "textarea" },
  { id: "interests", section: "Strengths", label: "Topics you enjoy", help: "Sustainable ideas usually match real interests.", type: "textarea" },
  { id: "learning_style", section: "Strengths", label: "How should Buddy teach?", help: "Choose the style that makes unfamiliar work feel manageable.", type: "select", options: ["show me", "step by step", "explain why", "let me practice", "mostly do the setup"] },
  { id: "business_stage", section: "Business", label: "Current business stage", help: "Buddy will not assume a company already exists.", type: "select", options: ["idea", "testing demand", "selling", "growing", "established", "personal use"] },
  { id: "offer", section: "Business", label: "What could you offer today?", help: "A product, service, skill, asset, or result is enough.", type: "textarea" },
  { id: "customers", section: "Business", label: "Who could benefit?", help: "Describe the people or organizations and the problem they have.", type: "textarea" },
  { id: "industries", section: "Business", label: "Preferred industries", help: "Choose areas Buddy should prioritize.", type: "textarea" },
  { id: "excluded_work", section: "Business", label: "Work Buddy should avoid", help: "List industries, tactics, or customers you do not want.", type: "textarea" },
  { id: "pricing_comfort", section: "Business", label: "Pricing comfort", help: "Buddy can prepare comparisons; you approve final prices.", type: "select", options: ["need help", "fixed price", "hourly", "subscription", "performance based", "multiple options"] },
  { id: "owned_assets", section: "Assets", label: "Useful assets you own or control", help: "Examples: a domain, equipment, code, content, audience, or licensed media.", type: "textarea" },
  { id: "available_tools", section: "Assets", label: "Apps and tools already available", help: "Do not enter passwords, tokens, secret keys, or account numbers.", type: "textarea" },
  { id: "data_rights", section: "Assets", label: "Data you own and may use", help: "Describe categories only. Do not paste private records here.", type: "textarea" },
  { id: "distribution", section: "Assets", label: "Ways you can reach people", help: "Examples: website, email list, local network, marketplace profile, or none yet.", type: "textarea" },
  { id: "research_permission", section: "Permissions", label: "Web research default", help: "This controls planning only; provider terms still apply.", type: "select", options: ["ask every time", "public read-only research", "official sources first"] },
  { id: "outreach_permission", section: "Permissions", label: "Outreach default", help: "Buddy never contacts someone solely because this profile exists.", type: "select", options: ["draft only", "ask before every message", "no outreach"] },
  { id: "transaction_permission", section: "Permissions", label: "Money action default", help: "Exact approval, amount, destination, and final review remain required.", type: "select", options: ["plan only", "prepare for approval", "never prepare transactions"] },
  { id: "publishing_permission", section: "Permissions", label: "Publishing default", help: "Buddy prepares drafts unless you approve a specific publication.", type: "select", options: ["draft only", "ask before every publish", "no publishing"] },
  { id: "approval_channel", section: "Permissions", label: "Preferred approval channel", help: "A deployed notification adapter is required for email, text, or calls.", type: "select", options: ["in app", "email", "text", "voice call"] },
  { id: "communication_style", section: "Buddy", label: "Conversation style", help: "Buddy can adapt while keeping business communication professional.", type: "select", options: ["friendly", "concise", "coach", "detailed", "professional"] },
  { id: "accessibility", section: "Buddy", label: "Accessibility preferences", help: "Describe reading, hearing, vision, motor, language, or pace needs.", type: "textarea" },
  { id: "retention", section: "Buddy", label: "Profile retention", help: "The public site stores this profile only in this browser.", type: "select", options: ["session only", "30 days", "until I delete it"] },
];

export const ONTOLOGY_DIMENSIONS = [
  "evidence",
  "safety",
  "user_value",
  "revenue_potential",
  "time_saved",
  "cost_control",
] as const;

export type OntologyDimension = typeof ONTOLOGY_DIMENSIONS[number];

export const ONTOLOGY_PRESETS: Record<string, Record<OntologyDimension, number>> = {
  balanced: { evidence: 20, safety: 20, user_value: 20, revenue_potential: 15, time_saved: 15, cost_control: 10 },
  growth: { evidence: 15, safety: 15, user_value: 20, revenue_potential: 30, time_saved: 10, cost_control: 10 },
  low_effort: { evidence: 15, safety: 20, user_value: 15, revenue_potential: 15, time_saved: 25, cost_control: 10 },
  evidence_first: { evidence: 30, safety: 25, user_value: 15, revenue_potential: 10, time_saved: 10, cost_control: 10 },
};

const INTENT_PATTERNS: Array<{ intent: BuddyIntent; patterns: RegExp[] }> = [
  { intent: "Fix", patterns: [/\bfix\b/i, /\bdebug\b/i, /\brepair\b/i, /\bfail(?:ed|ing|ure)?\b/i, /\berror\b/i, /\bbroken\b/i] },
  { intent: "Create", patterns: [/\bcreate\b/i, /\bmake (?:a|an|my)\b/i, /\bmovie\b/i, /\bmusic\b/i, /\bimage\b/i, /\bvideo\b/i, /\bstory\b/i, /\bdesign\b/i] },
  { intent: "Discover", patterns: [/\bfind\b/i, /\bsearch\b/i, /\bresearch\b/i, /\bdiscover\b/i, /\bcompare\b/i, /\bwhat (?:can|should|is|are)\b/i, /\bhelp me figure\b/i] },
  { intent: "Plan", patterns: [/\bplan\b/i, /\bstrategy\b/i, /\broadmap\b/i, /\bscope\b/i, /\bestimate\b/i, /\bprepare\b/i] },
  { intent: "Build", patterns: [/\bbuild\b/i, /\bcode\b/i, /\bimplement\b/i, /\bprototype\b/i, /\bdeploy\b/i, /\bconnect\b/i, /\bset up\b/i] },
];

export function classifyBuddyIntent(objective: string): BuddyIntent {
  const scores = INTENT_PATTERNS.map(({ intent, patterns }) => ({
    intent,
    score: patterns.reduce((total, pattern) => total + (pattern.test(objective) ? 1 : 0), 0),
  })).sort((a, b) => b.score - a.score);
  return scores[0]?.score ? scores[0].intent : "Discover";
}

export function summarizeSuccessAnswers(answers: Record<string, string | string[] | number>) {
  const usefulIds = ["primary_outcome", "success_measure", "timeline", "hours_available", "skills", "business_stage", "offer", "customers", "industries", "owned_assets", "effort_preference", "budget_range"];
  return usefulIds.flatMap((id) => {
    const value = answers[id];
    if (value === undefined || value === "" || (Array.isArray(value) && !value.length)) return [];
    const question = SUCCESS_QUESTIONNAIRE.find((item) => item.id === id);
    return [`${question?.label || id}: ${Array.isArray(value) ? value.join(", ") : value}`];
  }).join(" | ").slice(0, 1_500);
}
