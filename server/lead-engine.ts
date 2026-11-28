import { z } from "zod";

/**
 * Five-stage Lead Engine policy layer.
 *
 * This module is intentionally a planning/qualification engine: it does not
 * scrape sources, send messages, write to a CRM, book meetings, or collect
 * payments. External actions remain behind the existing governed-leads
 * approval and adapter boundaries.
 */

export const LEAD_ENGINE_STAGES = ["attract", "capture", "qualify", "nurture", "convert"] as const;
export type LeadEngineStage = typeof LEAD_ENGINE_STAGES[number];

const safeLabel = z.string().trim().min(1).max(160).refine(
  (value) => !/(?:github_pat_|ghs_|sk_(?:live|test)_|BEGIN .*PRIVATE KEY)/i.test(value),
  "Lead Engine fields must not contain credentials",
);

export const leadEngineRecordSchema = z.object({
  leadId: z.string().regex(/^lead-[A-Za-z0-9-]{4,80}$/),
  ownerUserId: z.string().trim().min(2).max(80),
  organizationName: safeLabel,
  sourceType: z.enum(["owner_supplied", "inbound_request", "public_business_directory", "authorized_partner_feed", "content_download", "event_referral"]),
  sourceReference: z.string().trim().min(3).max(240),
  sourceTermsConfirmed: z.literal(true),
  stage: z.enum(LEAD_ENGINE_STAGES).default("capture"),
  consentBasis: z.enum(["explicit_opt_in", "inbound_request", "existing_relationship", "none"]),
  consentEvidenceRef: z.string().trim().min(3).max(240).optional(),
  consentChannels: z.array(z.enum(["email", "sms", "voice_call", "social_dm"])).max(4).default([]),
  fitScore: z.number().finite().min(0).max(100).default(0),
  intentScore: z.number().finite().min(0).max(100).default(0),
  budgetFitScore: z.number().finite().min(0).max(100).default(0),
  timelineScore: z.number().finite().min(0).max(100).default(0),
  engagementScore: z.number().finite().min(0).max(100).default(0),
  useCase: safeLabel.optional(),
  humanReviewEvidenceRef: z.string().trim().min(3).max(240).optional(),
  buyingTimeline: z.enum(["now", "within_30_days", "this_quarter", "next_quarter", "researching", "unknown"]).default("unknown"),
  budgetConfirmed: z.boolean().default(false),
  lastEngagedAt: z.string().datetime({ offset: true }).optional(),
  suppressionStatus: z.enum(["active", "opted_out", "replied", "bounced", "complaint", "owner_blocked"]).default("active"),
  sensitiveTargeting: z.literal(false),
  includesMinor: z.literal(false),
}).strict().superRefine((lead, context) => {
  if (new Set(lead.consentChannels).size !== lead.consentChannels.length) {
    context.addIssue({ code: z.ZodIssueCode.custom, path: ["consentChannels"], message: "Consent channels must be unique" });
  }
  if (lead.consentBasis === "none" && lead.consentChannels.length > 0) {
    context.addIssue({ code: z.ZodIssueCode.custom, path: ["consentChannels"], message: "A lead without consent cannot have outreach channels" });
  }
  if (lead.consentBasis !== "none" && !lead.consentEvidenceRef) {
    context.addIssue({ code: z.ZodIssueCode.custom, path: ["consentEvidenceRef"], message: "Permission requires a consent evidence reference" });
  }
  if (lead.stage === "convert" && !lead.humanReviewEvidenceRef) {
    context.addIssue({ code: z.ZodIssueCode.custom, path: ["humanReviewEvidenceRef"], message: "Conversion requires documented human review evidence" });
  }
});

export type LeadEngineRecord = z.infer<typeof leadEngineRecordSchema>;

export type LeadQualification = {
  score: number;
  tier: "hot" | "warm" | "cold";
  breakdown: {
    buyingIntent: number;
    budgetFit: number;
    timeline: number;
    businessFit: number;
    engagement: number;
  };
  reasons: string[];
  nextStep: "human_sales_handoff" | "targeted_nurture_plan" | "educational_content" | "research_only";
};

const WEIGHTS = {
  buyingIntent: 30,
  budgetFit: 25,
  timeline: 20,
  businessFit: 15,
  engagement: 10,
} as const;

function weighted(value: number, maximum: number) {
  return Math.round((value / 100) * maximum);
}

/** Explainable 100-point qualification score; never uses protected traits. */
export function qualifyLead(input: LeadEngineRecord): LeadQualification {
  const lead = leadEngineRecordSchema.parse(input);
  const breakdown = {
    buyingIntent: weighted(lead.intentScore, WEIGHTS.buyingIntent),
    budgetFit: weighted(lead.budgetFitScore, WEIGHTS.budgetFit),
    timeline: weighted(lead.timelineScore, WEIGHTS.timeline),
    businessFit: weighted(lead.fitScore, WEIGHTS.businessFit),
    engagement: weighted(lead.engagementScore, WEIGHTS.engagement),
  };
  const score = Object.values(breakdown).reduce((total, points) => total + points, 0);
  const suppressed = lead.suppressionStatus !== "active";
  const permissioned = lead.consentBasis !== "none" && Boolean(lead.consentEvidenceRef);
  const tier = score >= 80 ? "hot" : score >= 50 ? "warm" : "cold";
  const reasons = [
    `buying_intent:${breakdown.buyingIntent}/30`,
    `budget_fit:${breakdown.budgetFit}/25`,
    `timeline:${breakdown.timeline}/20`,
    `business_fit:${breakdown.businessFit}/15`,
    `engagement:${breakdown.engagement}/10`,
  ];
  if (!lead.budgetConfirmed) reasons.push("budget_not_confirmed");
  if (!permissioned) reasons.push("outreach_permission_not_verified");
  if (suppressed) reasons.push(`contact_suppressed:${lead.suppressionStatus}`);
  const nextStep = suppressed || !permissioned
    ? "research_only"
    : tier === "hot"
      ? "human_sales_handoff"
      : tier === "warm"
        ? "targeted_nurture_plan"
        : "educational_content";
  return { score, tier, breakdown, reasons, nextStep };
}

