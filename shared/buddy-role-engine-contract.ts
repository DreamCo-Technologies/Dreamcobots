import { z } from "zod";

export const BUDDY_ROLE_TYPES = [
  "coach","motivational_speaker","broker","agent","consultant","manager","executive_assistant","recruiter","teacher","sales_rep","sales_manager","content_creator","business_builder","inventor","software_engineer","researcher","analyst","project_manager","customer_success","marketer","operations_manager","financial_coach","career_coach","creative_director","producer","editor","trainer","concierge","negotiator","advisor","planner","organizer","tutor","mentor","accountability_partner","support_specialist","procurement_specialist","scheduler","bookkeeper","compliance_assistant","other"
] as const;

export const buddyRoleTaskSchema = z.object({
  taskId: z.string().trim().min(2).max(160),
  label: z.string().trim().min(2).max(200),
  userGoal: z.string().trim().min(5).max(1000),
  requiredCapabilities: z.array(z.string().trim().min(2).max(160)).min(1).max(100),
  requiredConnectors: z.array(z.string().trim().min(2).max(160)).max(100).default([]),
  benchmarkSuiteIds: z.array(z.string().trim().min(2).max(160)).max(100).default([]),
  freshApprovalRequired: z.boolean().default(false),
}).strict();

export const buddyRoleProfileSchema = z.object({
  schema: z.literal("dreamco.buddy_role_profile.v1"),
  roleId: z.string().trim().min(2).max(160),
  roleType: z.enum(BUDDY_ROLE_TYPES),
  displayName: z.string().trim().min(2).max(160),
  purpose: z.string().trim().min(10).max(2000),
  tasks: z.array(buddyRoleTaskSchema).min(1).max(500),
  personalityProfileId: z.string().trim().max(160).nullable().default(null),
  defaultAutonomy: z.enum(["plan_only","read_only","sandbox_execute","approved_external_action","scheduled_read_only"]).default("plan_only"),
  successMetrics: z.array(z.string().trim().min(2).max(200)).min(1).max(100),
}).strict();

export const observedTaskPatternSchema = z.object({
  patternId: z.string().trim().min(2).max(160),
  normalizedIntent: z.string().trim().min(2).max(240),
  examples: z.array(z.string().trim().min(2).max(500)).max(50).default([]),
  frequency30d: z.number().int().min(0),
  completionRate: z.number().min(0).max(1).nullable().default(null),
  averageUserRating: z.number().min(0).max(5).nullable().default(null),
  currentRoleIds: z.array(z.string().trim().min(2).max(160)).max(50).default([]),
}).strict();

export const buddyRoleEvolutionSchema = z.object({
  schema: z.literal("dreamco.buddy_role_evolution.v1"),
  ownerOrTenantId: z.string().trim().min(3).max(160),
  observedPatterns: z.array(observedTaskPatternSchema).max(5000).default([]),
  suggestions: z.array(z.object({
    suggestionId: z.string().trim().min(3).max(160),
    proposedRoleType: z.enum(BUDDY_ROLE_TYPES),
    proposedName: z.string().trim().min(2).max(160),
    reason: z.string().trim().min(10).max(1500),
    supportingPatternIds: z.array(z.string().trim().min(2).max(160)).min(1).max(100),
    confidence: z.number().min(0).max(1),
    userApprovalRequired: z.literal(true),
  }).strict()).max(500).default([]),
  controls: z.object({
    learnFromTaskFrequency: z.boolean().default(true),
    learnFromOutcomes: z.boolean().default(true),
    learnFromRatings: z.boolean().default(true),
    suggestNewRolesAutomatically: z.boolean().default(true),
    neverExpandPermissionsWithoutApproval: z.literal(true),
    userCanDisableRoleLearning: z.boolean().default(true),
  }).strict(),
}).strict();

export function suggestRoleFromPatterns(patterns: z.infer<typeof observedTaskPatternSchema>[]) {
  const frequent = patterns.filter((pattern) => pattern.frequency30d >= 5);
  return frequent.map((pattern) => ({
    normalizedIntent: pattern.normalizedIntent,
    frequency30d: pattern.frequency30d,
    candidateForRoleEvolution: true,
  }));
}
