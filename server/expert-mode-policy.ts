import { z } from "zod";

import expertMode from "../config/generated/buddy_expert_mode.json";

type ResourceRecord = {
  id: string;
  host: string;
  primary_url: string;
  url_count: number;
  source_lists: string[];
  connection_status: string;
};

type ExpertDay = {
  day: number;
  id: string;
  label: string;
  outcome: string;
  resource_count: number;
  resource_ids: string[];
  protocol: string[];
  evidence_required: string[];
};

type InventionResource = { id: string; name: string; kind: string; url: string; cost: string; connection_status: string };
type InventionStage = { id: string; label: string; outputs: string[]; resource_ids: string[] };
type ExpertModeCatalog = {
  schema: string;
  identity: string;
  mission: string;
  summary: Record<string, number>;
  days: ExpertDay[];
  daily_protocol: string[];
  evidence_gates: Record<string, number | boolean>;
  resource_index: ResourceRecord[];
  connections: { methods: string[]; auth_methods: unknown[]; connector_contracts: unknown[]; platform_profiles: unknown[]; secret_rule: string };
  learning_sources: { schema: string; mission: string; sources: Array<{ id: string; label: string; category: string; readiness: string; ingestion: string; permission: string; learning_output: string }>; truth_rule: string };
  invention_navigator: {
    identity: string;
    mission: string;
    jurisdiction_rule: string;
    confidentiality_warning: string;
    stages: InventionStage[];
    resources: InventionResource[];
    approval_gates: string[];
    autonomous_allowed: string[];
    truth: Record<string, boolean | number>;
  };
  connection_rule: string;
  mastery_rule: string;
  autonomy_rule: string;
  truth: Record<string, boolean | number>;
};

export const BUDDY_EXPERT_MODE = expertMode as ExpertModeCatalog;

const sha256Schema = z.string().regex(/^[a-f0-9]{64}$/i);
const scoreRuns = z.array(z.number().min(0).max(1)).min(3).max(10);

export const expertSprintRequestSchema = z.object({
  sprintId: z.string().trim().regex(/^[a-z0-9][a-z0-9._-]{2,79}$/),
  goal: z.string().trim().min(10).max(1_000),
  hoursPerDay: z.number().min(0.5).max(16),
  learningStyle: z.enum(["balanced", "hands_on", "teach_back", "benchmark_first", "accessibility_first"]).default("balanced"),
  includedDays: z.array(z.number().int().min(1).max(7)).min(1).max(7).default([1, 2, 3, 4, 5, 6, 7]),
  resourceIds: z.array(z.string().trim().min(3).max(240)).max(1_000).default([]),
  focusKeywords: z.array(z.string().trim().min(2).max(80)).max(20).default([]),
  connectionMethods: z.array(z.string().trim().min(3).max(80)).max(9).default(["custom_rest", "mcp_transport"]),
  externalRetrievalAuthorized: z.boolean().default(false),
  privateWorkspaceConfirmed: z.boolean().default(false),
}).strict().superRefine((value, context) => {
  if (new Set(value.includedDays).size !== value.includedDays.length) context.addIssue({ code: z.ZodIssueCode.custom, message: "Included days must be unique." });
  if (new Set(value.resourceIds).size !== value.resourceIds.length) context.addIssue({ code: z.ZodIssueCode.custom, message: "Resource ids must be unique." });
  if (new Set(value.connectionMethods).size !== value.connectionMethods.length) context.addIssue({ code: z.ZodIssueCode.custom, message: "Connection methods must be unique." });
});

export const expertSprintEvidenceSchema = z.object({
  sprintId: z.string().trim().regex(/^[a-z0-9][a-z0-9._-]{2,79}$/),
  sprintManifestSha256: sha256Schema,
  hiddenHoldoutManifestSha256: sha256Schema,
  dayEvidence: z.array(z.object({
    day: z.number().int().min(1).max(7),
    completedResourceIds: z.array(z.string().trim().min(3).max(240)).max(1_000),
    routingScores: scoreRuns,
    sourceVerificationScores: scoreRuns,
    applicationScores: scoreRuns,
    teachBackScores: scoreRuns,
    hiddenHoldoutScores: scoreRuns,
    evidenceArtifactSha256: sha256Schema,
  }).strict()).length(7),
  ownerReviewed: z.boolean().default(false),
}).strict().superRefine((value, context) => {
  if (new Set(value.dayEvidence.map((item) => item.day)).size !== 7) context.addIssue({ code: z.ZodIssueCode.custom, message: "Evidence must contain each day exactly once." });
  if (value.sprintManifestSha256.toLowerCase() === value.hiddenHoldoutManifestSha256.toLowerCase()) context.addIssue({ code: z.ZodIssueCode.custom, message: "Sprint and hidden-holdout manifests must differ." });
  value.dayEvidence.forEach((item, index) => {
    if (new Set(item.completedResourceIds).size !== item.completedResourceIds.length) context.addIssue({ code: z.ZodIssueCode.custom, path: ["dayEvidence", index, "completedResourceIds"], message: "Completed resource ids must be unique within each day." });
  });
  if (new Set(value.dayEvidence.map((item) => item.evidenceArtifactSha256.toLowerCase())).size !== 7) context.addIssue({ code: z.ZodIssueCode.custom, message: "Each day requires a distinct evidence artifact." });
});

