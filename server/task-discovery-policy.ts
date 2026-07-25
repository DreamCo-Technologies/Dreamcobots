import { createHash, randomUUID } from "node:crypto";

import { z } from "zod";

export const taskDiscoveryRequestSchema = z.object({
  objective: z.string().trim().min(3).max(4_000),
  context: z.enum(["personal", "work", "business", "learning", "creative", "technical"]).default("personal"),
  knownSteps: z.array(z.string().trim().min(2).max(240)).max(20).default([]),
  constraints: z.array(z.string().trim().min(2).max(240)).max(20).default([]),
  preferredOutcome: z.string().trim().max(1_000).default(""),
}).strict();

export type TaskDiscoveryRequest = z.infer<typeof taskDiscoveryRequestSchema>;

const ROLE_RULES = [
  {
    id: "emergency_information_assistant",
    terms: ["emergency", "suicide", "overdose", "fire", "active threat"],
    boundary: "Do not rely on automation. Contact local emergency services or an appropriate crisis service now.",
  },
  {
    id: "financial_education_assistant",
    terms: ["invest", "investment", "stock", "retirement", "financial advisor", "portfolio", "loan", "credit"],
    boundary: "Education, calculators, source checks, and question preparation only. Personalized investment advice and regulated transactions require a properly licensed professional.",
  },
  {
    id: "health_information_assistant",
    terms: ["medical", "diagnose", "symptom", "medicine", "health", "therapy"],
    boundary: "General information, appointment preparation, and record organization only. Buddy does not diagnose, prescribe, or replace a qualified clinician.",
  },
  {
    id: "legal_information_assistant",
    terms: ["legal advice", "lawsuit", "court", "contract", "patent", "trademark", "immigration"],
    boundary: "General legal information, document organization, and question preparation only. Legal conclusions and representation require a qualified professional.",
  },
] as const;

function matchingRole(objective: string) {
  const normalized = objective.toLowerCase();
  return ROLE_RULES.find((rule) => rule.terms.some((term) => normalized.includes(term))) ?? {
    id: "general_task_partner",
    boundary: "Buddy can teach, plan, draft, test, and coordinate. Live account changes, purchases, messages, filings, and publications require a configured adapter and exact approval.",
  };
}

export function createTaskDiscoveryPlan(input: TaskDiscoveryRequest) {
  const request = taskDiscoveryRequestSchema.parse(input);
  const words = request.objective.split(/\s+/).filter(Boolean);
  const uncertain = words.length < 6 || /\b(not sure|do not know|don't know|figure out|anything|somehow)\b/i.test(request.objective);
  const role = matchingRole(request.objective);
  const fingerprint = createHash("sha256")
    .update(`${request.context}:${request.objective}:${request.preferredOutcome}`)
    .digest("hex")
    .slice(0, 20);
  const firstQuestion = request.preferredOutcome
    ? "What is the most important constraint: time, cost, quality, privacy, or ease of use?"
    : "What would a successful result let you do, even if you do not know the steps yet?";
  return {
    schema: "dreamco.buddy_task_discovery_plan.v1",
    planId: `discovery-${randomUUID()}`,
    fingerprint,
    status: uncertain ? "guided_discovery_ready" : "task_map_ready",
    objective: request.objective,
    context: request.context,
    clarity: uncertain ? "needs_one_question" : "sufficient_to_start_read_only",
    firstQuestion,
    assumedOutcome: request.preferredOutcome || "Turn the request into a verifiable result with the least risky first step.",
    knownSteps: request.knownSteps,
    constraints: request.constraints,
    taskMap: [
      { phase: "understand", action: "Restate the outcome, users, constraints, and definition of done." },
      { phase: "discover", action: "Find the missing skills, official sources, specialist bots, tools, permissions, and costs." },
      { phase: "practice", action: "Create a synthetic-data or local sandbox exercise that teaches each unfamiliar step." },
      { phase: "build", action: "Produce the smallest reviewable result and keep a reversible checkpoint." },
      { phase: "verify", action: "Run acceptance, safety, privacy, accessibility, and regression checks." },
      { phase: "act", action: "Preview live effects and request exact approval before each outside action." },
    ],
    role: {
      id: role.id,
      boundary: role.boundary,
      buddyIsLicensedProfessional: false,
      buddyIsHuman: false,
    },
    userCanSay: ["explain that more simply", "show me an example", "practice it with me", "do the safe parts", "stop and undo"],
    externalActionTaken: false,
  } as const;
}
