import { z } from "zod";

export const CAPABILITY_EVIDENCE_STATES = [
  "declared",
  "official_verified",
  "adapter_verified",
  "sandbox_tested",
  "live_tested",
  "production_certified",
  "deprecated",
  "blocked",
] as const;

export const BOT_AUTONOMY_CEILINGS = [
  "plan_only",
  "read_only",
  "sandbox_execute",
  "approved_external_action",
  "scheduled_read_only",
] as const;

export const BOT_OPERATION_MODES_V2 = ["offline", "sandbox", "live"] as const;

export const capabilityEvidenceSchema = z.object({
  capabilityId: z.string().trim().min(2).max(160),
  state: z.enum(CAPABILITY_EVIDENCE_STATES),
  evidenceReferences: z.array(z.string().trim().min(2).max(512)).max(50).default([]),
  exactVersion: z.string().trim().max(160).nullable().default(null),
  verifiedAt: z.string().datetime().nullable().default(null),
  expiresAt: z.string().datetime().nullable().default(null),
  benchmarkSuiteIds: z.array(z.string().trim().min(2).max(160)).max(50).default([]),
  notes: z.string().trim().max(2_000).default(""),
}).strict();

export const botPermissionSchema = z.object({
  action: z.string().trim().min(2).max(120),
  scope: z.string().trim().min(2).max(240),
  defaultAllowed: z.boolean().default(false),
  freshApprovalRequired: z.boolean().default(true),
  maximumSpendUsd: z.number().finite().min(0).max(10_000_000).nullable().default(null),
}).strict();

export const botDependencySchema = z.object({
  id: z.string().trim().min(2).max(160),
  kind: z.enum(["bot", "tool", "connector", "model", "database", "service", "policy", "human_review"]),
  required: z.boolean().default(true),
  readiness: z.enum(["ready", "configuration_required", "verification_required", "optional", "blocked"]),
}).strict();

export const botContractV2Schema = z.object({
  schema: z.literal("dreamco.bot_contract.v2"),
  version: z.string().trim().regex(/^\d+\.\d+\.\d+$/),
  identity: z.object({
    slug: z.string().trim().regex(/^[a-z0-9][a-z0-9-]{1,119}$/),
    displayName: z.string().trim().min(2).max(160),
    division: z.string().trim().min(2).max(120),
    category: z.string().trim().min(2).max(120),
    tier: z.enum(["free", "pro", "enterprise", "elite"]),
  }).strict(),
  mission: z.string().trim().min(10).max(2_000),
  userJobs: z.array(z.string().trim().min(3).max(500)).min(1).max(100),
  declaredCapabilities: z.array(z.string().trim().min(2).max(160)).min(1).max(200),
  capabilityEvidence: z.array(capabilityEvidenceSchema).max(200).default([]),
  tools: z.array(z.string().trim().min(2).max(160)).max(100).default([]),
  connectors: z.array(z.string().trim().min(2).max(160)).max(100).default([]),
  modelRequirements: z.array(z.string().trim().min(2).max(160)).max(100).default([]),
  dataCategories: z.array(z.string().trim().min(2).max(120)).max(100).default([]),
  permissions: z.array(botPermissionSchema).max(100).default([]),
  autonomyCeiling: z.enum(BOT_AUTONOMY_CEILINGS).default("plan_only"),
  operationalModes: z.array(z.enum(BOT_OPERATION_MODES_V2)).min(1).max(3),
  budgetPolicy: z.object({
    automaticSpendAllowed: z.literal(false),
    perRunMaximumUsd: z.number().finite().min(0).max(10_000_000).default(0),
    ownerMayApproveHigherPerRun: z.boolean().default(true),
  }).strict(),
  sideEffectPolicy: z.object({
    previewBeforeWrite: z.boolean().default(true),
    freshApprovalForHighImpactActions: z.boolean().default(true),
    externalWritesDisabledByDefault: z.boolean().default(true),
    auditReceiptRequired: z.boolean().default(true),
  }).strict(),
  benchmarkSuiteIds: z.array(z.string().trim().min(2).max(160)).min(1).max(100),
  runtimeBinding: z.object({
    kind: z.enum(["shared_worker", "dedicated_worker", "planner_only", "connector_backed", "human_review_backed"]),
    implementationReference: z.string().trim().min(2).max(512),
    healthCheckReference: z.string().trim().max(512).nullable().default(null),
  }).strict(),
  memoryPolicy: z.object({
    allowedCategories: z.array(z.string().trim().min(2).max(120)).max(50).default([]),
    sensitiveMemoryDefaultOff: z.boolean().default(true),
    defaultRetentionDays: z.number().int().min(1).max(365).default(30),
    userDeleteSupported: z.boolean().default(true),
  }).strict(),
  dependencies: z.array(botDependencySchema).max(200).default([]),
  failureModes: z.array(z.string().trim().min(3).max(500)).max(100).default([]),
  recoveryBehavior: z.array(z.string().trim().min(3).max(500)).max(100).default([]),
  professionalReview: z.object({
    required: z.boolean().default(false),
    domains: z.array(z.string().trim().min(2).max(100)).max(25).default([]),
  }).strict(),
  commercial: z.object({
    revenueModel: z.string().trim().max(240).default(""),
    targetUsers: z.string().trim().max(500).default(""),
    priceRange: z.string().trim().max(120).default(""),
  }).strict(),
  status: z.enum(["planned", "cataloged", "runtime_ready", "sandbox_certified", "production_certified", "deprecated", "blocked"]),
  lastVerifiedAt: z.string().datetime().nullable().default(null),
}).strict();

export type BotContractV2 = z.infer<typeof botContractV2Schema>;

export function certifiedCapabilities(bot: BotContractV2) {
  const certified = new Set(
    bot.capabilityEvidence
      .filter((item) => ["sandbox_tested", "live_tested", "production_certified"].includes(item.state))
      .map((item) => item.capabilityId),
  );
  return bot.declaredCapabilities.filter((capability) => certified.has(capability));
}

export function botReadinessSummary(bot: BotContractV2) {
  const evidenceCounts = Object.fromEntries(CAPABILITY_EVIDENCE_STATES.map((state) => [state, 0])) as Record<string, number>;
  for (const evidence of bot.capabilityEvidence) evidenceCounts[evidence.state] += 1;
  const requiredDependencies = bot.dependencies.filter((item) => item.required);
  const blockedDependencies = requiredDependencies.filter((item) => item.readiness === "blocked");
  const unresolvedDependencies = requiredDependencies.filter((item) => !["ready", "optional"].includes(item.readiness));
  return {
    slug: bot.identity.slug,
    status: bot.status,
    declaredCapabilityCount: bot.declaredCapabilities.length,
    certifiedCapabilityCount: certifiedCapabilities(bot).length,
    evidenceCounts,
    requiredDependencyCount: requiredDependencies.length,
    blockedDependencyCount: blockedDependencies.length,
    unresolvedDependencyCount: unresolvedDependencies.length,
    productionReady:
      bot.status === "production_certified"
      && blockedDependencies.length === 0
      && unresolvedDependencies.length === 0
      && certifiedCapabilities(bot).length === bot.declaredCapabilities.length,
  } as const;
}