export const inventionProjectRequestSchema = z.object({
  projectId: z.string().trim().regex(/^[a-z0-9][a-z0-9._-]{2,79}$/),
  title: z.string().trim().min(3).max(160),
  ideaSummary: z.string().trim().min(20).max(4_000),
  targetUser: z.string().trim().min(3).max(500),
  country: z.string().trim().min(2).max(120),
  prototypeType: z.enum(["software", "electronics", "mechanical", "consumer_product", "medical_device", "child_product", "food_or_cosmetic", "mixed"]),
  budgetUsd: z.number().min(0).max(100_000_000),
  confidentiality: z.enum(["private", "professional_confidential_review", "public_summary_only"]),
  ownerApprovesPublicResearch: z.boolean().default(false),
}).strict();

export type ExpertSprintRequest = z.infer<typeof expertSprintRequestSchema>;
export type ExpertSprintEvidence = z.infer<typeof expertSprintEvidenceSchema>;
export type InventionProjectRequest = z.infer<typeof inventionProjectRequestSchema>;

const average = (values: number[]) => values.reduce((sum, value) => sum + value, 0) / values.length;

export function createBuddyExpertSprint(input: ExpertSprintRequest) {
  const request = expertSprintRequestSchema.parse(input);
  const resourceMap = new Map(BUDDY_EXPERT_MODE.resource_index.map((item) => [item.id, item]));
  const unknownResources = request.resourceIds.filter((id) => !resourceMap.has(id));
  if (unknownResources.length) throw new Error(`Unknown Expert Mode resources: ${unknownResources.join(", ")}`);
  const unknownMethods = request.connectionMethods.filter((method) => !BUDDY_EXPERT_MODE.connections.methods.includes(method));
  if (unknownMethods.length) throw new Error(`Unsupported connection methods: ${unknownMethods.join(", ")}`);
  const explicitlySelected = request.resourceIds.length ? new Set(request.resourceIds) : null;
  const keywords = request.focusKeywords.map((item) => item.toLowerCase());
  const selectedDays = BUDDY_EXPERT_MODE.days.filter((item) => request.includedDays.includes(item.day)).map((day) => {
    const resources = day.resource_ids.map((id) => resourceMap.get(id)!).filter((resource) => {
      if (explicitlySelected && !explicitlySelected.has(resource.id)) return false;
      if (!keywords.length) return true;
      const text = `${resource.host} ${resource.source_lists.join(" ")}`.toLowerCase();
      return keywords.some((keyword) => text.includes(keyword));
    });
    const minutesAvailable = request.hoursPerDay * 60;
    return {
      day: day.day,
      id: day.id,
      label: day.label,
      outcome: day.outcome,
      resourceCount: resources.length,
      resourceIds: resources.map((item) => item.id),
      minutesAvailable,
      minutesPerResource: resources.length ? minutesAvailable / resources.length : 0,
      protocol: day.protocol,
      evidenceRequired: day.evidence_required,
      status: "scheduled_not_executed",
    };
  });
  const resourceCount = selectedDays.reduce((sum, day) => sum + day.resourceCount, 0);
  const thinnestMinutes = Math.min(...selectedDays.filter((day) => day.resourceCount).map((day) => day.minutesPerResource), Number.POSITIVE_INFINITY);
  return {
    schema: "dreamco.buddy_expert_sprint.v1",
    sprintId: request.sprintId,
    goal: request.goal,
    learningStyle: request.learningStyle,
    status: !request.privateWorkspaceConfirmed ? "private_workspace_confirmation_required" : !request.externalRetrievalAuthorized ? "external_retrieval_approval_required" : "retrieval_adapter_and_daily_execution_required",
    days: selectedDays,
    dayCount: selectedDays.length,
    resourceCount,
    includesEveryRepositoryResource: !explicitlySelected && !keywords.length && request.includedDays.length === 7,
    connectionMethods: request.connectionMethods,
    feasibility: thinnestMinutes < 5 ? "routing_and_indexing_sprint_not_content_mastery" : "bounded_study_sprint_mastery_still_requires_evidence",
    learningStarted: false,
    externalRequestsStarted: false,
    masteryClaimed: false,
    productionPromotionPerformed: false,
  } as const;
}

