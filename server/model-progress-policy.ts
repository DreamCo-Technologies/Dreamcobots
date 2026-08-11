import { readFileSync } from "node:fs";
import { resolve } from "node:path";

import { z } from "zod";

import { MODEL_DISCOVERY_TASKS } from "@shared/model-benchmark-targets";

type ProgressCatalog = {
  schema: string;
  summary: Record<string, number>;
  taskCategories: string[];
  councils: Array<{
    id: string;
    task: string;
    mode: "free" | "premium";
    status: string;
    selectionBasis: string;
    liveBenchmarkContribution: number;
    paidApprovalRequired: boolean;
    members: Array<Record<string, unknown> & { targetId: number; tier: string }>;
  }>;
  benchmarkRoadmaps: Array<Record<string, unknown> & { id: string }>;
  bootcampTracks: Array<Record<string, unknown> & { id: string; task: string }>;
  datasetPackages: Array<Record<string, unknown>>;
  truthContract: Record<string, boolean>;
};

const taskCategorySchema = z.string().trim().refine(
  (value) => MODEL_DISCOVERY_TASKS.includes(value as (typeof MODEL_DISCOVERY_TASKS)[number]),
  "Unknown model task category",
);

export const modelCouncilRequestSchema = z.object({
  taskCategory: taskCategorySchema,
  mode: z.enum(["free", "premium"]).default("free"),
  approvePaidModelsForThisRequest: z.boolean().default(false),
}).strict();

export const modelImprovementPlanRequestSchema = z.object({
  taskCategory: taskCategorySchema,
  targetId: z.number().int().min(1).max(500).optional(),
  mode: z.enum(["free", "premium"]).default("free"),
  maxBudgetUsd: z.number().min(0).max(100_000).default(0),
  approvePaidModelsForThisRun: z.boolean().default(false),
  allowExternalNetwork: z.boolean().default(false),
  allowWeightTraining: z.boolean().default(false),
}).strict();

let catalogCache: ProgressCatalog | undefined;

export function getModelProgressCenter(
  path = resolve(process.cwd(), "config", "generated", "buddy_model_progress_center.json"),
) {
  catalogCache ??= JSON.parse(readFileSync(path, "utf8")) as ProgressCatalog;
  return catalogCache;
}

export function selectModelCouncil(input: z.input<typeof modelCouncilRequestSchema>) {
  const request = modelCouncilRequestSchema.parse(input);
  const catalog = getModelProgressCenter();
  const council = catalog.councils.find((item) => item.task === request.taskCategory && item.mode === request.mode);
  if (!council) throw new Error(`No ${request.mode} council exists for ${request.taskCategory}`);
  const paidApprovalRequired = request.mode === "premium" && !request.approvePaidModelsForThisRequest;
  return {
    schema: "dreamco.buddy_model_council_selection.v1",
    ...council,
    memberCount: council.members.length,
    status: paidApprovalRequired ? "paid_approval_required" : council.status,
    paidApprovalRecordedForThisRequest: request.mode === "premium" && request.approvePaidModelsForThisRequest,
    providerCallsExecuted: 0,
    liveQualityClaimed: false,
    nextStep: paidApprovalRequired
      ? "Approve premium models for this request or use the free council."
      : "Run identical signed fixtures before promoting any member as the measured best for this task.",
  } as const;
}

export function createModelImprovementPlan(input: z.input<typeof modelImprovementPlanRequestSchema>) {
  const request = modelImprovementPlanRequestSchema.parse(input);
  const catalog = getModelProgressCenter();
  const council = catalog.councils.find((item) => item.task === request.taskCategory && item.mode === request.mode);
  const track = catalog.bootcampTracks.find((item) => item.task === request.taskCategory);
  if (!council || !track) throw new Error(`Missing council or Bootcamp track for ${request.taskCategory}`);
  const member = request.targetId === undefined
    ? council.members[0]
    : council.members.find((item) => item.targetId === request.targetId);
  if (!member) throw new Error("The requested target is not a member of this task council.");
  const paidBlocked = request.mode === "premium"
    && (!request.approvePaidModelsForThisRun || request.maxBudgetUsd <= 0);
  const networkBlocked = request.allowExternalNetwork;
  const weightTrainingBlocked = request.allowWeightTraining;
  const status = paidBlocked
    ? "paid_budget_approval_required"
    : networkBlocked
      ? "authenticated_adapter_and_network_approval_required"
      : weightTrainingBlocked
        ? "rights_compute_and_training_approval_required"
        : "local_bootcamp_plan_ready";
  return {
    schema: "dreamco.buddy_model_improvement_plan.v1",
    status,
    taskCategory: request.taskCategory,
    mode: request.mode,
    selectedMember: member,
    councilId: council.id,
    bootcampTrack: track,
    benchmarkRoadmaps: catalog.benchmarkRoadmaps,
    maxBudgetUsd: request.maxBudgetUsd,
    paidApprovalRecordedForThisRun: request.approvePaidModelsForThisRun,
    externalNetworkApprovedForThisRun: false,
    weightTrainingApproved: false,
    trainingExecuted: false,
    modelReleased: false,
    providerCallsExecuted: 0,
    controls: {
      syntheticOrRightsClearedFixturesOnly: true,
      baselineBeforeChanges: true,
      identicalHeldOutRetest: true,
      checkpointAndRollback: true,
      stopOnRegression: true,
      stopOnBudgetLimit: true,
      humanReviewBeforePromotion: true,
      productionSelfModification: false,
    },
    nextStep: status === "local_bootcamp_plan_ready"
      ? "Generate rights-safe fixtures, capture the baseline, and run the first isolated local drill."
      : "Resolve the displayed approval, adapter, data-rights, or budget gate before execution.",
  } as const;
}
