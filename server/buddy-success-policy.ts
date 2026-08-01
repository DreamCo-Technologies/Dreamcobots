import { createHash } from "node:crypto";
import { z } from "zod";

import {
  classifyBuddyIntent,
  ONTOLOGY_DIMENSIONS,
  ONTOLOGY_PRESETS,
  SUCCESS_QUESTIONNAIRE,
  summarizeSuccessAnswers,
} from "@shared/buddy-success-contract";

const answerValueSchema = z.union([
  z.string().trim().max(1_000),
  z.number().finite().min(0).max(100_000_000),
  z.array(z.string().trim().min(1).max(160)).max(20),
]);

export const successProfileRequestSchema = z.object({
  profileId: z.string().trim().min(3).max(120),
  answers: z.record(answerValueSchema),
  shareWithBots: z.boolean(),
  ownerConfirmsNoSecrets: z.literal(true),
}).strict();

export const growthExperimentRequestSchema = z.object({
  profileId: z.string().trim().min(3).max(120),
  title: z.string().trim().min(3).max(160),
  problem: z.string().trim().min(10).max(1_000),
  customer: z.string().trim().min(2).max(400),
  offer: z.string().trim().min(3).max(600),
  validationMethod: z.string().trim().min(3).max(600),
  estimatedEffortHours: z.number().finite().min(0).max(10_000),
  maximumBudgetUsd: z.number().finite().min(0).max(1_000_000),
  allowExternalResearch: z.boolean().default(false),
  approveOutreach: z.boolean().default(false),
  approveSpend: z.boolean().default(false),
}).strict();

export const ontologyPlanRequestSchema = z.object({
  profileId: z.string().trim().min(3).max(120),
  mode: z.enum(["balanced", "growth", "low_effort", "evidence_first", "custom"]),
  weights: z.record(z.number().int().min(0).max(100)),
}).strict();

export const intentRequestSchema = z.object({
  objective: z.string().trim().min(3).max(4_000),
}).strict();

function stableId(prefix: string, value: string) {
  return `${prefix}-${createHash("sha256").update(value).digest("hex").slice(0, 16)}`;
}

function rejectSecretLikeAnswers(answers: Record<string, unknown>) {
  const forbidden = /(password|passcode|secret|token|api.?key|social.?security|ssn|account.?number|private.?key)/i;
  for (const [key, value] of Object.entries(answers)) {
    if (forbidden.test(key) || forbidden.test(String(value))) {
      throw new Error("Success profiles must not contain credentials, government identifiers, account numbers, or secret keys.");
    }
  }
}

export function createSuccessProfilePlan(input: z.input<typeof successProfileRequestSchema>) {
  const request = successProfileRequestSchema.parse(input);
  const allowed = new Set(SUCCESS_QUESTIONNAIRE.map((question) => question.id));
  const unknown = Object.keys(request.answers).filter((key) => !allowed.has(key));
  if (unknown.length) throw new Error(`Unknown success profile answers: ${unknown.join(", ")}`);
  rejectSecretLikeAnswers(request.answers);
  const missingRequired = SUCCESS_QUESTIONNAIRE.filter((question) => question.required && !request.answers[question.id]).map((question) => question.id);
  return {
    schema: "dreamco.buddy_success_profile_plan.v1",
    profilePlanId: stableId("success", `${request.profileId}:${JSON.stringify(request.answers)}`),
    status: missingRequired.length ? "profile_incomplete" : "profile_ready",
    shareWithBots: request.shareWithBots,
    missingRequired,
    botContext: request.shareWithBots ? summarizeSuccessAnswers(request.answers) : "",
    storedByThisRoute: false,
    externalActionTaken: false,
    boundaries: {
      guaranteedIncomeClaims: false,
      secretsAccepted: false,
      sensitiveEligibilityDataRequested: false,
      liveMoneyMovement: false,
      liveOutreach: false,
    },
  } as const;
}

export function createGrowthExperimentPlan(input: z.input<typeof growthExperimentRequestSchema>) {
  const request = growthExperimentRequestSchema.parse(input);
  const status = request.approveSpend && request.maximumBudgetUsd === 0
    ? "budget_amount_required"
    : request.approveOutreach || request.approveSpend
      ? "exact_action_approval_required"
      : request.allowExternalResearch
        ? "research_adapter_required"
        : "local_validation_plan_ready";
  return {
    schema: "dreamco.buddy_growth_experiment_plan.v1",
    experimentId: stableId("growth", `${request.profileId}:${request.title}:${request.problem}`),
    status,
    hypothesis: `${request.customer} may pay for ${request.offer} because ${request.problem}`,
    steps: [
      "Record the customer problem and current alternative with source evidence.",
      `Run this validation method with synthetic or owner-supplied data: ${request.validationMethod}`,
      "Measure interest, effort, cost, delivery quality, and user-confirmed revenue separately.",
      "Keep failed results visible, revise one assumption, and stop when the budget or risk limit is reached.",
    ],
    maximumBudgetUsd: request.maximumBudgetUsd,
    liveResearchPerformed: false,
    outreachSent: false,
    moneyMoved: false,
    incomeGuaranteed: false,
  } as const;
}

export function createOntologyPlan(input: z.input<typeof ontologyPlanRequestSchema>) {
  const request = ontologyPlanRequestSchema.parse(input);
  const weights = request.mode === "custom" ? request.weights : ONTOLOGY_PRESETS[request.mode];
  const missing = ONTOLOGY_DIMENSIONS.filter((dimension) => typeof weights[dimension] !== "number");
  if (missing.length) throw new Error(`Missing ontology weights: ${missing.join(", ")}`);
  const total = ONTOLOGY_DIMENSIONS.reduce((sum, dimension) => sum + Number(weights[dimension]), 0);
  if (total !== 100) throw new Error("Ontology weights must total 100.");
  if (Number(weights.evidence) < 10 || Number(weights.safety) < 10) {
    throw new Error("Evidence and safety weights each have a hard minimum of 10.");
  }
  return {
    schema: "dreamco.buddy_weighted_ontology_plan.v1",
    mode: request.mode,
    weights,
    total,
    graphEngine: "weighted_relationship_ranking",
    developerRegionUsedAsQualitySignal: false,
    liveDecisionExecuted: false,
  } as const;
}

export function createIntentResult(input: z.input<typeof intentRequestSchema>) {
  const request = intentRequestSchema.parse(input);
  return {
    schema: "dreamco.buddy_intent_result.v1",
    intent: classifyBuddyIntent(request.objective),
    inferredWithoutModeButton: true,
    ownerCanOverride: true,
  } as const;
}
