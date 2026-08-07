import { z } from "zod";

export const ACTION_RISK_LEVELS = ["low", "moderate", "high", "critical"] as const;
export const ACTION_CONSEQUENCE_TYPES = [
  "account_warning",
  "temporary_restriction",
  "rate_limit",
  "content_removal",
  "monetization_loss",
  "account_suspension",
  "account_ban",
  "payment_hold",
  "financial_loss",
  "privacy_exposure",
  "data_loss",
  "legal_or_contractual_risk",
  "reputation_risk",
  "service_disruption",
] as const;

export const riskEvidenceSchema = z.object({
  sourceType: z.enum(["official_terms", "official_policy", "official_api_docs", "platform_notice", "internal_test", "user_report", "unknown"]),
  sourceReference: z.string().trim().max(1024).nullable().default(null),
  checkedAt: z.string().datetime(),
  notes: z.string().trim().max(2000).default(""),
}).strict();

export const actionRiskAssessmentSchema = z.object({
  schema: z.literal("dreamco.action_risk_assessment.v1"),
  actionId: z.string().trim().min(3).max(160),
  actionLabel: z.string().trim().min(2).max(200),
  platformOrSystem: z.string().trim().min(2).max(200),
  autonomous: z.boolean(),
  riskLevel: z.enum(ACTION_RISK_LEVELS),
  score: z.number().int().min(0).max(100),
  confidence: z.number().min(0).max(1),
  possibleConsequences: z.array(z.object({
    type: z.enum(ACTION_CONSEQUENCE_TYPES),
    likelihood: z.enum(["unlikely", "possible", "likely", "unknown"]),
    explanation: z.string().trim().min(5).max(1000),
  }).strict()).max(30).default([]),
  platformPolicyUnknown: z.boolean().default(false),
  saferAlternative: z.string().trim().max(1500).nullable().default(null),
  freshApprovalRequired: z.boolean().default(true),
  canRunUnattended: z.boolean().default(false),
  evidence: z.array(riskEvidenceSchema).max(50).default([]),
  userFacingSummary: z.string().trim().min(5).max(2000),
}).strict();

export const guardrailRuleSchema = z.object({
  id: z.string().trim().regex(/^[A-Za-z0-9_.:-]{3,160}$/),
  name: z.string().trim().min(2).max(200),
  explanation: z.string().trim().min(10).max(2000),
  whyItExists: z.string().trim().min(10).max(2000),
  scope: z.enum(["platform", "personal", "enterprise"]),
  mutableByUser: z.boolean(),
  enabled: z.boolean().default(true),
  effect: z.enum(["inform", "require_approval", "limit", "block", "require_human_review", "require_managed_device"]),
  appliesTo: z.array(z.string().trim().min(2).max(160)).max(200).default([]),
  userMayMakeStricter: z.boolean().default(true),
}).strict();

export const guardrailCenterSchema = z.object({
  schema: z.literal("dreamco.guardrail_center.v1"),
  ownerOrTenantId: z.string().trim().min(3).max(160),
  platformGuardrails: z.array(guardrailRuleSchema).default([]),
  personalGuardrails: z.array(guardrailRuleSchema).default([]),
  enterpriseGuardrails: z.array(guardrailRuleSchema).default([]),
  showEveryActiveGuardrailInUi: z.boolean().default(true),
  showReasonForEveryBlockOrApproval: z.boolean().default(true),
  showActionHistory: z.boolean().default(true),
}).strict();

export function mayUserChangeGuardrail(rule: z.infer<typeof guardrailRuleSchema>, requestedEnabled: boolean) {
  if (rule.scope === "platform" && !rule.mutableByUser && !requestedEnabled) {
    return { allowed: false, reason: "non_negotiable_platform_guardrail" } as const;
  }
  if (!rule.mutableByUser && requestedEnabled !== rule.enabled) {
    return { allowed: false, reason: "guardrail_locked" } as const;
  }
  return { allowed: true, reason: "user_configurable" } as const;
}

export function radarBadge(assessment: z.infer<typeof actionRiskAssessmentSchema>) {
  return {
    label: assessment.riskLevel.toUpperCase(),
    score: assessment.score,
    autonomous: assessment.autonomous,
    approvalRequired: assessment.freshApprovalRequired,
    unattendedAllowed: assessment.canRunUnattended,
  } as const;
}