export function evaluateBuddyExpertSprint(input: ExpertSprintEvidence) {
  const request = expertSprintEvidenceSchema.parse(input);
  const known = new Set(BUDDY_EXPERT_MODE.resource_index.map((item) => item.id));
  const expectedByDay = new Map(BUDDY_EXPERT_MODE.days.map((item) => [item.day, new Set(item.resource_ids)]));
  const completed = new Set(request.dayEvidence.flatMap((item) => item.completedResourceIds));
  const unknown = [...completed].filter((id) => !known.has(id));
  if (unknown.length) throw new Error(`Unknown completed resources: ${unknown.join(", ")}`);
  const gates = BUDDY_EXPERT_MODE.evidence_gates;
  const days = [...request.dayEvidence].sort((left, right) => left.day - right.day).map((day) => {
    const completedForDay = new Set(day.completedResourceIds);
    const expectedForDay = expectedByDay.get(day.day) ?? new Set<string>();
    const scores = {
      routing: average(day.routingScores),
      sourceVerification: average(day.sourceVerificationScores),
      application: average(day.applicationScores),
      teachBack: average(day.teachBackScores),
      hiddenHoldout: average(day.hiddenHoldoutScores),
    };
    const passed = scores.routing >= Number(gates.minimum_daily_routing_score)
      && scores.sourceVerification >= Number(gates.minimum_daily_source_verification_score)
      && scores.application >= Number(gates.minimum_daily_application_score)
      && scores.teachBack >= Number(gates.minimum_daily_teach_back_score)
      && scores.hiddenHoldout >= Number(gates.minimum_daily_benchmark_score);
    const resourcesAssignedToCorrectDay = completedForDay.size === expectedForDay.size
      && [...completedForDay].every((resourceId) => expectedForDay.has(resourceId));
    return { day: day.day, completedResources: completedForDay.size, expectedResources: expectedForDay.size, resourcesAssignedToCorrectDay, scores, passed, evidenceArtifactSha256: day.evidenceArtifactSha256 };
  });
  const coverage = completed.size / known.size;
  const evidenceGates = {
    seven_days_present: days.length === 7,
    every_day_passed: days.every((day) => day.passed),
    every_repository_resource_covered: completed.size === known.size,
    resources_assigned_to_correct_days: days.every((day) => day.resourcesAssignedToCorrectDay),
    repeat_runs_present: request.dayEvidence.every((day) => [day.routingScores, day.sourceVerificationScores, day.applicationScores, day.teachBackScores, day.hiddenHoldoutScores].every((scores) => scores.length >= 3)),
    separate_hidden_holdout: request.sprintManifestSha256.toLowerCase() !== request.hiddenHoldoutManifestSha256.toLowerCase(),
  };
  const routingProven = Object.values(evidenceGates).every(Boolean);
  return {
    schema: "dreamco.buddy_expert_sprint_evidence.v1",
    sprintId: request.sprintId,
    status: routingProven ? (request.ownerReviewed ? "bounded_routing_competency_owner_reviewed" : "bounded_routing_competency_owner_review_required") : "expert_sprint_evidence_failed",
    resourceCoverage: { completed: completed.size, total: known.size, ratio: coverage },
    days,
    gates: evidenceGates,
    boundedResourceRoutingProven: routingProven,
    universalMasteryClaimed: false,
    liveConnectionsClaimed: false,
    modelWeightsModified: false,
  } as const;
}

export function createBuddyInventionProject(input: InventionProjectRequest) {
  const request = inventionProjectRequestSchema.parse(input);
  const navigator = BUDDY_EXPERT_MODE.invention_navigator;
  const resourceMap = new Map(navigator.resources.map((item) => [item.id, item]));
  const regulatorIds = new Set<string>();
  if (["electronics", "mixed"].includes(request.prototypeType)) regulatorIds.add("fcc-equipment-authorization");
  if (["consumer_product", "child_product", "electronics", "mixed"].includes(request.prototypeType)) regulatorIds.add("cpsc-business-guidance");
  if (request.prototypeType === "medical_device") regulatorIds.add("fda-device-advice");
  const stages = navigator.stages.map((stage) => ({
    id: stage.id,
    label: stage.label,
    status: "not_started",
    requiredOutputs: stage.outputs,
    resources: stage.resource_ids.map((id) => resourceMap.get(id)!),
    ownerApprovalRequiredBeforeExternalAction: true,
  }));
  return {
    schema: "dreamco.buddy_invention_project.v1",
    projectId: request.projectId,
    title: request.title,
    ideaSummary: request.ideaSummary,
    targetUser: request.targetUser,
    jurisdiction: request.country,
    prototypeType: request.prototypeType,
    budgetUsd: request.budgetUsd,
    confidentiality: request.confidentiality,
    status: request.confidentiality === "private" && request.ownerApprovesPublicResearch ? "confidentiality_conflict_owner_review_required" : "private_project_plan_ready",
    disclosureRule: navigator.confidentiality_warning,
    jurisdictionRule: navigator.jurisdiction_rule,
    productSpecificRegulatorResources: [...regulatorIds].map((id) => resourceMap.get(id)),
    stages,
    approvalGates: navigator.approval_gates,
    autonomousAllowed: navigator.autonomous_allowed,
    externalResearchStarted: false,
    filingsSubmitted: false,
    peopleContacted: false,
    purchasesMade: false,
    legalAdviceProvided: false,
    storeLaunchPerformed: false,
  } as const;
}
