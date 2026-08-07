import { z } from "zod";

export const COMPANY_BUDDY_DATA_CLASSES = [
  "public",
  "internal",
  "confidential",
  "restricted",
] as const;

export const companyBuddyRoleSchema = z.object({
  id: z.string().trim().regex(/^[a-z][a-z0-9_-]{1,80}$/),
  name: z.string().trim().min(2).max(120),
  description: z.string().trim().min(5).max(500),
  allowedWorkflows: z.array(z.string().trim().min(2).max(160)).max(200).default([]),
  allowedConnectors: z.array(z.string().trim().min(2).max(160)).max(100).default([]),
  maximumAutonomy: z.enum(["plan_only", "read_only", "sandbox_execute", "approved_external_action", "scheduled_read_only"]),
  requiresHumanReviewFor: z.array(z.string().trim().min(2).max(160)).max(100).default([]),
}).strict();

export const companyKnowledgeSourceSchema = z.object({
  id: z.string().trim().regex(/^[A-Za-z0-9_.:/-]{2,160}$/),
  name: z.string().trim().min(2).max(160),
  type: z.enum(["sop", "policy", "manual", "knowledge_base", "ticket_history", "crm", "repository", "document_set", "database", "api", "training_material"]),
  dataClass: z.enum(COMPANY_BUDDY_DATA_CLASSES),
  sourceReference: z.string().trim().min(2).max(512),
  readOnlyByDefault: z.boolean().default(true),
  retentionDays: z.number().int().min(1).max(3650).default(365),
}).strict();

export const companyBuddyWorkflowSchema = z.object({
  id: z.string().trim().regex(/^[a-z][a-z0-9_-]{1,120}$/),
  name: z.string().trim().min(2).max(160),
  objective: z.string().trim().min(10).max(1000),
  ownerRoleIds: z.array(z.string().trim().min(2).max(80)).min(1).max(50),
  steps: z.array(z.object({
    id: z.string().trim().min(2).max(100),
    action: z.string().trim().min(3).max(500),
    connectorId: z.string().trim().max(160).nullable().default(null),
    sideEffect: z.boolean().default(false),
    freshApprovalRequired: z.boolean().default(false),
    evidenceRequired: z.boolean().default(true),
  }).strict()).min(1).max(200),
  trigger: z.enum(["manual", "schedule", "event", "api", "inbox", "queue"]).default("manual"),
  runMode: z.enum(["sandbox", "production"]).default("sandbox"),
  maximumSpendUsd: z.number().finite().min(0).max(10_000_000).default(0),
  benchmarkSuiteIds: z.array(z.string().trim().min(2).max(160)).max(100).default([]),
}).strict();

export const companyBuddyTenantSchema = z.object({
  schema: z.literal("dreamco.company_buddy.v1"),
  tenantId: z.string().trim().regex(/^[A-Za-z0-9_.:-]{3,120}$/),
  companyName: z.string().trim().min(2).max(200),
  buddyName: z.string().trim().min(2).max(120).default("Buddy"),
  roles: z.array(companyBuddyRoleSchema).min(1).max(500),
  knowledgeSources: z.array(companyKnowledgeSourceSchema).max(1000).default([]),
  workflows: z.array(companyBuddyWorkflowSchema).max(1000).default([]),
  policies: z.object({
    leastPrivilege: z.literal(true),
    externalWritesDisabledByDefault: z.boolean().default(true),
    freshApprovalForHighImpactActions: z.boolean().default(true),
    auditReceiptsRequired: z.boolean().default(true),
    secretsByReferenceOnly: z.boolean().default(true),
    productionPromotionRequiresBenchmarks: z.boolean().default(true),
    userCanPauseAllAutomations: z.boolean().default(true),
  }).strict(),
  training: z.object({
    sourceTypesAllowed: z.array(z.enum(["sop", "policy", "manual", "knowledge_base", "ticket_history", "crm", "repository", "document_set", "database", "api", "training_material"])).min(1),
    privateTrainingOptInRequired: z.boolean().default(true),
    syntheticEvaluationRequiredBeforeProduction: z.boolean().default(true),
    humanFeedbackSupported: z.boolean().default(true),
    rollbackSupported: z.boolean().default(true),
  }).strict(),
}).strict();

export type CompanyBuddyTenant = z.infer<typeof companyBuddyTenantSchema>;

export function companyBuddyProductionReadiness(tenant: CompanyBuddyTenant) {
  const productionWorkflows = tenant.workflows.filter((workflow) => workflow.runMode === "production");
  const unsafe = productionWorkflows.filter((workflow) => workflow.steps.some((step) => step.sideEffect && !step.freshApprovalRequired));
  return {
    tenantId: tenant.tenantId,
    workflowCount: tenant.workflows.length,
    productionWorkflowCount: productionWorkflows.length,
    unsafeProductionWorkflowCount: unsafe.length,
    ready: unsafe.length === 0,
  } as const;
}