export type LeadStagePlan = {
  schema: "dreamco.lead_engine.stage_plan.v1";
  leadId: string;
  currentStage: LeadEngineStage;
  recommendedStage: LeadEngineStage;
  stageActions: Array<{ stage: LeadEngineStage; status: "complete" | "ready" | "blocked"; reason: string }>;
  qualification: LeadQualification;
  externalActionTaken: false;
};

const STAGE_ORDER: LeadEngineStage[] = ["attract", "capture", "qualify", "nurture", "convert"];

/** Creates a deterministic, non-executing stage plan for Buddy and CRM adapters. */
export function buildLeadStagePlan(input: LeadEngineRecord): LeadStagePlan {
  const lead = leadEngineRecordSchema.parse(input);
  const qualification = qualifyLead(lead);
  const currentIndex = STAGE_ORDER.indexOf(lead.stage);
  const suppressed = lead.suppressionStatus !== "active";
  const permissioned = lead.consentBasis !== "none" && Boolean(lead.consentEvidenceRef);
  const canConvert = permissioned &&
    !suppressed &&
    qualification.tier === "hot" &&
    lead.budgetConfirmed &&
    Boolean(lead.useCase) &&
    Boolean(lead.humanReviewEvidenceRef);

  const recommendedStage: LeadEngineStage = suppressed
    ? lead.stage
    : currentIndex === 0
      ? "capture"
      : currentIndex === 1
        ? "qualify"
        : currentIndex === 2
          ? permissioned && qualification.tier !== "cold" ? "nurture" : "qualify"
          : currentIndex === 3
            ? canConvert ? "convert" : "nurture"
            : "convert";

  const actions = STAGE_ORDER.map((stage, index) => {
    if (index < currentIndex) {
      return { stage, status: "complete" as const, reason: "stage_previously_completed" };
    }
    if (stage === "nurture" && (!permissioned || suppressed)) {
      return { stage, status: "blocked" as const, reason: suppressed ? "contact_suppressed" : "documented_permission_required" };
    }
    if (stage === "convert" && !canConvert) {
      return { stage, status: "blocked" as const, reason: "hot_score_budget_use_case_permission_and_human_review_required" };
    }
    if (stage === lead.stage) {
      return { stage, status: "ready" as const, reason: "current_stage_ready_for_owner_workflow" };
    }
    if (stage === recommendedStage) {
      return { stage, status: "ready" as const, reason: "next_eligible_stage_recommended" };
    }
    return { stage, status: "blocked" as const, reason: "prior_stage_completion_required" };
  });

  return {
    schema: "dreamco.lead_engine.stage_plan.v1",
    leadId: lead.leadId,
    currentStage: lead.stage,
    recommendedStage,
    stageActions: actions,
    qualification,
    externalActionTaken: false,
  };
}

/** Enforces one-stage-at-a-time progression and explicit gates for nurture/convert. */
export function assertLeadStageTransition(
  existing: LeadEngineRecord | undefined,
  nextInput: LeadEngineRecord,
): LeadEngineRecord {
  const next = leadEngineRecordSchema.parse(nextInput);
  const nextIndex = STAGE_ORDER.indexOf(next.stage);
  if (!existing) {
    if (nextIndex > 1) throw new Error("lead_engine_initial_stage_must_be_attract_or_capture");
    return next;
  }
  const current = leadEngineRecordSchema.parse(existing);
  const currentIndex = STAGE_ORDER.indexOf(current.stage);
  if (nextIndex < currentIndex) throw new Error("lead_engine_stage_regression_forbidden");
  if (nextIndex > currentIndex + 1) throw new Error("lead_engine_stage_skip_forbidden");
  if (nextIndex === currentIndex + 1 && next.stage === "nurture") {
    if (next.consentBasis === "none" || !next.consentEvidenceRef || next.suppressionStatus !== "active") {
      throw new Error("lead_engine_nurture_requires_current_permission_and_active_contact");
    }
  }
  if (nextIndex === currentIndex + 1 && next.stage === "convert") {
    const qualification = qualifyLead(next);
    if (
      qualification.tier !== "hot" ||
      !next.budgetConfirmed ||
      !next.useCase ||
      !next.humanReviewEvidenceRef ||
      next.consentBasis === "none" ||
      !next.consentEvidenceRef ||
      next.suppressionStatus !== "active"
    ) {
      throw new Error("lead_engine_conversion_requires_hot_lead_budget_use_case_permission_and_human_review");
    }
  }
  return next;
}

export function leadEngineReadiness() {
  return {
    schema: "dreamco.lead_engine.readiness.v1",
    stages: LEAD_ENGINE_STAGES,
    scoringWeights: WEIGHTS,
    thresholds: { hot: 80, warm: 50, cold: 0 },
    integrations: {
      governedOutreach: "existing_governed_leads_policy",
      crmPersistence: "oauth_protected_owner_scoped_postgres_api_requires_migration_and_staging_rls_verification",
      emailDelivery: "requires_configured_approved_adapter",
      calendarBooking: "requires_owner_authorized_calendar_adapter",
      payments: "requires_separate_payment_authorization",
    },
    externalActionsEnabled: false,
    credentialStorage: "secret_references_only",
  } as const;
}
